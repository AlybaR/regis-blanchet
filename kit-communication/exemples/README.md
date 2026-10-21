# Exemples remplis — pack de la réunion du 21 octobre 2026

Maquettes HTML rendues en PDF « aplati » (pages en image haute définition, rendu identique dans tous les lecteurs).

| Source | Sortie | Contenu |
| --- | --- | --- |
| `planche-exemples.html` | `output/pdf/03_charte_en_situation_regis_blanchet.pdf` | La charte en situation (6 p.) |
| `posts.html` | `posts-png/*.png` | 9 publications 1080 × 1350 prêtes à l'emploi |
| `reseaux.html` | `output/pdf/04_formats_reseaux_regis_blanchet.pdf` | Instagram / Facebook / LinkedIn, grille, mois type (3 p.) |
| `lettre.html` | `output/pdf/05_lettre_numero_0_regis_blanchet.pdf` + `documents/lettre_regis_blanchet_numero_zero.pdf` | La lettre de Régis Blanchet n°0 (sans logo de groupe) (4 p. A4) |

Règles tenues : aucune image générée ; aucune citation inventée (édito = extraits de la profession de foi) ; faits publics sourcés ; crédits photo dans `photos/CREDITS.md`.

Rendu : Chromium (Playwright) → captures 240 dpi → `img2pdf`. Polices : Cormorant Garamond et Inter (licence OFL, dossier `fonts/`).
