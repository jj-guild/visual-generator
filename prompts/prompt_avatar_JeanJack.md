# Prompt — avatar JeanJack (fond LAN + flou + personnage)

Combine `raw_bg_LAN.png` et `raw_JeanJack.png` en `avatar_JeanJack.png`
avec le pipeline du repo (skill `avatar`) :

```bash
# 1. fond : crop carré + flou (la scène validée est naturellement
#    lumineuse : aucune correction de luminosité nécessaire ;
#    --brightness n'est autorisé QUE sur demande explicite utilisateur)
python tools/make_avatar.py bg \
    --src examples/assets/scenes/lan/raw_bg_LAN.png \
    --out examples/assets/scenes/lan/bg_LAN_blurry.png --blur 4

# 2. cutout : personnage transparent (rembg, matting doux —
#    préserve les bras fins et les interstices du casque)
python tools/make_avatar.py cutout \
    --src examples/assets/personnages/jeanjack/raw_JeanJack.png \
    --out examples/assets/personnages/jeanjack/cutout_JeanJack.png

# 3. avatar : composition pilotée par l'ancre (auto-détection sur la
#    plaque dorée), fail-closed.
#    --dx 20 : le personnage est posé de biais, l'ancre décalée à
#    droite du nez impose un léger décalage vers la droite pour un
#    centrage visuel correct.
#    --max-kb 976 : contrainte de CE cas-ci (< 1 Mo, soit 999 424
#    octets) — la borne n'est pas universelle, elle se demande au
#    cas par cas. PNG d'abord ; si le PNG dépasse, repli JPEG
#    (qualité 92→70) sans postérisation.
python tools/make_avatar.py compose \
    --bg examples/assets/scenes/lan/bg_LAN_blurry.png \
    --character examples/assets/personnages/jeanjack/cutout_JeanJack.png \
    --out examples/avatars/avatar_JeanJack.png --dx 20 --max-kb 976
```

## Paramètres retenus (validation utilisateur)

| Paramètre | Valeur | Raison |
|---|---|---|
| `--blur` | 4 | le fond reste lisible comme LAN mais détache le personnage ; en dessous, l'avatar dépasse 1 Mo en RGB |
| `--dx` | 20 | centrage visuel du personnage posé de biais |
| `--brightness` | (aucun) | la scène validée est lumineuse nativement (lum ~72 après flou) |
| `--max-kb` | 976 | borne < 1 Mo de ce cas (contrainte par cas, pas un défaut) |

Avec blur 4 le PNG RGB fait ≈ 1,04 Mo : il dépasse la borne, le
pipeline produit donc un JPEG qualité 92 (≈ 140 Ko) — gradients
propres, aucun artifact visible, JeanJack intact.
