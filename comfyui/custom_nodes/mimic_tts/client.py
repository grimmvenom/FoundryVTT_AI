import requests


class MimicTTSClient:
    """
    Client for the Mimic-TTS HTTP API.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    ############################################################
    #
    # Characters
    #
    ############################################################

    def list_characters(self):
        response = requests.get(
            f"{self.base_url}/v1/characters",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def create_character(
        self,
        name: str,
        audio: bytes,
        instructions: str = "",
        personality: str = "",
        description: str = "",
        overwrite: bool = False,
    ):
        files = {
            "audio": (
                "character.wav",
                audio,
                "audio/wav",
            )
        }

        data = {
            "name": name,
            "instructions": instructions,
            "personality": personality,
            "description": description,
            "overwrite": str(overwrite).lower(),
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/characters",
                files=files,
                data=data,
                timeout=600,
            )

            response.raise_for_status()

        except requests.HTTPError as exc:
            if response.status_code == 409:
                raise ValueError(
                    f"Character '{name}' already exists. "
                    "Enable Overwrite to replace it."
                ) from exc

            try:
                detail = response.json().get(
                    "detail",
                    response.text,
                )
            except Exception:
                detail = response.text

            raise RuntimeError(
                f"Failed to create character: {detail}"
            ) from exc

        return response.json()

    def update_character(
        self,
        name: str,
        audio: bytes = None,
        instructions: str = None,
        personality: str = None,
        description: str = None,
    ):
        """
        Update an existing character.

        Any field set to None is left unchanged.

        Audio, when supplied, replaces the existing voice
        clone prompt and transcript.
        """

        files = None

        if audio is not None:
            files = {
                "audio": (
                    "character.wav",
                    audio,
                    "audio/wav",
                )
            }

        data = {
            "name": name,
        }

        if instructions is not None:
            data["instructions"] = instructions

        if personality is not None:
            data["personality"] = personality

        if description is not None:
            data["description"] = description

        try:
            response = requests.patch(
                f"{self.base_url}/v1/characters/{name}",
                files=files,
                data=data,
                timeout=600,
            )

            response.raise_for_status()

        except requests.HTTPError as exc:
            try:
                detail = response.json().get(
                    "detail",
                    response.text,
                )
            except Exception:
                detail = response.text

            raise RuntimeError(
                f"Failed to update character: {detail}"
            ) from exc

        return response.json()

    ############################################################
    #
    # Speech
    #
    ############################################################

    def speech(
        self,
        text: str,
        voice: str,
        instructions: str = "",
        response_format: str = "wav",
    ) -> bytes:
        """
        Call the OpenAI-compatible speech endpoint.
        """

        payload = {
            "input": text,
            "voice": voice,
            "response_format": response_format,
        }

        if instructions:
            payload["instructions"] = instructions

        response = requests.post(
            f"{self.base_url}/v1/audio/speech",
            json=payload,
            timeout=600,
        )

        response.raise_for_status()

        return response.content

    ############################################################
    #
    # Roleplay
    #
    ############################################################

    def roleplay(
        self,
        *,
        character: str,
        text: str,
        instructions: str = "",
        emotion: str = "neutral",
    ):
        """
        Generate roleplay speech from an existing character.

        The API returns audio/wav directly.
        """

        url = f"{self.base_url}/v1/roleplay"

        payload = {
            "character": character,
            "text": text,
            "instructions": instructions,
            "emotion": emotion,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=300,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise RuntimeError(
                "Mimic-TTS roleplay request failed:\n"
                f"URL: {url}\n"
                f"Error: {exc}\n"
                f"Response: {getattr(exc.response, 'text', '')[:2000]}"
            ) from exc

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "audio/wav" not in content_type:
            raise RuntimeError(
                "Mimic-TTS roleplay API returned an "
                "unexpected response:\n"
                f"URL: {url}\n"
                f"HTTP status: {response.status_code}\n"
                f"Content-Type: {content_type}\n"
                f"Response: {response.text[:2000]}"
            )

        return response.content