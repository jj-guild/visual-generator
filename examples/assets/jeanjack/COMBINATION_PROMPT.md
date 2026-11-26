# JeanJack — Prompt de combinaison avatar (doctrine d'assemblage)

## Éléments (tous générés une fois, jamais retouchés au pixel)
- `jeanjack_character_E3_full.png` — personnage complet E3 sans baguette, fond transparent (interstices casque et bras nets)
- `jeanjack_background_LAN.png` — fond LAN grenier validé (lan_a), crop carré 896, GaussianBlur(5), aucune correction colorimétrique
- (option) `baguette_tip3.png` — pointe de baguette katana, transparente, à intercaler ENTRE le fond et le personnage

## Règles de cadrage (session validée)
Canvas : carré 896×896, PNG < 1 Mo.
1. Découpe du personnage : rembg isnet-general-use + alpha matting (foreground 230, background 15, erode 8) — préserver bras fins et interstices du casque.
2. Détecter la plaque "JeanJack" (blob doré : R>110, G>80, B<210, G<R+20 ; lettres larges 20-40px ; bande y). Noter `plate_bottom` et `cx` (centre de la plaque).
3. Échelle : `r = (0.70 × SIZE) / plate_bottom` (SIZE=896) — distance casque-haut → bas de plaque = 70% de la hauteur.
4. Position : `py = 0.15 × SIZE` (15% libre au-dessus du casque) ; `px = SIZE/2 − cx × r` (centrage sur la plaque, les bras n'entrent PAS dans le calcul).
5. Le bas du corps doit être coupé NET par le bord bas du cadre (alpha jusqu'à y=895) ; ~15% de corps visible sous la plaque.
6. Largeur occupée ~70% (règle soft : les bras peuvent déborder, ~15-25% de fond visible de chaque côté).
7. Ordre de composition : fond → (baguette optionnelle, pointe jamais plus haute que le haut du casque, ~30-45% visible, plaquée contre la silhouette) → personnage.
8. Baguette katana : assemblée par grid-search — maximiser contact avec la silhouette (overlap 40-60%), fraction visible 0.38-0.48, sommet sous le haut du casque.
9. Export : PNG optimize=True ; vérifier < 1 Mo.

## Interdits
- Aucun edit sur une génération (edit_image) pour corriger un défaut → régénérer.
- Aucune post-prod pixel (inpainting, clone, fondu, déplacement d'élément du rendu).
- Aucune correction colorimétrique du fond (brut + blur 5 uniquement).
- Ne jamais modifier le personnage après découpe (hors scale/crop/position).

## QA avant livraison
- Zoom casque : interstices transparents, pas de fond résiduel, pas de halo.
- Zoom plaque : "JeanJack" lisible (vérif OCR).
- Numérique : alpha top ≈ 15% de hauteur, bas de plaque ≈ 85%, alpha jusqu'au bord bas (pas d'écart de pixels).
- Segment analysis : bras présents, séparés du torse (segments multiples), pas de baguette si version sans.
