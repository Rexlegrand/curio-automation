"""Génération des 2 versions audio (voix Curio 8) via ElevenLabs API."""

import requests

from config import COST_AUDIO_VERSION, ELEVENLABS_CONFIG, ENV, log_api_call

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# Deux lectures différentes du même texte : v1 naturelle, v2 créative/expressive
# eleven_v3 n'accepte que des valeurs discrètes de stability : 0.0 / 0.5 / 1.0
VOICE_SETTINGS = {
    1: {"stability": 0.5, "similarity_boost": 0.8, "use_speaker_boost": True},
    2: {"stability": 0.0, "similarity_boost": 0.8, "use_speaker_boost": True},
}


def generate_audio_versions(script, output_dir):
    """Génère audio_v1.mp3 et audio_v2.mp3. Skip si le fichier existe déjà."""
    voice_id = ENV["ELEVENLABS_VOICE_ID"]
    generated = []

    for version in range(1, ELEVENLABS_CONFIG["versions_to_generate"] + 1):
        target = output_dir / f"audio_v{version}.mp3"
        if target.exists():
            print(f"  [skip] {target.name} existe déjà")
            generated.append(target)
            continue

        response = requests.post(
            API_URL.format(voice_id=voice_id),
            params={"output_format": ELEVENLABS_CONFIG["output_format"]},
            headers={"xi-api-key": ENV["ELEVENLABS_API_KEY"]},
            json={
                "text": script["narration"],
                "model_id": ELEVENLABS_CONFIG["model_id"],
                "voice_settings": VOICE_SETTINGS[version],
            },
            timeout=120,
        )
        if response.status_code != 200:
            raise RuntimeError(f"ElevenLabs {response.status_code} : {response.text[:300]}")

        target.write_bytes(response.content)
        log_api_call(output_dir, f"elevenlabs v{version}", COST_AUDIO_VERSION, target)
        print(f"  [ok] {target.name}")
        generated.append(target)

    return generated
