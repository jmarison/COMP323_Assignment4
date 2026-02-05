# Week 4 — Live Build Collision Loop (Completed)

A small **collision-driven game loop** that matches the Week 4 guided-build slides:

- player movement + bounds
- coin pickups → score
- hazards → damage
- i-frames (anti-spam guard)
- win/lose rule
- one feedback cue (hit flash + tiny shake)

## Run

```bash
python3 -m pip install pygame
python3 main.py
```

## Controls

- Move: WASD / Arrow keys
- Debug overlay: F1
- Restart: R
- Quit: Esc

## Rules

- Collect **10 coins** to win.
- Touch hazards to take damage.
- You have **3 HP**.
- After taking damage you get short **i-frames** so you don’t lose all HP in one overlap.
