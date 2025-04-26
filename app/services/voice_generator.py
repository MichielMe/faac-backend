import traceback
from pathlib import Path

from elevenlabs.client import ElevenLabs
from loguru import logger

from app.core import settings
from app.models import VOICE_ID_MAPPING, Voice

# Check if API key is set
api_key = settings.ELEVEN_LABS_API_KEY
if not api_key:
    logger.warning("ELEVEN_LABS_API_KEY is not set or empty")

audio_dir = Path("app/assets/audio")


def generate_voice(text: str, voice: Voice):
    """Generate voice audio file for given text and voice type"""
    try:
        # Re-check API key
        if not api_key:
            logger.error(
                "Cannot generate voice: ELEVEN_LABS_API_KEY is not set or empty"
            )
            return None

        logger.info(f"Using API key: {api_key[:5]}... for voice generation")

        client = ElevenLabs(api_key=api_key)

        # Get the appropriate voice ID from the mapping
        if voice not in VOICE_ID_MAPPING:
            logger.error(f"Voice {voice} not found in VOICE_ID_MAPPING")
            return None

        voice_id = VOICE_ID_MAPPING[voice]
        if not voice_id:
            logger.error(f"Voice ID for {voice.name} is empty or invalid")
            return None

        logger.info(
            f"Generating {voice.name} voice for '{text}' with voice_id: {voice_id}"
        )

        # Make the API call
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        # Convert the generator to bytes
        audio_bytes = b"".join(chunk for chunk in audio)
        if not audio_bytes:
            logger.error(f"Received empty audio data for {text}")
            return None

        # Ensure audio directory exists
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Create filename based on text and voice type to avoid conflicts
        voice_name = voice.name.lower()
        filename = f"audio_{text}_{voice_name}.mp3"
        audio_path = audio_dir / filename

        # Save audio to file
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"Voice for '{text}' saved as {filename}")

        return str(audio_path)

    except Exception as e:
        logger.error(
            f"Error generating voice for '{text}' with voice {voice.name}: {str(e)}"
        )
        logger.error(traceback.format_exc())
        return None


def generate_voice_flemish(text: str, voice: Voice):
    """Generate Flemish voice audio file for given text and voice type"""
    try:
        # Re-check API key
        if not api_key:
            logger.error(
                "Cannot generate Flemish voice: ELEVEN_LABS_API_KEY is not set or empty"
            )
            return None

        logger.info(f"Using API key: {api_key[:5]}... for Flemish voice generation")

        client = ElevenLabs(api_key=api_key)

        # Get the appropriate voice ID from the mapping
        if voice not in VOICE_ID_MAPPING:
            logger.error(f"Voice {voice} not found in VOICE_ID_MAPPING")
            return None

        voice_id = VOICE_ID_MAPPING[voice]
        if not voice_id:
            logger.error(f"Voice ID for {voice.name} is empty or invalid")
            return None

        logger.info(
            f"Generating Flemish {voice.name} voice for '{text}' with voice_id: {voice_id}"
        )

        # Make the API call
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5",
            output_format="mp3_44100_128",
            language_code="nl",
        )

        # Convert the generator to bytes
        audio_bytes = b"".join(chunk for chunk in audio)
        if not audio_bytes:
            logger.error(f"Received empty audio data for Flemish {text}")
            return None

        # Ensure audio directory exists
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Create filename based on text and voice type to avoid conflicts
        voice_name = voice.name.lower()
        filename = f"audio_{text}_{voice_name}_flemish.mp3"
        audio_path = audio_dir / filename

        # Save audio to file
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"Flemish voice for '{text}' saved as {filename}")

        return str(audio_path)

    except Exception as e:
        logger.error(
            f"Error generating Flemish voice for '{text}' with voice {voice.name}: {str(e)}"
        )
        logger.error(traceback.format_exc())
        return None
