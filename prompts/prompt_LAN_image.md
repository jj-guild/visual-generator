# Prompt — scène LAN (fond d'avatar JeanJack)

Génère la scène brute `raw_bg_LAN.png` avec ce prompt, mot pour mot :

> Photorealistic candid photo of a packed, messy modern LAN party in a
> windowless garage workshop. Even, bright, neutral ambient light fills
> the space from no visible source — no windows, no lamps, no ceiling
> fixtures in frame, everything clearly lit, warm lived-in tones, no
> dark corners. Around twenty gamers wearing light-colored clothing —
> white, beige, pale grey t-shirts and hoodies — with gaming headsets
> sit crammed at folding tables arranged at mismatched haphazard angles
> filling the room, each player seated directly in front of their own
> modern thin LCD monitor facing them, screens aimed in different
> directions — no rows, no central aisle, the space fully packed.
> Each setup: modern flat-screen monitor, LED-backlit, mechanical
> keyboard, mouse, headset, sleek PC tower. Authentic clutter: tangled
> ethernet cables, power strips, a network switch on a crate, empty
> soda cans, energy drink bottles, pizza boxes, someone in a white
> hoodie asleep in a duvet in a corner, backpacks on chairs. Crowded,
> chaotic, documentary photography, sharp faces, no readable text, no
> logos, no windows, no lamps.

## Pourquoi ce prompt (leçons de session)

- **Lumière ambiante sans source** : l'utilisateur veut une scène
  lumineuse SANS voir fenêtre ni lampe. « even, bright, neutral
  ambient light from no visible source » marche ~1 fois sur 2 ; les
  fenêtres réapparaissent dès qu'on décrit la lumière comme venant
  de l'extérieur. Ne jamais promettre « roof windows ».
- **Vêtements clairs** : le personnage (JeanJack) est brun sombre —
  des joueurs en vêtements clairs détachent les silhouettes et
  renforcent le contraste une fois floutés.
- **Écrans modernes, un par joueur** : « modern thin LCD monitor
  facing them » ; « chunky CRT » génère une ambiance années 90 que
  l'utilisateur a refusée.
- **Court et photographique** : les prompts de 600 mots noient le
  modèle. Chaque phrase porte un critère bloquant.
- **Tables en biais** : « mismatched haphazard angles, no rows, no
  central aisle » limite (sans l'éliminer) le défaut systématique des
  wide-shots alignés. Énumérer des positions concrètes aide parfois.
- La scène sera **floutée** (GaussianBlur 4) puis recouverte par le
  personnage au centre : les joueurs doivent être visibles partout
  autour du centre.

## Critères bloqués avant d'accepter un run

1. Écrans modernes (LCD fins), un écran face à chaque joueur.
2. Aucune fenêtre visible ; luminosité ambiante claire, uniforme.
3. Vêtements clairs pour les joueurs.
4. Joueurs partout, tables désalignées au possible, pas d'allée
   centrale (défaut récurrent du générateur, tolérable s'il est
   discret : le flou final l'atténue).
5. Aucun humain déformé/dupliqué.
6. Résolution ≥ 1024 px (le raw n'est jamais réduit).
7. Luminance moyenne ≥ 55 (le personnage est brun sombre : fond trop
   sombre = illisible). Vérifier aussi l'absence de letterbox (bandes
   noires du générateur) — si présent, régénérer.
