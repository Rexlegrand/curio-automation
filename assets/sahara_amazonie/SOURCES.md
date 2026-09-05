# Assets — reel « le Sahara nourrit l'Amazonie »

## Générés (ChatGPT, abonnement personnel de Benjamin — 2026-09-02)

Aucun appel API, aucun crédit consommé par le pipeline.

| Fichier | Format | Usage |
|---|---|---|
| `dune.png` | 941×1672 | plein cadre, beats 1, 2, 3 — ciel libre en haut pour le titre |
| `canopee.png` | 941×1672 | plein cadre, beats 1, 2, 7 |
| `lac_asseche.png` | 941×1672 | plein cadre, beat 7 |
| `sol_riche.png` | 1536×1024 | isolé sur noir, beat 5 — surface de sol à 13 % de la hauteur |
| `sol_pauvre.png` | 1536×1024 | isolé sur noir, beat 5 — surface à 20 %, à recaler de 72 px sur `sol_riche` |
| `camion.png` | 1536×1024 | isolé sur BLANC, beat 4 — le fond noir mangeait tout le châssis au détourage |
| `poussiere.png` | 1672×941 | isolé sur noir, beats 3 et 6, et en liant entre les plans |
| `sable_macro.png` | 1672×941 | isolé sur noir, beat 6 |

## Sources libres (`sources_libres/`)

Tout est en **domaine public** : aucune attribution légalement exigée, mais le
crédit reste dû dans la description Instagram pour un média éducatif.

| Fichier | Source | Licence |
|---|---|---|
| `bodele_tempete_nasa.jpg` (3840×2880) | NASA / Goddard Space Flight Center, MODIS — tempête de poussière sur la dépression du Bodélé. Via Wikimedia Commons, « Dust Storm in the Bodele Depression (14232).jpg » | Domaine public |
| `tchad_modis_nasa.jpg` (3400×2600) | NASA Earth Observatory, MODIS — le Tchad et le lac Tchad. Via Commons, « Chad AMO 2004323 lrg.jpg ». Plan de secours du précédent | Domaine public |
| `diatomees_noaa.jpg` (1796×1180) | NOAA Corps Collection (corp2365) — diatomées au microscope optique. Via Commons, « Diatoms through the microscope.jpg » | Domaine public |

La texture du globe n'est pas dupliquée ici : elle existe déjà dans le repo,
`remotion/public/desert-sel/map_texture_world.jpg` (Blue Marble, 8192×4096),
avec un précédent d'usage géo-aligné dans `remotion/src/desert-sel/MapZoomUyuni.tsx`.

## Réserve — exactitude du beat 6

`diatomees_noaa.jpg` montre des diatomées **vivantes**, bleutées et en suspension.
Le sable du Bodélé, lui, est fait de leurs **frustules fossilisées** — des coques de
silice blanches, vides, dans un sédiment sec. L'image illustre donc la forme, pas
l'état. Le script dit « squelettes d'algues microscopiques ».

Si cette approximation gêne, Commons a des vues au microscope électronique qui
montrent les frustules seules (« Modern diatoms under SEM », 4096×4576) — mais
elles sont en CC BY 4.0, donc l'attribution devient obligatoire dans la
description du reel.
