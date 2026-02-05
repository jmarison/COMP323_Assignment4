# Week 4 Example — Sprites + Collisions

This example supports the Week 4 slides (sprites, groups, hitboxes, and collision responses).

## Learning goals
- Use `pygame.sprite.Sprite` and `pygame.sprite.Group`
- Keep a *hitbox* (`rect`) separate from how you draw
- Detect overlaps and handle *responses* (solid walls, triggers, damage)
- Add basic fairness/feel: feedback bundle + short invincibility frames

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `F1`: toggle debug (hitboxes)
- `R`: reset
- `Esc`: quit

## What to change first
- Make the coin smaller/bigger (hitbox vs art) in `sprites_collisions/game.py`
- Change the arena walls layout
- Try different knockback + i-frame timing
