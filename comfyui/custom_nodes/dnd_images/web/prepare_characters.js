import { app } from "/scripts/app.js";

const NODE_NAME = "DNDPrepareCharacters";

const INITIAL_CHARACTERS = 2;
const MAX_CHARACTERS = 10;


/**
 * Return the fixed library selector widgets.
 *
 * These are NOT CHARACTER inputs.
 *
 * The node has exactly one CHARACTER input:
 *
 *     characters
 *
 * Everything else here is a persistent library selector.
 */
function getLibraryWidgets(node) {

    return (node.widgets || [])
        .filter(widget =>
            /^library_character_\d+$/.test(
                widget.name
            )
        )
        .sort((a, b) => {

            const aIndex = Number(
                a.name.split("_").pop()
            );

            const bIndex = Number(
                b.name.split("_").pop()
            );

            return aIndex - bIndex;
        });
}


/**
 * Return the currently visible library selectors.
 */
function getVisibleLibraryWidgets(node) {

    return getLibraryWidgets(node)
        .filter(widget =>
            !widget.hidden
        );
}


/**
 * Update library selector visibility.
 *
 * IMPORTANT:
 *
 * We never create or remove CHARACTER inputs here.
 *
 * The Python node has exactly one:
 *
 *     characters
 *
 * The ten library selectors already exist in the schema.
 */
function updateLibraryVisibility(node) {

    const widgets =
        getLibraryWidgets(node);

    widgets.forEach(
        (widget, index) => {

            widget.hidden =
                index >= INITIAL_CHARACTERS;
        }
    );

    updateNodeSize(node);
    updateButtonState(node);

    node.setDirtyCanvas(
        true,
        true
    );
}


/**
 * Resize the node based only on visible library selectors.
 */
function updateNodeSize(node) {

    const visibleWidgets =
        getVisibleLibraryWidgets(node);

    const width = Math.max(
        node.size?.[0] || 300,
        300
    );

    const rowHeight = 30;
    const buttonHeight = 32;

    /*
     * Leave enough room for:
     *
     * - node title
     * - CHARACTER input
     * - library rows
     * - buttons
     */
    const padding = 90;

    const height =
        padding +
        (
            visibleWidgets.length *
            rowHeight
        ) +
        (
            buttonHeight *
            2
        );

    node.setSize([
        width,
        height,
    ]);
}


/**
 * Show the next library selector.
 */
function addCharacterWidget(node) {

    const widgets =
        getLibraryWidgets(node);

    const visibleWidgets =
        getVisibleLibraryWidgets(node);

    if (
        visibleWidgets.length >=
        MAX_CHARACTERS
    ) {
        return;
    }

    const nextWidget =
        widgets[
            visibleWidgets.length
        ];

    if (!nextWidget) {
        return;
    }

    nextWidget.hidden = false;

    updateNodeSize(node);
    updateButtonState(node);

    node.setDirtyCanvas(
        true,
        true
    );
}


/**
 * Hide the last visible library selector.
 *
 * The widget remains part of the Python schema.
 * We only hide it and clear its value.
 */
function removeCharacterWidget(node) {

    const visibleWidgets =
        getVisibleLibraryWidgets(node);

    if (
        visibleWidgets.length <=
        INITIAL_CHARACTERS
    ) {
        return;
    }

    const lastWidget =
        visibleWidgets[
            visibleWidgets.length - 1
        ];

    /*
     * Clear the selection so a hidden row cannot
     * accidentally remain active.
     */
    lastWidget.value = "";

    lastWidget.hidden = true;

    updateNodeSize(node);
    updateButtonState(node);

    node.setDirtyCanvas(
        true,
        true
    );
}


/**
 * Enable/disable the Add and Remove buttons.
 */
function updateButtonState(node) {

    const visibleCount =
        getVisibleLibraryWidgets(node)
            .length;

    const addButton =
        node.widgets?.find(
            widget =>
                widget.name ===
                "add_character"
        );

    const removeButton =
        node.widgets?.find(
            widget =>
                widget.name ===
                "remove_character"
        );

    if (addButton) {

        addButton.disabled =
            visibleCount >=
            MAX_CHARACTERS;
    }

    if (removeButton) {

        removeButton.disabled =
            visibleCount <=
            INITIAL_CHARACTERS;
    }
}


/**
 * Initialize the node.
 */
app.registerExtension({

    name:
        "dnd_images.prepare_characters",

    async nodeCreated(node) {

        if (
            node.comfyClass !==
            NODE_NAME
        ) {
            return;
        }

        /*
         * Prevent duplicate initialization.
         */
        if (
            node._dndPrepareCharactersInitialized
        ) {
            return;
        }

        node._dndPrepareCharactersInitialized =
            true;


        // ================================================================
        // IMPORTANT
        //
        // NO CHARACTER INPUTS ARE CREATED HERE.
        //
        // There must never be:
        //
        //     character_0
        //     character_1
        //     character_2
        //
        // The Python node contains exactly:
        //
        //     characters
        //
        // ================================================================


        // ================================================================
        // Library selectors
        // ================================================================

        updateLibraryVisibility(node);


        // ================================================================
        // Add button
        // ================================================================

        const addButton =
            node.addWidget(
                "button",
                "add_character",
                "+ Add Character",
                () => {

                    addCharacterWidget(
                        node
                    );
                }
            );

        /*
         * This is a UI control, not workflow data.
         */
        addButton.serialize =
            false;


        // ================================================================
        // Remove button
        // ================================================================

        const removeButton =
            node.addWidget(
                "button",
                "remove_character",
                "− Remove Character",
                () => {

                    removeCharacterWidget(
                        node
                    );
                }
            );

        /*
         * This is a UI control, not workflow data.
         */
        removeButton.serialize =
            false;


        // ================================================================
        // Connection handling
        // ================================================================

        const originalOnConnectionsChange =
            node.onConnectionsChange;

        node.onConnectionsChange =
            function (
                type,
                slotIndex,
                connected,
                linkInfo,
                output
            ) {

                originalOnConnectionsChange?.apply(
                    this,
                    arguments
                );

                /*
                 * Connections affect node layout,
                 * but never create additional inputs.
                 */
                updateNodeSize(this);
                updateButtonState(this);

                this.setDirtyCanvas(
                    true,
                    true
                );
            };


        // ================================================================
        // Initial layout
        // ================================================================

        updateNodeSize(node);
        updateButtonState(node);

        node.setDirtyCanvas(
            true,
            true
        );
    },
});