import type { Caption } from "@remotion/captions";

// Le subtitles.srt produit par le pipeline Python (generators/subtitle_generator.py)
// regroupe déjà les mots Whisper en blocs de phrase (1 sous-titre = 1 phrase/morceau,
// jusqu'à 2 lignes) : les timestamps mot à mot d'origine sont lus puis jetés
// (json.unlink() dans subtitle_generator.py) et ne sont donc pas disponibles ici.
// En attendant que le pipeline les persiste, on répartit la durée de chaque bloc
// entre ses mots au prorata de leur longueur — une approximation, pas les vrais
// timestamps Whisper. À remplacer par un vrai parsing mot à mot le jour où
// subtitle_generator.py exporte ces timestamps.
export const approximateWordCaptions = (phraseCaptions: Caption[]): Caption[] => {
  const words: Caption[] = [];

  for (const phrase of phraseCaptions) {
    const tokens = phrase.text.split(/\s+/).filter(Boolean);
    if (tokens.length === 0) continue;

    const totalChars = tokens.reduce((sum, t) => sum + t.length, 0);
    const durationMs = phrase.endMs - phrase.startMs;
    let cursor = phrase.startMs;

    tokens.forEach((token, i) => {
      const isLast = i === tokens.length - 1;
      const share = token.length / totalChars;
      const endMs = isLast ? phrase.endMs : cursor + durationMs * share;

      words.push({
        text: token,
        startMs: cursor,
        endMs,
        timestampMs: (cursor + endMs) / 2,
        confidence: null,
      });

      cursor = endMs;
    });
  }

  return words;
};

// Regroupe des mots (Caption[] déjà unitaires) en lignes de ≤ maxCharsPerLine
// caractères, en évitant de laisser un mot orphelin seul sur la dernière ligne
// (même heuristique que l'algorithme d'origine de @remotion/captions, réimplémentée
// ici pour ne pas dépendre de CaptionsInternals.ensureMaxCharactersPerLine — non
// exporté publiquement par le package, donc pas une API stable).
export const groupWordsIntoLines = (words: Caption[], maxCharsPerLine: number): Caption[][] => {
  const lines: Caption[][] = [];
  let current: Caption[] = [];

  words.forEach((word, i) => {
    const remaining = words.length - i - 1;
    const filledChars = current.reduce((sum, w) => sum + w.text.length + 1, 0);
    const preventOrphan = remaining > 1 && remaining < 4 && filledChars > maxCharsPerLine / 2;

    if (current.length > 0 && (filledChars + word.text.length > maxCharsPerLine || preventOrphan)) {
      lines.push(current);
      current = [];
    }
    current.push(word);
  });

  if (current.length > 0) {
    lines.push(current);
  }

  return lines;
};
