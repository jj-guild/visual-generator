# Prompt — avatar JeanJack (fond LAN + flou + personnage)

Combine `raw_bg_LAN.png` et `raw_JeanJack.png` en `avatar_JeanJack.png`
avec le pipeline du repo (skill `avatar`) :

```bash
# 1. fond : crop carré + flou (aucune correction colorimétrique)
python tools/make_avatar.py bg \
    --src examples/assets/scenes/lan/raw_bg_LAN.png \
    --out examples/assets/scenes/lan/bg_LAN_blurry.png --blur 5

# 2. cutout : personnage transparent (rembg, matting doux —
#    préserve les bras fins et les interstices du casque)
python tools/make_avatar.py cutout \
    --src examples/assets/personnages/jeanjack/raw_JeanJack.png \
    --out examples/assets/personnages/jeanjack/cutout_JeanJack.png

# 3. avatar : composition pilotée par l'ancre (auto-détection sur la
#    plaque dorée), taille bornée, fail-closed
python tools/make_avatar.py compose \
    --bg examples/assets/scenes/lan/bg_LAN_blurry.png \
    --character examples/assets/personnages/jeanjack/cutout_JeanJack.png \
    --out examples/avatars/avatar_JeanJack.png
```

## Règles de cadrage (défauts du CLI = règles de session)

| Règle | Valeur |
|---|---|
| Espace libre au-dessus du casque | 15% (`--headroom 0.15`) |
| Bas de la plaque "JeanJack" | 85% de la hauteur (`--plate-bottom 0.85`) |
| Centrage | sur la plaque (l'ancre), jamais sur les bras |
| Bord bas | corps coupé net, aucun écart de pixels |
| Canvas | carré 896 px (`--size 896`) |
| Taille fichier | PNG < 1 Mo (`--max-kb 1024`, fail-closed) |

## Doctrine

- Chaque élément est généré une fois, jamais édité ni retouché.
- Seules transformations permises : crop, scale, position, flou.
- Si un critère échoue (cutout raté, ancre perdue, taille dépassée) :
  régénérer l'élément, ne jamais corriger au pixel.
- Utiliser uniquement `raw_JeanJack.png` comme personnage de référence
  (render validé, image d'origine comme source d'identité).
