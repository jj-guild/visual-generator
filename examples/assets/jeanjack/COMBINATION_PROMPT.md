# JeanJack — Prompts de combinaison avatar (doctrine d'assemblage)

## Éléments (générés une fois, jamais retouchés au pixel)
- `jeanjack_character_E3_full.png` — personnage complet E3 sans baguette, fond transparent (interstices casque et bras nets)
- `jeanjack_background_LAN.png` — fond LAN grenier validé (lan_a), crop carré 896, GaussianBlur(5), aucune correction colorimétrique
- `baguette_tip3.png` — pointe de baguette katana, transparente (uniquement pour la variante AVEC)

## Cadrage commun (règles de session validées)
Canvas : carré 896×896, PNG < 1 Mo.
1. Découpe : rembg isnet-general-use + alpha matting (foreground 230, background 15, erode 8) — préserver bras fins et interstices du casque. Vérif numérique : trous internes ~20k px, segments multiples (bras séparés du torse).
2. Plaque "JeanJack" : blob doré (R>110, G>80, B<210, G<R+20), lettres 20-40px de large → noter `plate_bottom` et `cx` (centre de la plaque).
3. Échelle : `r = (0.70 × 896) / plate_bottom` (distance casque-haut → bas de plaque = 70% de la hauteur).
4. Position : `py = 0.15 × 896` (15% libre au-dessus du casque) ; `px = 896/2 − cx × r` (centrage sur la plaque — les bras n'entrent PAS dans le calcul).
5. Corps coupé NET par le bord bas (alpha jusqu'à y=895, zéro écart) ; ~15% de corps visible sous la plaque.
6. Largeur occupée ~70% (règle soft : les bras peuvent déborder ; ~15-25% de fond visible de chaque côté).
7. Export : PNG optimize=True, vérifier < 1 Mo.

---

## PROMPT 1 — Avatar SANS baguette
Composition à 2 couches, dans cet ordre :
1. Couche fond : `jeanjack_background_LAN.png` (896×896).
2. Couche personnage : cutout E3 cadré selon les règles communes ci-dessus.
Rien d'autre. Aucun élément ajouté.

## PROMPT 2 — Avatar AVEC katanaguette
Composition à 3 couches, dans cet ordre :
1. Couche fond : `jeanjack_background_LAN.png` (896×896).
2. Couche katanaguette : `baguette_tip3.png`, redimensionnée à ~16% de la hauteur du canvas (≈139×143 px), positionnée par grid-search derrière l'épaule avec les contraintes :
   - chevauchement majoritairement caché par la silhouette (overlap ≥ 72%) ;
   - fraction visible très faible : 0.18 ≤ visible ≤ 0.30 (cible 0.24) — la pointe ne dépasse presque pas ;
   - contact obligatoire avec la silhouette (pas de baguette flottante) ;
   - sommet de la pointe JAMAIS plus haut que le haut du casque.
3. Couche personnage : cutout E3 cadré selon les règles communes, par-dessus.

## Interdits (doctrine, non négociable)
- Aucun edit_image sur une génération pour corriger un défaut → régénérer.
- Aucune post-prod pixel (inpainting, clone, fondu, déplacement d'élément du rendu).
- Aucune correction colorimétrique du fond (brut + blur 5 uniquement).
- Ne jamais modifier le personnage après découpe (hors scale/crop/position).
- Si un critère QA échoue : on ne livre pas, on recommence.

## QA avant livraison
- Zoom casque : interstices transparents, pas de fond résiduel, pas de halo.
- Zoom plaque : "JeanJack" lisible (vérif OCR), bas de plaque ≈ 85% de la hauteur.
- Numérique : alpha top ≈ 15% de hauteur ; alpha jusqu'au bord bas (y=895) ; segments multiples (bras présents, séparés).
- Variante katanaguette : zoom épaule — pointe à peine visible, intégrée, sans halo ; sommet sous le casque.
- Taille : tous les PNG < 1 Mo.
