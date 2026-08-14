import json
import inspect
import re
from pathlib import Path

import folder_paths


# ============================================================================
# Character Library Configuration
# ============================================================================

CHARACTERS_DIR = "characters"

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


# These are the same preferred resolutions used by
# ComfyUI's FluxKontextImageScale node.
PREFERRED_KONTEXT_RESOLUTIONS = [
    (672, 1568),
    (688, 1504),
    (720, 1456),
    (752, 1392),
    (800, 1328),
    (832, 1248),
    (880, 1184),
    (944, 1104),
    (1024, 1024),
    (1104, 944),
    (1184, 880),
    (1248, 832),
    (1328, 800),
    (1392, 752),
    (1456, 720),
    (1504, 688),
    (1568, 672),
]


# ============================================================================
# Character Library
# ============================================================================

def characters_root():
    """
    Persistent character directory.

    With the Docker setup used by this project, this resolves to:

        ai_data/comfyui/input/characters/
    """
    return Path(folder_paths.get_input_directory()) / CHARACTERS_DIR


def safe_id(name):
    """
    Convert a character name into a safe directory ID.

    Example:
        "Sir Julian!" -> "sir_julian"
    """
    value = re.sub(
        r"[^a-z0-9_-]+",
        "_",
        (name or "").strip().lower(),
    )

    return re.sub(
        r"_+",
        "_",
        value,
    ).strip("_")


def find_image(folder):
    """
    Find the reference image for a character.

    reference.png is preferred, but other common image formats
    are supported as a fallback.
    """
    preferred = [
        folder / "reference.png",
        folder / "reference.jpg",
        folder / "reference.jpeg",
        folder / "reference.webp",
    ]

    for path in preferred:
        if path.is_file():
            return path

    if folder.exists():
        for path in sorted(folder.iterdir()):
            if (
                path.is_file()
                and path.suffix.lower() in IMAGE_EXTENSIONS
            ):
                return path

    return None


def list_characters():
    """
    Return all characters that have a valid reference image.

    The returned values are the character directory IDs, which are
    also the values used by the Prepare Characters dropdown.
    """
    root = characters_root()
    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    return [
        path.name
        for path in sorted(
            root.iterdir(),
            key=lambda p: p.name.lower(),
        )
        if path.is_dir() and find_image(path)
    ]


def read_character(character_id):
    """
    Load character metadata and reference image information.

    This reads:

        characters/<character_id>/character.json

    and locates the corresponding reference image.
    """
    folder = characters_root() / character_id

    if not folder.is_dir():
        raise ValueError(
            f"Character '{character_id}' does not exist."
        )

    image = find_image(folder)

    if not image:
        raise ValueError(
            f"Character '{character_id}' has no reference image."
        )

    metadata = folder / "character.json"
    data = {}

    if metadata.is_file():
        with metadata.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    preserve = data.get(
        "preserve",
        [],
    )

    avoid = data.get(
        "avoid",
        [],
    )

    if isinstance(preserve, str):
        preserve = [preserve]

    if isinstance(avoid, str):
        avoid = [avoid]

    return {
        "id": character_id,
        "name": data.get(
            "name",
            character_id,
        ),
        "description": data.get(
            "description",
            "",
        ),
        "preserve": [
            str(value)
            for value in preserve
        ],
        "avoid": [
            str(value)
            for value in avoid
        ],
        "image": image,
        "path": folder,
    }


# ============================================================================
# Character Text Helpers
# ============================================================================

def split_lines(value):
    """
    Convert a multiline string into a cleaned list of values.
    """
    return [
        line.strip()
        for line in (value or "").splitlines()
        if line.strip()
    ]


def join_lines(values):
    """
    Convert a list of values into a comma-separated string.
    """
    return ", ".join(
        str(value).strip()
        for value in (values or [])
        if str(value).strip()
    )


# ============================================================================
# Character Persistence
# ============================================================================

def save_character_data(
    name,
    reference_image,
    description,
    preserve,
    avoid,
):
    """
    Persist a character to the character library.

    Existing characters are intentionally updated.

    The Editor's save_character option determines whether this function
    is called.
    """
    character_id = safe_id(name)

    if not character_id:
        raise ValueError(
            "Character name must contain a letter or number."
        )

    folder = characters_root() / character_id

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    import numpy as np
    from PIL import Image

    if reference_image is None:
        raise ValueError(
            "A reference image is required."
        )

    if len(reference_image) == 0:
        raise ValueError(
            "Reference image is empty."
        )

    image_array = (
        reference_image[0]
        .detach()
        .cpu()
        .numpy()
        * 255
    ).clip(
        0,
        255,
    ).astype(
        np.uint8
    )

    Image.fromarray(
        image_array
    ).save(
        folder / "reference.png"
    )

    metadata = {
        "name": name.strip(),
        "description": (
            description or ""
        ).strip(),
        "preserve": split_lines(
            preserve
        ),
        "avoid": split_lines(
            avoid
        ),
        "reference_image": "reference.png",
    }

    with (
        folder / "character.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return character_id, folder


# ============================================================================
# Character Data
# ============================================================================

def make_character(
    name,
    description="",
    preserve=None,
    avoid=None,
    image=None,
    character_id=None,
    path=None,
):
    """
    Create the structured CHARACTER object passed between D&D
    character nodes.

    The CHARACTER object contains:

        name
        description
        preserve
        avoid
        image
        id
        path

    The id and path are implementation details used internally by
    the character library.
    """
    if preserve is None:
        preserve = []

    if avoid is None:
        avoid = []

    return {
        "name": (name or "").strip(),

        "description": (
            description or ""
        ).strip(),

        "preserve": [
            str(value).strip()
            for value in preserve
            if str(value).strip()
        ],

        "avoid": [
            str(value).strip()
            for value in avoid
            if str(value).strip()
        ],

        "image": image,

        "id": character_id,

        "path": path,
    }


def character_from_library(character_id):
    """
    Load a character from the persistent library.

    Returns:

        (
            CHARACTER,
            IMAGE,
        )

    The IMAGE is the same reference image stored inside the CHARACTER
    object. It is returned separately because Character Reference and
    other nodes may need direct access to it.
    """
    data = read_character(
        character_id
    )

    image = load_image(
        data["image"]
    )

    character = make_character(
        name=data["name"],
        description=data["description"],
        preserve=data["preserve"],
        avoid=data["avoid"],
        image=image,
        character_id=data["id"],
        path=str(data["path"]),
    )

    return character, image


# ============================================================================
# Native ComfyUI Node Helpers
# ============================================================================

def get_core_node(node_name):
    """
    Resolve one of ComfyUI's native nodes.

    Supports both legacy V1 nodes and newer V3 API nodes.
    """
    import nodes

    mapping = getattr(
        nodes,
        "NODE_CLASS_MAPPINGS",
        {},
    )

    node_class = mapping.get(
        node_name
    )

    if node_class is None:
        raise RuntimeError(
            f"Required ComfyUI node '{node_name}' was not found."
        )

    return node_class()


def unwrap_node_result(result):
    """
    Convert a V3 io.NodeOutput into the same tuple-like result
    used by legacy ComfyUI nodes.
    """
    if hasattr(
        result,
        "result",
    ):
        result = result.result

    if result is None:
        return ()

    if isinstance(
        result,
        tuple,
    ):
        return result

    return (result,)


def run_core_node(
    node_name,
    **kwargs,
):
    """
    Execute a native ComfyUI node.

    ComfyUI V3 nodes use EXECUTE_NORMALIZED. That wrapper exposes
    (*args, **kwargs), so signature inspection is not appropriate
    for those nodes.

    Legacy V1 nodes continue to use signature-based filtering.
    """
    node = get_core_node(
        node_name
    )

    function_name = getattr(
        node,
        "FUNCTION",
        None,
    )

    if not function_name:
        raise RuntimeError(
            f"ComfyUI node '{node_name}' does not expose a FUNCTION."
        )

    function = getattr(
        node,
        function_name,
    )

    # ------------------------------------------------------------------------
    # ComfyUI V3
    # ------------------------------------------------------------------------

    if function_name in (
        "EXECUTE_NORMALIZED",
        "EXECUTE_NORMALIZED_ASYNC",
    ):
        if (
            function_name
            == "EXECUTE_NORMALIZED_ASYNC"
        ):
            raise RuntimeError(
                f"Native node '{node_name}' exposes an async execution "
                f"function, which cannot be called from this synchronous "
                f"custom node."
            )

        return unwrap_node_result(
            function(**kwargs)
        )

    # ------------------------------------------------------------------------
    # Legacy V1
    # ------------------------------------------------------------------------

    signature = inspect.signature(
        function
    )

    accepted = {}
    missing = []

    for (
        parameter_name,
        parameter,
    ) in signature.parameters.items():

        if parameter_name == "self":
            continue

        if parameter_name in kwargs:
            accepted[
                parameter_name
            ] = kwargs[
                parameter_name
            ]

        elif (
            parameter.default
            is inspect.Parameter.empty
            and parameter.kind
            not in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            )
        ):
            missing.append(
                parameter_name
            )

    if missing:
        raise RuntimeError(
            f"Unable to execute '{node_name}'. "
            f"Missing inputs: {', '.join(missing)}"
        )

    return unwrap_node_result(
        function(**accepted)
    )


def load_image(path):
    """
    Load an image through ComfyUI's native LoadImage implementation.
    """
    from nodes import LoadImage

    return LoadImage().load_image(
        str(path)
    )[0]


# ============================================================================
# Flux Kontext Reference Helpers
# ============================================================================

def apply_character_reference(
    image,
    conditioning,
    vae,
):
    """
    Apply one image as a Flux Kontext reference latent.

    Pipeline:

        IMAGE
          |
          v
        FluxKontextImageScale
          |
          v
        VAEEncode
          |
          v
        ReferenceLatent
          |
          v
        CONDITIONING

    The resulting CONDITIONING can be passed into another
    Character Reference or Character Editor node.
    """
    if image is None:
        raise ValueError(
            "A reference image is required."
        )

    if conditioning is None:
        raise ValueError(
            "Conditioning is required."
        )

    if vae is None:
        raise ValueError(
            "VAE is required."
        )

    # ------------------------------------------------------------------------
    # Scale reference image
    # ------------------------------------------------------------------------

    scaled_result = run_core_node(
        "FluxKontextImageScale",
        image=image,
    )

    if not scaled_result:
        raise RuntimeError(
            "FluxKontextImageScale returned no output."
        )

    scaled_image = scaled_result[0]

    # ------------------------------------------------------------------------
    # Encode reference image
    # ------------------------------------------------------------------------

    encoded_result = run_core_node(
        "VAEEncode",
        pixels=scaled_image,
        vae=vae,
    )

    if not encoded_result:
        raise RuntimeError(
            "VAEEncode returned no output."
        )

    latent = encoded_result[0]

    # ------------------------------------------------------------------------
    # Apply reference latent
    # ------------------------------------------------------------------------

    reference_result = run_core_node(
        "ReferenceLatent",
        conditioning=conditioning,
        latent=latent,
    )

    if not reference_result:
        raise RuntimeError(
            "ReferenceLatent returned no output."
        )

    return reference_result[0]