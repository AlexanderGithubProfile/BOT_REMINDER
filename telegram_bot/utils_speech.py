import requests

async def text_to_speech(text: str) -> None:
    """Преобразования голоса"""
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ"

    headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": "0bdbcf63934856091cef9ee133b1339f"
    }

    data = {
      "text": text,
      "model_id": "eleven_multilingual_v2",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "speaker_boost": True
      }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('assets/output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)