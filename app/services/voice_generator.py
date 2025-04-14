from pathlib import Path

from elevenlabs import play
from elevenlabs.client import ElevenLabs

from app.core.config import settings

api_key = settings.ELEVEN_LABS_API_KEY

audio_dir = Path("app/assets/audio")


def generate_voice(keyword: str):
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        text=keyword,
        voice_id="8z5UhJ1uv7X8TN5yg8oI",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    # Convert the generator to bytes
    audio_bytes = b"".join(chunk for chunk in audio)

    # Ensure audio directory exists
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Create filename based on keyword and save audio
    filename = f"audio_{keyword}.mp3"
    audio_path = audio_dir / filename

    # Save audio to file
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # Play the audio bytes directly
    play(audio_bytes)

    return str(audio_path)
