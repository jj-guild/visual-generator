# Prompt — scène LAN (fond d'avatar JeanJack)

Génère la scène brute `raw_bg_LAN.png` avec ce prompt, mot pour mot :

> Amateur photo taken from the middle of a messy LAN party in a wooden
> barn on a bright summer evening, the room well lit by warm light
> streaming through two large dusty roof windows, mixed with the glow
> of many screens — everything clearly visible, no dark corners. A
> dozen gamers sit facing their own monitors oriented in EVERY
> direction: screens turned left, turned right, diagonal, some facing
> the camera, some sideways, some facing away — nothing aligned,
> tables crammed at odd angles, chairs scattered around, cables
> snaking underfoot, PC towers on the floor, empty pizza boxes,
> crushed cans, a couch with someone asleep on it, duvets piled in a
> corner. Chaotic, cluttered, bright and warm, lived-in. No readable
> text, no logos, no lamps. Photorealistic, sharp faces.

## Pourquoi ce prompt (leçons de session)

- **Court et photographique** — les prompts de 600 mots noient le
  modèle : il lâche la plupart des détails et aligne les tables.
  Chaque phrase ci-dessus porte un critère bloquant.
- « taken from the middle » + « facing … in every direction » +
  « odd angles » — évite la perspective en rangées avec allée
  centrale (défaut systématique des « wide shot »).
- « screen glow as the only light, bright and even … no lamps » —
  évite les singularités lumineuses (lampes, glare, hotspots) qui
  gâchent l'avatar final.
- « chaotic, cluttered, lived-in » — le bordel demandé.
- La scène sera **floutée** (GaussianBlur 5) puis recouverte par le
  personnage au centre : les joueurs doivent donc être visibles
  partout autour du centre, aucun couloir vide n'est acceptable.

## Critères bloqués avant d'accepter un run

1. Lumière = glow écran, claire, uniforme, sans lampe ni hotspot.
2. Joueurs orientés différemment, tables de travers, pas de rangées.
3. Joueurs partout, pas d'allée centrale.
4. Aucun humain déformé/dupliqué.
5. Résolution ≥ 1024 px (le raw n'est jamais réduit).
6. Luminance moyenne ≥ 55 (le personnage est brun sombre : fond trop
   sombre = illisible ; les fenêtres éclairent, les hotspots partiront
   au flou). Vérifier aussi l'absence de letterbox (bandes noires du
   générateur) — si présent, le retirer au crop avant tout le reste.
