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
- `Space` : Restart after win/lose
- `Esc`: quit
- `M`: toggle Mute

## What to change first
- Make the coin smaller/bigger (hitbox vs art) in `sprites_collisions/game.py`
- Change the arena walls layout
- Try different knockback + i-frame timing

## What I added
- Redesigned map layout 
- Implemented a locked goal (blue) which only becomes unlocked (green) after collecting all 7 coins
- Toggleable Sound Effects (muted with `M`) on coin pickup, goal unlock, player hit, and game win
- Hazards move both vertically and horizontally
- Win state on reaching unlocked goal
- Gave coin more generous hitbox

## Game Loop
- The player is tasked with collecting all 7 coins and returning back to the goal while avoiding hazards. Hazards reduce player's health upon collision and if they take all health, its a game over. 
