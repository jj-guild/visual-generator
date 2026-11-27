# Character prompt — JeanJack (raw generation)

Generate `raw.png` for this character. Every rule below was validated
during the jj-guild avatar session; nothing here is arbitrary.

## Reference

`original.png` is the identity reference — the generated character
must be recognizably the SAME character (same proportions, same head
shape, same gold nameplate), not a crop of the reference.

## Prompt used

> Full-body character render of <JeanJack>, a friendly French gamer
> robot: rounded dark-brown metal head and body, glowing round
> yellow eyes, small subtle smirk (mouth closed, no teeth), no nose,
> large gaming headset with an attached microphone reaching under
> the mouth, a small gold nameplate on the chest reading
> "JeanJack", slim three-finger robot hands, arms held slightly away
> from the body, standing straight on a flat uniform light-grey
> background. Consistent soft studio lighting, sharp focus, high
> detail, no other objects, nothing held in the hands, nothing on
> the back.

## Why each constraint (session-validated)

- **flat uniform background** — the crop step depends on it;
- **full body visible** — the pipeline crops, the render must not;
- **empty hands, nothing on the back** — held items (the baguette)
  failed every generation attempt; user dropped them;
- **no nose** — explicitly rejected by the user ("I never asked for
  a nose");
- **small closed-mouth smirk** — every larger smile rendered creepy;
- **microphone attached to the headset, ending under the mouth** —
  free-floating or chin-mounted microphones appeared repeatedly;
- **eyes slightly high, small, round, luminous** — the user tuned
  this for a more human face;
- **arms away from the body** — keeps the thin-limb interstices the
  crop needs;
- **no readable text except the nameplate** — the model misspells
  text.

## Blocking criteria before accepting a run

1. Recognizably the same character as `original.png` (zoom on the
   face before anything else).
2. Full body visible, flat background, empty hands.
3. One microphone only, attached to the headset.
4. No nose, closed-mouth smirk.
5. Resolution ≥ 1024 px (the raw is never downscaled).
