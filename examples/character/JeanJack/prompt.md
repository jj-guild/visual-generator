# Character prompt — JeanJack (raw generation)

Generate `raw.png` for this character. Every rule below was validated
during the jj-guild avatar session; nothing here is arbitrary.

![Original reference](original.png)

## Reference

`original.png` is the identity reference — the generated character
must be recognizably the SAME character (same proportions, same head
shape, same gold nameplate), not a crop of the reference.

## Prompt used (edit of the user's reference, not of a prior
generation)

> Regenerate this exact same robot character as if freshly
> polished. Keep the identity identical: same proportions and
> rounded head shape, glowing round bright eyes, same small subtle
> closed-mouth smirk (no teeth, no nose), same nameplate position on
> the chest, slim three-finger robot hands. Changes: remove the
> baguette and everything held in his hands (empty hands held
> slightly away from the body); the body is polished glossy BLACK
> metal, mirror-like with bright specular highlights, no brown
> tint, catching the light across the whole figure; uniform bright
> soft studio lighting, no dark areas; the gaming headset is matte
> black with an attached matte-black microphone reaching under the
> mouth; the nameplate on the chest is matte black with the name
> "JeanJack" engraved in shiny gold letters; full body visible
> head to feet, standing on a completely flat uniform light-gray
> background. Sharp focus, high detail, no other objects, no
> readable text other than the nameplate.

## Why each constraint (session-validated)

- **polished glossy black, uniform lighting** — the user iterated:
  dark matte brown -> bright glossy brown ("too dark") -> satin
  brown ("less bright than v2") -> polished black, lighter and
  shinier, no brown tint ("he just changed clothes and took a
  shower");
- **flat uniform background** — the crop step depends on it;
- **full body visible** — the pipeline crops, the render must not;
- **empty hands, nothing on the back** — held items (the baguette)
  failed every generation attempt; the user dropped them;
- **no nose** — explicitly rejected by the user;
- **small closed-mouth smirk** — every larger smile rendered creepy;
- **matte black headset + microphone attached to it, ending under
  the mouth** — user-selected color; free-floating or chin-mounted
  microphones appeared repeatedly;
- **matte black nameplate with "JeanJack" in gold letters** —
  user-selected (was a gold plate with gold lettering); the plate
  keeps the gold detection working;
- **no readable text except the nameplate** — the model misspells
  text (verify by OCR on the plate zoom).

## Blocking criteria before accepting a run

1. Recognizably the same character as `original.png` (zoom on the
   face before anything else). Note: on a glossy black body the
   generator renders the eye glow white or pale blue, not amber —
   three attempts with explicit amber wording did not change it;
   the user's original artwork also has white eyes.
2. Full body visible, flat background, empty hands.
3. One microphone only, attached to the headset.
4. No nose, closed-mouth smirk.
5. Bright, uniform lighting — no dark areas, no shadows on the body.
6. Resolution ≥ 1024 px (the raw is never downscaled).
