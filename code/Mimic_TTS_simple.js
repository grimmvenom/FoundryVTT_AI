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
 * - Play generated audio
 * - Download generated audio
 *
 * Expected API:
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

    const MIMIC_TTS_URL = "http://localhost:8188";

    const MIMIC_TTS_API_KEY =
        "mimic";


    ////////////////////////////////////////////////////////////
    //
    // Load Voices
    //
    ////////////////////////////////////////////////////////////

    let voices;

    try {

        const response = await fetch(
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


        const data = await response.json();

        voices = data.data || [];


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

    const voiceOptions = voices
        .map(voice => {

            const description =
                voice.description
                    ? ` - ${voice.description}`
                    : "";

            return `
                <option value="${voice.id}">
                    ${voice.name}${description}
                </option>
            `;

        })
        .join("");


    ////////////////////////////////////////////////////////////
    //
    // Dialog
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
                        // Notify User
                        //
                        ////////////////////////////////////////////////////

                        ui.notifications.info(
                            `Generating ${voice} voice...`
                        );


                        ////////////////////////////////////////////////////
                        //
                        // Send Request
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
                                                    emotion || "neutral",

                                                instructions:
                                                    instructions || ""

                                            })

                                    }

                                );


                            ////////////////////////////////////////////////////
                            //
                            // Check Response
                            //
                            ////////////////////////////////////////////////////

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
                                    // Ignore JSON parse errors
                                }


                                throw new Error(
                                    errorMessage
                                );

                            }


                            ////////////////////////////////////////////////////
                            //
                            // Get WAV
                            //
                            ////////////////////////////////////////////////////

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
                        // Create Audio URL
                        //
                        ////////////////////////////////////////////////////

                        const audioUrl =
                            URL.createObjectURL(
                                audioBlob
                            );


                        ////////////////////////////////////////////////////
                        //
                        // Play Audio
                        //
                        ////////////////////////////////////////////////////

                        const playAudio =
                            () => {

                                const audio =
                                    new Audio(
                                        audioUrl
                                    );

                                audio.volume =
                                    1.0;

                                audio.play()
                                    .catch(error => {

                                        console.error(
                                            "Audio playback failed:",
                                            error
                                        );

                                        ui.notifications.error(
                                            "Unable to play generated audio."
                                        );

                                    });

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
                                    `${voice}-dialogue.wav`;

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
                                    ${voice}
                                </p>

                                <p>
                                    <strong>Emotion:</strong>
                                    ${emotion || "neutral"}
                                </p>

                                <p>
                                    <strong>Instructions:</strong>
                                    ${instructions || "None"}
                                </p>

                                <hr>

                                <p>
                                    ${script}
                                </p>

                            `,

                            buttons: {

                                play: {

                                    icon:
                                        '<i class="fas fa-play"></i>',

                                    label:
                                        "Play Audio",

                                    callback:
                                        () => {

                                            playAudio();

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

                                    //
                                    // Keep the object URL alive
                                    // for a short time so the user
                                    // can still play/download it.
                                    //

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

                        if (autoplay) {

                            playAudio();

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

                //
                // Focus script box
                //

                html
                    .find("#mimic-script")
                    .focus();

            }

    }).render(
        true
    );


})();