/*
 * Mimic-TTS Character Voice Macro
 *
 * Features:
 * - Dynamically loads available voices from Mimic-TTS
 * - Select character / voice
 * - Enter script
 * - Enter emotion
 * - Enter voice instructions
 * - Generate WAV through Mimic-TTS
 * - Upload generated WAV into Foundry
 * - Save under:
 *
 *     assets/audio/mimic-tts/<character>/
 *
 * - Create / reuse:
 *
 *     Mimic-TTS - <character>
 *
 * - Add generated audio to the character playlist
 * - Configure playlist as Soundboard Only
 * - Disable looping
 * - Play audio through Foundry's Playlist system
 * - Download generated WAV
 *
 *
 * Mimic-TTS API:
 *
 * GET:
 *   http://localhost:8188/v1/voices
 *
 * POST:
 *   http://localhost:8188/v1/audio/speech
 *
 */


(async () => {

    ////////////////////////////////////////////////////////////
    //
    // Configuration
    //
    ////////////////////////////////////////////////////////////

    const MIMIC_TTS_URL =
        "http://localhost:8188";

    const MIMIC_TTS_API_KEY =
        "mimic";

    //
    // Foundry audio root.
    //
    // This path is relative to Foundry's Data directory.
    //

    const AUDIO_ROOT =
        "assets/audio/mimic-tts";


    ////////////////////////////////////////////////////////////
    //
    // Utility: Escape HTML
    //
    ////////////////////////////////////////////////////////////

    const escapeHtml = (value) => {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    };


    ////////////////////////////////////////////////////////////
    //
    // Utility: Sanitize Filename
    //
    ////////////////////////////////////////////////////////////

    const sanitizeFilename = (value) => {

        return String(value ?? "")
            .trim()
            .replace(/[<>:"/\\|?*\x00-\x1F]/g, "")
            .replace(/\s+/g, " ")
            .substring(0, 120);

    };


    ////////////////////////////////////////////////////////////
    //
    // Utility: Create Time-Based Filename
    //
    ////////////////////////////////////////////////////////////

    const createFilename = (description) => {

        const now =
            new Date();

        const time =
            now.toLocaleTimeString(
                "en-US",
                {
                    hour: "numeric",
                    minute: "2-digit",
                    second: "2-digit"
                }
            );

        const safeDescription =
            sanitizeFilename(
                description
            ) || "dialogue";

        return `${time} - ${safeDescription}.wav`;

    };


    ////////////////////////////////////////////////////////////
    //
    // Load Voices
    //
    ////////////////////////////////////////////////////////////

    let voices;

    try {

        const response =
            await fetch(
                `${MIMIC_TTS_URL}/v1/voices`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${MIMIC_TTS_API_KEY}`
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}: ${response.statusText}`
            );

        }


        const data =
            await response.json();


        voices =
            data.data || [];


    } catch (error) {

        ui.notifications.error(
            "Unable to connect to Mimic-TTS."
        );

        console.error(
            "Mimic-TTS voice loading failed:",
            error
        );

        return;

    }


    ////////////////////////////////////////////////////////////
    //
    // Validate Voices
    //
    ////////////////////////////////////////////////////////////

    if (!voices.length) {

        ui.notifications.warn(
            "Mimic-TTS returned no available voices."
        );

        return;

    }


    ////////////////////////////////////////////////////////////
    //
    // Build Voice Dropdown
    //
    ////////////////////////////////////////////////////////////

    const voiceOptions =
        voices
            .map(
                voice => {

                    const description =
                        voice.description
                            ? ` - ${voice.description}`
                            : "";

                    return `
                        <option value="${escapeHtml(voice.id)}">
                            ${escapeHtml(voice.name)}${escapeHtml(description)}
                        </option>
                    `;

                }
            )
            .join("");


    ////////////////////////////////////////////////////////////
    //
    // Dialog Content
    //
    ////////////////////////////////////////////////////////////

    const content = `

        <form>

            <div class="form-group">

                <label>
                    Character / Voice
                </label>

                <select
                    id="mimic-voice"
                    style="width: 100%;"
                >

                    ${voiceOptions}

                </select>

            </div>


            <div class="form-group">

                <label>
                    Script
                </label>

                <textarea
                    id="mimic-script"
                    rows="7"
                    style="
                        width: 100%;
                        resize: vertical;
                    "
                    placeholder="Enter dialogue..."
                ></textarea>

            </div>


            <div class="form-group">

                <label>
                    Filename / Description
                </label>

                <input
                    id="mimic-description"
                    type="text"
                    style="width: 100%;"
                    placeholder="Example: greeting the party"
                />

            </div>


            <div class="form-group">

                <label>
                    Emotion
                </label>

                <input
                    id="mimic-emotion"
                    type="text"
                    style="width: 100%;"
                    placeholder="neutral"
                    value="neutral"
                />

            </div>


            <div class="form-group">

                <label>
                    Voice Instructions
                </label>

                <textarea
                    id="mimic-instructions"
                    rows="3"
                    style="
                        width: 100%;
                        resize: vertical;
                    "
                    placeholder="Optional voice direction..."
                ></textarea>

            </div>


            <div class="form-group">

                <label>

                    <input
                        id="mimic-autoplay"
                        type="checkbox"
                        checked
                    />

                    Play audio automatically

                </label>

            </div>

        </form>

    `;


    ////////////////////////////////////////////////////////////
    //
    // Ensure Character Playlist Exists
    //
    ////////////////////////////////////////////////////////////

    const getOrCreatePlaylist =
        async (voice) => {

            const playlistName =
                `Mimic-TTS - ${voice}`;


            //
            // Look for existing playlist.
            //

            let playlist =
                game.playlists.contents.find(
                    p =>
                        p.name === playlistName
                );


            //
            // Create playlist if necessary.
            //
            // IMPORTANT:
            //
            // Do NOT set "mode" here.
            //
            // Foundry versions differ in how the
            // Playlist mode field is represented.
            //
            // We configure it after creation using
            // the numeric Playlist mode value.
            //

            if (!playlist) {

                console.log(
                    `Creating playlist: ${playlistName}`
                );


                playlist =
                    await Playlist.create(
                        {
                            name:
                                playlistName,

                            description:
                                `Generated Mimic-TTS dialogue for ${voice}`,

                            playing:
                                false,

                            seed:
                                false,

                            // Foundry playlist mode:
                            // 1 = sequential
                            //
                            // We intentionally do not set
                            // this here. It will be updated
                            // after creation.
                        }
                    );

            }


            //
            // Verify we actually received a Playlist
            // document before continuing.
            //

            if (
                !playlist ||
                typeof playlist.createEmbeddedDocuments !==
                    "function"
            ) {

                throw new Error(
                    `Unable to create or locate playlist "${playlistName}".`
                );

            }


            return playlist;

        };


    ////////////////////////////////////////////////////////////
    //
    // Configure Playlist as Soundboard
    //
    ////////////////////////////////////////////////////////////

    const configureSoundboardPlaylist =
        async (playlist) => {

            if (!playlist) {

                throw new Error(
                    "Playlist document is undefined."
                );

            }


            //
            // Foundry Playlist modes are numeric.
            //
            // Soundboard mode is 2 in current Foundry versions.
            //
            // IMPORTANT:
            // This must be a NUMBER, not an object.
            //

            try {

                await playlist.update(
                    {
                        mode: 2,

                        playing: false,

                        seed: false
                    }
                );

            } catch (error) {

                console.warn(
                    "Unable to configure playlist mode:",
                    error
                );

                //
                // Do not stop the macro if the playlist
                // is already configured correctly.
                //

            }

        };


    ////////////////////////////////////////////////////////////
    //
    // Add Sound to Playlist
    //
    ////////////////////////////////////////////////////////////

    const addSoundToPlaylist =
        async (
            playlist,
            audioPath,
            filename
        ) => {

            //
            // Verify playlist.
            //

            if (!playlist) {

                throw new Error(
                    "Cannot add sound: playlist is undefined."
                );

            }


            if (
                typeof playlist.createEmbeddedDocuments !==
                    "function"
            ) {

                throw new Error(
                    "Cannot add sound: invalid Playlist document."
                );

            }


            console.log(
                `Adding ${filename} to playlist ${playlist.name}`
            );


            //
            // Create PlaylistSound.
            //

            const sounds =
                await playlist.createEmbeddedDocuments(
                    "PlaylistSound",
                    [
                        {
                            name:
                                filename,

                            path:
                                audioPath,

                            playing:
                                false,

                            paused:
                                false,

                            repeat:
                                false,

                            volume:
                                1.0
                        }
                    ]
                );


            if (
                !sounds ||
                !sounds.length
            ) {

                throw new Error(
                    "Foundry did not create the PlaylistSound."
                );

            }


            return sounds[0];

        };


    ////////////////////////////////////////////////////////////
    //
    // Play Foundry Playlist Sound
    //
    ////////////////////////////////////////////////////////////

    const playFoundrySound =
        async (
            playlist,
            playlistSound
        ) => {

            if (!playlist) {

                throw new Error(
                    "Playlist is undefined."
                );

            }


            if (!playlistSound) {

                throw new Error(
                    "PlaylistSound is undefined."
                );

            }


            //
            // Ensure this playlist is configured as
            // Soundboard Only.
            //

            await configureSoundboardPlaylist(
                playlist
            );


            //
            // Explicitly disable looping.
            //

            await playlistSound.update(
                {
                    repeat:
                        false,

                    paused:
                        false,

                    playing:
                        false
                }
            );


            console.log(
                `Playing Foundry PlaylistSound: ${playlistSound.name}`
            );


            //
            // Use the PlaylistSound document's
            // play() method.
            //
            // This is the correct Foundry API for
            // playing an existing PlaylistSound.
            //

            if (
                typeof playlistSound.play ===
                    "function"
            ) {

                await playlistSound.play();

                return;

            }


            //
            // Fallback:
            // Update playing state.
            //

            await playlistSound.update(
                {
                    playing:
                        true
                }
            );

        };


    ////////////////////////////////////////////////////////////
    //
    // Open Dialog
    //
    ////////////////////////////////////////////////////////////

    new Dialog({

        title:
            "Mimic-TTS Character Dialogue",

        content:
            content,


        buttons: {

            generate: {

                icon:
                    '<i class="fas fa-microphone"></i>',

                label:
                    "Generate Audio",


                callback:
                    async (html) => {

                        ////////////////////////////////////////////////////
                        //
                        // Read Form
                        //
                        ////////////////////////////////////////////////////

                        const voice =
                            html
                                .find("#mimic-voice")
                                .val();


                        const script =
                            html
                                .find("#mimic-script")
                                .val()
                                .trim();


                        const description =
                            html
                                .find("#mimic-description")
                                .val()
                                .trim();


                        const emotion =
                            html
                                .find("#mimic-emotion")
                                .val()
                                .trim();


                        const instructions =
                            html
                                .find("#mimic-instructions")
                                .val()
                                .trim();


                        const autoplay =
                            html
                                .find("#mimic-autoplay")
                                .is(":checked");


                        ////////////////////////////////////////////////////
                        //
                        // Validate Script
                        //
                        ////////////////////////////////////////////////////

                        if (!script) {

                            ui.notifications.warn(
                                "Please enter a script."
                            );

                            return;

                        }


                        ////////////////////////////////////////////////////
                        //
                        // Notify
                        //
                        ////////////////////////////////////////////////////

                        ui.notifications.info(
                            `Generating ${voice} voice...`
                        );


                        ////////////////////////////////////////////////////
                        //
                        // Generate TTS
                        //
                        ////////////////////////////////////////////////////

                        let audioBlob;

                        try {

                            const response =
                                await fetch(

                                    `${MIMIC_TTS_URL}/v1/audio/speech`,

                                    {

                                        method:
                                            "POST",

                                        headers: {

                                            "Content-Type":
                                                "application/json",

                                            "Authorization":
                                                `Bearer ${MIMIC_TTS_API_KEY}`

                                        },

                                        body:
                                            JSON.stringify({

                                                model:
                                                    "mimic-tts",

                                                voice:
                                                    voice,

                                                input:
                                                    script,

                                                emotion:
                                                    emotion ||
                                                    "neutral",

                                                instructions:
                                                    instructions ||
                                                    ""

                                            })

                                    }

                                );


                            if (!response.ok) {

                                let errorMessage =
                                    `HTTP ${response.status}`;


                                try {

                                    const errorData =
                                        await response.json();


                                    if (
                                        errorData.detail
                                    ) {

                                        errorMessage =
                                            errorData.detail;

                                    }

                                } catch (e) {

                                    // Ignore JSON parsing errors.

                                }


                                throw new Error(
                                    errorMessage
                                );

                            }


                            audioBlob =
                                await response.blob();


                        } catch (error) {

                            console.error(
                                "Mimic-TTS generation failed:",
                                error
                            );


                            ui.notifications.error(
                                `Mimic-TTS error: ${error.message}`
                            );

                            return;

                        }


                        ////////////////////////////////////////////////////
                        //
                        // Create Filename
                        //
                        ////////////////////////////////////////////////////

                        const filename =
                            createFilename(
                                description ||
                                script.substring(
                                    0,
                                    60
                                )
                            );


                        ////////////////////////////////////////////////////
                        //
                        // Create Object URL
                        //
                        ////////////////////////////////////////////////////

                        const audioUrl =
                            URL.createObjectURL(
                                audioBlob
                            );


                        ////////////////////////////////////////////////////
                        //
                        // Upload Audio to Foundry
                        //
                        ////////////////////////////////////////////////////

                        let audioPath;

                        try {

                            const voiceDirectory =
                                `${AUDIO_ROOT}/${sanitizeFilename(voice)}`;


                            console.log(
                                `Uploading generated audio to Foundry...`
                            );


                            //
                            // Foundry's FilePicker upload
                            // expects a File with a valid extension.
                            //

                            const audioFile =
                                new File(
                                    [
                                        audioBlob
                                    ],
                                    filename,
                                    {
                                        type:
                                            "audio/wav"
                                    }
                                );


                            //
                            // Ensure target directory exists.
                            //

                            try {

                                await FilePicker.createDirectory(
                                    "data",
                                    voiceDirectory
                                );

                            } catch (error) {

                                //
                                // Directory may already exist.
                                //

                                console.log(
                                    "Audio directory already exists or was created previously."
                                );

                            }


                            //
                            // Upload.
                            //

                            const uploadResult =
                                await FilePicker.upload(
                                    "data",
                                    voiceDirectory,
                                    audioFile,
                                    {},
                                    {
                                        notify:
                                            false
                                    }
                                );


                            audioPath =
                                uploadResult?.path;


                            if (!audioPath) {

                                throw new Error(
                                    "Foundry did not return an uploaded audio path."
                                );

                            }


                            console.log(
                                `Uploaded audio: ${audioPath}`
                            );


                        } catch (error) {

                            console.error(
                                "Mimic-TTS upload failed:",
                                error
                            );


                            ui.notifications.error(
                                `Audio upload failed: ${error.message}`
                            );


                            return;

                        }


                        ////////////////////////////////////////////////////
                        //
                        // Get / Create Playlist
                        //
                        ////////////////////////////////////////////////////

                        let playlist;

                        let playlistSound;

                        try {

                            playlist =
                                await getOrCreatePlaylist(
                                    voice
                                );


                            //
                            // Add sound to playlist.
                            //

                            playlistSound =
                                await addSoundToPlaylist(
                                    playlist,
                                    audioPath,
                                    filename
                                );


                            //
                            // Configure soundboard mode.
                            //

                            await configureSoundboardPlaylist(
                                playlist
                            );


                            ui.notifications.info(
                                `Added to ${playlist.name}`
                            );


                        } catch (error) {

                            console.error(
                                "Failed to add sound to playlist:",
                                error
                            );


                            ui.notifications.error(
                                `Unable to add audio to playlist: ${error.message}`
                            );


                            //
                            // Audio was successfully uploaded,
                            // so do not delete or invalidate it.
                            //

                        }


                        ////////////////////////////////////////////////////
                        //
                        // Play Foundry Audio
                        //
                        ////////////////////////////////////////////////////

                        const playAudio =
                            async () => {

                                if (
                                    !playlist ||
                                    !playlistSound
                                ) {

                                    ui.notifications.error(
                                        "The audio was uploaded, but no valid Foundry playlist sound is available."
                                    );

                                    return;

                                }


                                try {

                                    await playFoundrySound(
                                        playlist,
                                        playlistSound
                                    );


                                    console.log(
                                        "Playing jester dialogue."
                                    );


                                } catch (error) {

                                    console.error(
                                        "Unable to play Foundry audio:",
                                        error
                                    );


                                    ui.notifications.error(
                                        `Unable to play Foundry audio: ${error.message}`
                                    );

                                }

                            };


                        ////////////////////////////////////////////////////
                        //
                        // Download Audio
                        //
                        ////////////////////////////////////////////////////

                        const downloadAudio =
                            () => {

                                const link =
                                    document.createElement(
                                        "a"
                                    );


                                link.href =
                                    audioUrl;


                                link.download =
                                    filename;


                                document.body.appendChild(
                                    link
                                );


                                link.click();


                                link.remove();

                            };


                        ////////////////////////////////////////////////////
                        //
                        // Result Dialog
                        //
                        ////////////////////////////////////////////////////

                        new Dialog({

                            title:
                                `Generated: ${voice}`,

                            content: `

                                <p>
                                    <strong>Voice:</strong>
                                    ${escapeHtml(voice)}
                                </p>

                                <p>
                                    <strong>Filename:</strong>
                                    ${escapeHtml(filename)}
                                </p>

                                <p>
                                    <strong>Emotion:</strong>
                                    ${escapeHtml(
                                        emotion ||
                                        "neutral"
                                    )}
                                </p>

                                <p>
                                    <strong>Instructions:</strong>
                                    ${escapeHtml(
                                        instructions ||
                                        "None"
                                    )}
                                </p>

                                <p>
                                    <strong>Playlist:</strong>
                                    ${escapeHtml(
                                        playlist
                                            ? playlist.name
                                            : "Upload only"
                                    )}
                                </p>

                                <hr>

                                <p>
                                    ${escapeHtml(script)}
                                </p>

                            `,

                            buttons: {

                                play: {

                                    icon:
                                        '<i class="fas fa-play"></i>',

                                    label:
                                        "Play Audio",

                                    callback:
                                        async () => {

                                            await playAudio();

                                        }

                                },


                                download: {

                                    icon:
                                        '<i class="fas fa-download"></i>',

                                    label:
                                        "Download WAV",

                                    callback:
                                        () => {

                                            downloadAudio();

                                        }

                                },


                                close: {

                                    icon:
                                        '<i class="fas fa-times"></i>',

                                    label:
                                        "Close"

                                }

                            },


                            default:
                                "play",


                            close:
                                () => {

                                    setTimeout(

                                        () => {

                                            URL.revokeObjectURL(
                                                audioUrl
                                            );

                                        },

                                        60000

                                    );

                                }

                        }).render(
                            true
                        );


                        ////////////////////////////////////////////////////
                        //
                        // Autoplay
                        //
                        ////////////////////////////////////////////////////

                        if (
                            autoplay &&
                            playlist &&
                            playlistSound
                        ) {

                            await playAudio();

                        }

                    }

            },


            cancel: {

                icon:
                    '<i class="fas fa-times"></i>',

                label:
                    "Cancel"

            }

        },


        default:
            "generate",


        render:
            (html) => {

                html
                    .find("#mimic-script")
                    .focus();

            }

    }).render(
        true
    );


})();