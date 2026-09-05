"""Reel « lacs roses » rendu 100% localement — deux architectures narratives.

Piste ouverte pour sortir de Dreamina : le hook n'est plus une vidéo générée
sur une plateforme externe, c'est le Curio découpé animé dans Remotion, qui
s'illumine au rythme de la voix (anneau vert façon Discord, validé le 31/08).
Plus aucune étape manuelle entre le script et le MP4.

Deux versions sont produites sur le même script (reel du 17/08, lacs roses) :

  A — full_curio   Curio parle du début à la fin. Grand au centre sur le hook
                   et le CTA, en pastille en bas à droite pendant le contenu.

  B — narrateur    Curio fait le hook et le CTA ; un narrateur (voix plus
                   grave, plus posée) porte toute la structure et n'a AUCUNE
                   représentation à l'écran — registre « faceless ». Curio
                   n'intervient qu'à deux moments, en pastille. Les sous-titres
                   changent de couleur selon le locuteur : vert Curio, bleu
                   narrateur.

Ce qui coûte : ElevenLabs (~0,25 $ par version, un appel par segment) et rien
d'autre. Les photos viennent de Pexels (gratuit, clé déjà en place), Whisper et
Remotion tournent en local. Zéro GPT Image : les 7 photos trouvées couvrent
tous les segments.

Découpage par segment plutôt qu'un seul appel TTS : c'est ce qui donne les
frontières exactes entre locuteurs (indispensable en version B) et les bornes
de scène, sans avoir à les deviner après coup.

Tout est mis en cache sur disque (photos, MP3 par segment, SRT) : relancer le
script ne refacture rien. Supprimer testing_remotion/curio_reel_local/ pour
repartir de zéro.
"""

import array
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import CTA_TEXTE, ELEVENLABS_CONFIG, ENV, VIDEO_FPS  # noqa: E402
from generators.subtitle_generator import generate_subtitles  # noqa: E402

REPO = Path(__file__).parent.resolve()
CURIO_CUTOUT = REPO / "assets/curio_cutout/curio_flat.png"
REMOTION_DIR = REPO / "remotion"
PUBLIC_DIR = REMOTION_DIR / "public" / "curio-reel"
WORKSPACE = REPO / "testing_remotion/curio_reel_local"
PHOTO_DIR = WORKSPACE / "photos"
VOICE_DIR = WORKSPACE / "voix"

# ELEVENLABS_VOICE_ID pointe sur « Curio 8 v3 », une voix clonée (IVC) : elle
# est refusée par l'abonnement pay-as-you-go actuel — 401 ivc_not_permitted.
# Les trois autres voix Curio du compte répondent normalement ; on prend la plus
# récente qui passe. À remettre sur ENV["ELEVENLABS_VOICE_ID"] le jour où le
# plan autorise à nouveau les voix clonées.
VOICE_CURIO = "iDpRg8Sg5Xh5u2THyfPl"  # « curio 8 v2 »
# « Daniel - Steady Broadcaster » : registre grave et posé, archétype narrateur.
# eleven_v3 est multilingue, la voix lit donc le français — mais elle est
# étiquetée british, un accent résiduel est possible. Un échantillon comparatif
# avec « Brian - Deep, Resonant » est produit à côté (voir NARRATOR_CANDIDATES).
VOICE_NARRATEUR = "onwK4e9ZLuTAKqWW03F9"
NARRATOR_CANDIDATES = {
    "daniel": "onwK4e9ZLuTAKqWW03F9",
    "brian": "nPczCjzI2devNBz1zQrb",
}
NARRATOR_SAMPLE = ("On en trouve en Australie, au lac Hillier, "
                   "et aussi au Sénégal, avec le lac Rose.")

TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
# eleven_v3 n'accepte que 0.0 / 0.5 / 1.0 en stability. Curio garde le réglage
# expressif de audio_v2 (0.0) ; le narrateur est posé, donc stable (0.5).
SETTINGS_CURIO = {"stability": 0.0, "similarity_boost": 0.8, "use_speaker_boost": True}
SETTINGS_NARRATEUR = {"stability": 0.5, "similarity_boost": 0.85, "use_speaker_boost": True}

GAP_SAME_SPEAKER = 0.14   # respiration entre deux segments d'une même voix
GAP_SPEAKER_CHANGE = 0.30  # passage de relais entre deux voix
TAIL = 0.35                # silence final, pour ne pas couper sur le dernier mot

SAMPLE_RATE = 48000
ATTACK, RELEASE = 0.55, 0.14  # enveloppe de la lumière autour de Curio

# Transition d'un état de Curio à l'autre (grand ↔ pastille ↔ absent).
STATE_BLEND_S = 0.45

# --- Script du reel -----------------------------------------------------------
# Textes repris du script.json du 17/08, sauf le CTA : celui du fichier date
# d'avant v2.11 (« Commente CURIO... »), on utilise la formule en vigueur.
#
# photo  : clé de PHOTO_QUERIES ci-dessous.
# motion : mouvement de caméra de la scène (jamais deux fois le même d'affilée).
# label  : cartouche affiché — c'est la technique HORS caméra du beat, exigée
#          par CLAUDE.md §10 (un mouvement de caméra ne suffit jamais seul).
SEGMENTS = [
    {"role": "hook", "texte": "Attends... il existe des lacs entièrement roses ?",
     "photo": "lac_rose", "motion": "zoom-in", "label": ""},
    {"role": "illustration_1",
     "texte": "Oui, complètement roses ! Cette couleur vient de minuscules algues "
              "et du sel dans l'eau. C'est un phénomène naturel fascinant.",
     "photo": "sel_cristaux", "motion": "pan-right", "label": "Des algues + du sel"},
    {"role": "curio_a", "texte": "Vus de loin, on dirait un immense lac de fraise.",
     "photo": "lac_pastel", "motion": "zoom-out", "label": ""},
    {"role": "illustration_2",
     "texte": "On en trouve en Australie, au lac Hillier, et aussi au Sénégal, "
              "avec le lac Rose.",
     "photo": "lac_et_mer", "motion": "pan-left", "label": "Australie · Lac Hillier"},
    {"role": "curio_b",
     "texte": "L'eau est si salée qu'on flotte facilement dessus, comme dans la mer Morte.",
     "photo": "flotter", "motion": "zoom-in", "label": ""},
    {"role": "illustration_3", "texte": "La nature nous réserve de belles surprises !",
     "photo": "lac_aerien", "motion": "zoom-out", "label": ""},
    # texte_dit : ce que la voix prononce, quand il diffère du texte de
    # référence. La barre oblique de CTA_TEXTE (« activité/un exercice ») n'a
    # pas de prononciation : ElevenLabs la lit comme une syllabe parasite et
    # Whisper en fait « activité-slagane ». Le CTA écrit, lui, ne change pas.
    {"role": "cta", "texte": CTA_TEXTE,
     "texte_dit": CTA_TEXTE.replace("activité/un", "activité ou un"),
     "photo": "plage_rose", "motion": "pan-up", "label": ""},
]

# Sélection Pexels : la requête ET un fragment du texte descriptif de la photo
# retenue. On filtre sur ce fragment plutôt que sur un rang de résultat —
# l'ordre renvoyé par Pexels n'est pas stable d'un jour à l'autre.
PHOTO_QUERIES = {
    "lac_rose":     ("pink lake aerial", "transparent pink water"),
    "sel_cristaux": ("pink salt lake water", "crystallized branches"),
    "lac_pastel":   ("pink salt lake water", "Las Coloradas"),
    "lac_et_mer":   ("pink lake aerial", "Sasyk-Sivash"),
    "flotter":      ("person floating salt water dead sea", "reading a newspaper"),
    "lac_aerien":   ("pink lake aerial", "Lake Tyrrell"),
    "plage_rose":   ("pink salt lake water", "pink salt beach"),
}

# Qui parle, par version.
SPEAKERS = {
    "full_curio": {s["role"]: "curio" for s in SEGMENTS},
    "narrateur": {
        "hook": "curio", "illustration_1": "narrateur", "curio_a": "curio",
        "illustration_2": "narrateur", "curio_b": "curio",
        "illustration_3": "narrateur", "cta": "curio",
    },
}

# État de Curio à l'écran, par version. "big" = plein centre, "pill" = pastille
# en bas à droite, "none" = absent (le narrateur parle, registre faceless).
AVATAR = {
    "full_curio": {"hook": "big", "illustration_1": "pill", "curio_a": "pill",
                   "illustration_2": "pill", "curio_b": "pill",
                   "illustration_3": "pill", "cta": "big"},
    "narrateur": {"hook": "big", "illustration_1": "none", "curio_a": "pill",
                  "illustration_2": "none", "curio_b": "pill",
                  "illustration_3": "none", "cta": "big"},
}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace") if isinstance(r.stderr, bytes) else r.stderr
        raise RuntimeError(f"échec: {' '.join(map(str, cmd))}\n{err[-1500:]}")
    return r


# --- Photos -------------------------------------------------------------------

def resolve_photos():
    """Télécharge les 7 photos en pleine résolution. Rien n'est refait si présent."""
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = PHOTO_DIR / "photos.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    for key, (query, needle) in PHOTO_QUERIES.items():
        dest = PHOTO_DIR / f"{key}.jpg"
        if dest.exists() and key in manifest:
            continue
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": ENV["PEXELS_API_KEY"]},
            params={"query": query, "per_page": 20, "orientation": "portrait"},
            timeout=30,
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        match = next((p for p in photos if needle.lower() in (p.get("alt") or "").lower()), None)
        if match is None:
            raise RuntimeError(
                f"photo '{key}' introuvable : aucun résultat de « {query} » ne contient "
                f"« {needle} ». La sélection Pexels a changé, revoir PHOTO_QUERIES."
            )
        # src.original : la pleine résolution. src.large2x plafonne à 1300 px de
        # haut, insuffisant pour un cadre 1080x1920 avec mouvement de caméra.
        blob = requests.get(match["src"]["original"], timeout=60)
        blob.raise_for_status()
        dest.write_bytes(blob.content)
        manifest[key] = {"id": match["id"], "url": match["url"],
                         "auteur": match.get("photographer"), "alt": match.get("alt")}
        print(f"  [dl] {key}.jpg — {match.get('photographer')}")

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


# --- Voix ---------------------------------------------------------------------

def tts(text, voice_id, settings, dest):
    """Un segment parlé. Le fichier existant n'est jamais régénéré (= jamais refacturé)."""
    if dest.exists():
        return dest
    r = requests.post(
        TTS_URL.format(voice_id=voice_id),
        params={"output_format": ELEVENLABS_CONFIG["output_format"]},
        headers={"xi-api-key": ENV["ELEVENLABS_API_KEY"]},
        json={"text": text, "model_id": ELEVENLABS_CONFIG["model_id"],
              "voice_settings": settings},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs {r.status_code} : {r.text[:300]}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    return dest


def to_wav(src, dest):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-ac", "1", "-ar", str(SAMPLE_RATE), str(dest)])
    return dest


def silence_wav(seconds, dest):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
         "-t", f"{seconds:.4f}", str(dest)])
    return dest


def pcm_duration(path):
    """Durée exacte, mesurée en décodant — ffprobe est absent de cette machine.

    On ne déduit PAS la durée de la taille du fichier moins 44 octets : ffmpeg
    n'écrit pas toujours un en-tête WAV canonique (chunk LIST/INFO en plus).
    """
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
               "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "-"]).stdout
    return len(raw) / (SAMPLE_RATE * 2)


def build_voice_track(version, work):
    """Concatène les segments parlés et retourne (wav, spans par segment)."""
    speakers = SPEAKERS[version]
    parts, spans, cursor = [], [], 0.0
    previous_speaker = None

    for i, seg in enumerate(SEGMENTS):
        speaker = speakers[seg["role"]]
        if previous_speaker is not None:
            gap = GAP_SPEAKER_CHANGE if speaker != previous_speaker else GAP_SAME_SPEAKER
            sil = silence_wav(gap, work / f"{version}_sil_{i}.wav")
            parts.append(sil)
            cursor += gap

        mp3 = VOICE_DIR / version / f"{i}_{seg['role']}_{speaker}.mp3"
        tts(seg.get("texte_dit", seg["texte"]),
            VOICE_CURIO if speaker == "curio" else VOICE_NARRATEUR,
            SETTINGS_CURIO if speaker == "curio" else SETTINGS_NARRATEUR,
            mp3)
        wav = to_wav(mp3, work / f"{version}_seg_{i}.wav")
        duration = pcm_duration(wav)
        parts.append(wav)
        spans.append({"role": seg["role"], "speaker": speaker,
                      "start": cursor, "end": cursor + duration})
        cursor += duration
        previous_speaker = speaker

    parts.append(silence_wav(TAIL, work / f"{version}_tail.wav"))
    cursor += TAIL

    listfile = work / f"{version}_concat.txt"
    listfile.write_text("".join(f"file '{p}'\n" for p in parts))
    track = work / f"{version}_voix.wav"
    # Ré-encodage PCM plutôt que -c copy : un concat de WAV en copie garde dans
    # l'en-tête RIFF la taille du seul premier fichier, et certains lecteurs
    # tronquent la piste sur cette valeur.
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:a", "pcm_s16le", "-ar", str(SAMPLE_RATE), "-ac", "1", str(track)])
    return track, spans, cursor


# --- Sous-titres -------------------------------------------------------------

def _srt_seconds(stamp):
    hh, mm, rest = stamp.split(":")
    ss, ms = rest.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000


def _srt_stamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _parse_srt(text):
    blocks = []
    for raw in text.strip().split("\n\n"):
        lines = [l for l in raw.strip().splitlines() if l.strip()]
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        start, end = (t.strip() for t in lines[1].split("-->"))
        blocks.append((_srt_seconds(start), _srt_seconds(end), "\n".join(lines[2:])))
    return blocks


def subtitles_by_segment(version, spans):
    """Transcrit CHAQUE segment séparément, puis décale les timestamps.

    Un seul passage Whisper sur la piste entière donnait un résultat inutilisable :
    `initial_prompt` doit recevoir un indice court, pas la narration complète. Avec
    tout le script en prompt, Whisper recrache le texte du prompt et perd
    l'alignement — version full_curio sans aucun sous-titre avant 18,7s, version
    narrateur avec un bloc unique de 10,8s et des phrases inventées.

    Segment par segment, chaque passage ne reçoit que SON texte comme indice et ne
    peut pas dériver au-delà de sa propre durée. Bonus : l'attribution du locuteur
    devient exacte, elle ne dépend plus d'un recoupement de timestamps.
    """
    entries = []
    for i, (seg, span) in enumerate(zip(SEGMENTS, spans)):
        seg_dir = WORKSPACE / "srt" / version / f"{i}_{seg['role']}"
        seg_dir.mkdir(parents=True, exist_ok=True)
        mp3 = VOICE_DIR / version / f"{i}_{seg['role']}_{span['speaker']}.mp3"
        srt_path = generate_subtitles(mp3, seg_dir, initial_prompt=seg.get("texte_dit", seg["texte"]))
        for start, end, text in _parse_srt(srt_path.read_text()):
            entries.append((start + span["start"], end + span["start"], text))

    return "\n".join(
        f"{i}\n{_srt_stamp(a)} --> {_srt_stamp(b)}\n{t}\n"
        for i, (a, b, t) in enumerate(entries, start=1)
    )


# --- Pistes image par image ---------------------------------------------------

def voice_levels(wav_path, n_frames, curio_windows):
    """Niveau de voix de CURIO par image, 0 → 1.

    Hors des fenêtres où Curio parle, le niveau est forcé à zéro : sa lumière ne
    doit jamais réagir à la voix du narrateur.
    """
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(wav_path),
               "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "-"]).stdout
    pcm = array.array("h")
    pcm.frombytes(raw[: len(raw) - len(raw) % 2])

    per_frame = SAMPLE_RATE // VIDEO_FPS
    rms = []
    for i in range(n_frames):
        chunk = pcm[i * per_frame:(i + 1) * per_frame]
        rms.append(math.sqrt(sum(s * s for s in chunk) / len(chunk)) if chunk else 0.0)

    ordered = sorted(v for v in rms if v > 0)
    ref = ordered[int(len(ordered) * 0.95)] if ordered else 1.0
    levels, prev = [], 0.0
    for i, v in enumerate(rms):
        t = i / VIDEO_FPS
        speaking = any(a <= t < b for a, b in curio_windows)
        target = min(v / ref, 1.0) if speaking else 0.0
        prev += (target - prev) * (ATTACK if target > prev else RELEASE)
        levels.append(round(prev, 4))
    return levels


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _smooth_binary(raw, blend_frames):
    """Adoucit une piste en marches d'escalier : chaque changement devient une
    rampe smoothstep centrée sur la frontière. Les segments font tous plus de
    3s, aucune rampe n'en chevauche une autre."""
    out = list(raw)
    n = len(raw)
    half = blend_frames / 2
    for f in range(1, n):
        if raw[f] == raw[f - 1]:
            continue
        a, b = raw[f - 1], raw[f]
        for j in range(max(0, int(f - half)), min(n - 1, int(f + half)) + 1):
            p = smoothstep((j - (f - half)) / blend_frames)
            out[j] = round(a + (b - a) * p, 4)
    return out


def avatar_tracks(version, spans, n_frames):
    """bigness (grand ↔ pastille) et presence (visible ↔ absent), image par image."""
    states = AVATAR[version]

    per_frame_state = []
    for i in range(n_frames):
        t = i / VIDEO_FPS
        span = next((s for s in spans if s["start"] <= t < s["end"]), None)
        if span is None:
            span = spans[-1] if t >= spans[-1]["end"] else spans[0]
        per_frame_state.append(states[span["role"]])

    presence_raw = [0.0 if st == "none" else 1.0 for st in per_frame_state]

    # Pendant un passage "none", la TAILLE conserve celle de l'état visible le
    # plus proche (le suivant en priorité) : Curio réapparaît directement à la
    # bonne place au lieu de traverser l'écran en même temps qu'il s'affiche.
    big_raw = [None if st == "none" else (1.0 if st == "big" else 0.0)
               for st in per_frame_state]
    for i in range(n_frames):
        if big_raw[i] is not None:
            continue
        nxt = next((big_raw[j] for j in range(i, n_frames) if big_raw[j] is not None), None)
        prv = next((big_raw[j] for j in range(i, -1, -1) if big_raw[j] is not None), None)
        big_raw[i] = nxt if nxt is not None else (prv if prv is not None else 0.0)

    blend = STATE_BLEND_S * VIDEO_FPS
    return _smooth_binary(big_raw, blend), _smooth_binary(presence_raw, blend)


def scene_plan(spans, n_frames):
    """Une scène par segment, bornée sur les frontières réelles de la voix."""
    scenes = []
    for i, (seg, span) in enumerate(zip(SEGMENTS, spans)):
        start = round(span["start"] * VIDEO_FPS)
        end = round(spans[i + 1]["start"] * VIDEO_FPS) if i + 1 < len(spans) else n_frames
        scenes.append({"start": start, "duration": max(1, end - start),
                       "src": f"curio-reel/{seg['photo']}.jpg",
                       "motion": seg["motion"], "label": seg["label"]})
    return scenes


# --- Rendu --------------------------------------------------------------------

def stage_public_assets():
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)
    shutil.copyfile(CURIO_CUTOUT, PUBLIC_DIR / "curio_flat.png")
    for key in PHOTO_QUERIES:
        shutil.copyfile(PHOTO_DIR / f"{key}.jpg", PUBLIC_DIR / f"{key}.jpg")


def render(version, props, voice_track, work):
    props_path = work / f"props_{version}.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False))
    silent = work / f"reel_{version}.mp4"
    run(["npx", "remotion", "render", "src/index.experiments.ts", "CurioReel",
         str(silent), f"--props={props_path}", "--muted", "--log=error"], cwd=REMOTION_DIR)

    final = WORKSPACE / f"reel_lacs_roses_{version}.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(silent), "-i", str(voice_track),
         "-map", "0:v", "-map", "1:a", "-shortest",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    return final


def narrator_samples(work):
    """Échantillon comparatif des deux voix de narrateur candidates."""
    out = WORKSPACE / "narrateur_candidats"
    out.mkdir(parents=True, exist_ok=True)
    for name, voice_id in NARRATOR_CANDIDATES.items():
        dest = out / f"narrateur_{name}.mp3"
        tts(NARRATOR_SAMPLE, voice_id, SETTINGS_NARRATEUR, dest)
    return out


def build(version, work):
    print(f"\n=== version {version} ===")
    print("  [1/5] voix par segment (ElevenLabs, mise en cache)")
    voice_track, spans, total_s = build_voice_track(version, work)
    n_frames = round(total_s * VIDEO_FPS)
    for s in spans:
        print(f"        {s['role']:16s} {s['speaker']:10s} {s['start']:6.2f} → {s['end']:6.2f}s")
    print(f"        durée totale {total_s:.2f}s ({n_frames} images)")

    print("  [2/5] sous-titres (Whisper local, un passage par segment)")
    srt_text = subtitles_by_segment(version, spans)

    print("  [3/5] enveloppe de la voix de Curio")
    curio_windows = [(s["start"], s["end"]) for s in spans if s["speaker"] == "curio"]
    levels = voice_levels(voice_track, n_frames, curio_windows)

    print("  [4/5] présence et taille de Curio")
    bigness, presence = avatar_tracks(version, spans, n_frames)

    props = {
        "curioSrc": "curio-reel/curio_flat.png",
        "scenes": scene_plan(spans, n_frames),
        "levels": levels,
        "bigness": bigness,
        "presence": presence,
        "speakerSpans": [{"startMs": round(s["start"] * 1000),
                          "endMs": round(s["end"] * 1000),
                          "speaker": s["speaker"]} for s in spans],
        "srtText": srt_text,
        "captions": [],
        "totalFrames": n_frames,
    }

    print("  [5/5] rendu Remotion + audio")
    return render(version, props, voice_track, work)


def main():
    if not CURIO_CUTOUT.exists():
        sys.exit(f"introuvable : {CURIO_CUTOUT}")
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="curio_reel_"))
    print(f"[work] {work}")

    print("[photos] Pexels, pleine résolution")
    manifest = resolve_photos()

    print("[voix narrateur] échantillon comparatif des candidats")
    samples = narrator_samples(work)

    stage_public_assets()
    finals = []
    try:
        for version in ("full_curio", "narrateur"):
            finals.append(build(version, work))
    finally:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)

    shutil.rmtree(work, ignore_errors=True)
    print("\nCrédits photos (Pexels) :")
    for key, meta in manifest.items():
        print(f"  {key:14s} {meta['auteur']} — {meta['url']}")
    print(f"\nÉchantillons voix narrateur : {samples}")
    for f in finals:
        print(f"✅ {f}")


if __name__ == "__main__":
    main()
