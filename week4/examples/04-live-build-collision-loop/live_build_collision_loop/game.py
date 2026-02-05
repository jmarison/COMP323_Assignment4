from __future__ import annotations

from dataclasses import dataclass, field
import random

import pygame


@dataclass(frozen=True)
class Palette:
    bg: pygame.Color = field(default_factory=lambda: pygame.Color("#1e222a"))
    panel: pygame.Color = field(default_factory=lambda: pygame.Color("#2a303c"))
    text: pygame.Color = field(default_factory=lambda: pygame.Color("#e5e9f0"))
    subtle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3adbf"))

    player: pygame.Color = field(default_factory=lambda: pygame.Color("#88c0d0"))
    coin: pygame.Color = field(default_factory=lambda: pygame.Color("#ebcb8b"))
    hazard: pygame.Color = field(default_factory=lambda: pygame.Color("#bf616a"))


class Player(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color) -> None:
        super().__init__()
        self.rect = pygame.Rect(0, 0, 28, 28)
        self.rect.center = center

        self.visual_size = 38
        self.color = color

        self.speed = 320.0
        self.invincible_for = 0.0
        self.hit_flash_for = 0.0

    @property
    def is_invincible(self) -> bool:
        return self.invincible_for > 0


class Coin(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color) -> None:
        super().__init__()
        self.rect = pygame.Rect(0, 0, 18, 18)
        self.rect.center = center
        self.visual_size = 28
        self.color = color


class Hazard(pygame.sprite.Sprite):
    def __init__(
        self,
        center: tuple[int, int],
        *,
        color: pygame.Color,
        patrol_dx: int = 140,
        speed: float = 180.0,
    ) -> None:
        super().__init__()
        self.rect = pygame.Rect(0, 0, 28, 28)
        self.rect.center = center
        self.color = color

        self.home_x = center[0]
        self.patrol_dx = patrol_dx
        self.speed = speed
        self.direction = 1

    def update(self, dt: float) -> None:
        x = self.rect.centerx + self.direction * self.speed * dt

        if x < self.home_x - self.patrol_dx:
            x = self.home_x - self.patrol_dx
            self.direction = 1
        elif x > self.home_x + self.patrol_dx:
            x = self.home_x + self.patrol_dx
            self.direction = -1

        self.rect.centerx = int(x)


class Game:
    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 56
    PAD = 12

    COINS_TO_WIN = 10

    def __init__(self) -> None:
        self.palette = Palette()

        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 44)

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.playfield = pygame.Rect(
            self.PAD,
            self.HUD_H + self.PAD,
            self.SCREEN_W - 2 * self.PAD,
            self.SCREEN_H - self.HUD_H - 2 * self.PAD,
        )

        self.debug = False
        self.state = "play"  # play | win | lose

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = pygame.sprite.Group()
        self.coins: pygame.sprite.Group[Coin] = pygame.sprite.Group()
        self.hazards: pygame.sprite.Group[Hazard] = pygame.sprite.Group()

        self.player = Player(self.playfield.center, color=self.palette.player)
        self.all_sprites.add(self.player)

        self.score = 0
        self.hp = 3

        self._shake_for = 0.0

        self._spawn_level()

    def _spawn_level(self) -> None:
        self.coins.empty()
        self.hazards.empty()

        rng = random.Random(4)

        def rand_point() -> tuple[int, int]:
            return (
                rng.randint(self.playfield.left + 30, self.playfield.right - 30),
                rng.randint(self.playfield.top + 30, self.playfield.bottom - 30),
            )

        # Hazards
        hz1 = Hazard((self.playfield.centerx + 220, self.playfield.centery - 80), color=self.palette.hazard)
        hz2 = Hazard(
            (self.playfield.centerx - 160, self.playfield.centery + 120),
            color=self.palette.hazard,
            patrol_dx=110,
            speed=220.0,
        )
        self.hazards.add(hz1, hz2)
        self.all_sprites.add(hz1, hz2)

        # Coins
        for _ in range(self.COINS_TO_WIN):
            for __ in range(200):
                c = Coin(rand_point(), color=self.palette.coin)
                if c.rect.colliderect(self.player.rect):
                    continue
                if pygame.sprite.spritecollideany(c, self.hazards):
                    continue
                if pygame.sprite.spritecollideany(c, self.coins):
                    continue

                self.coins.add(c)
                self.all_sprites.add(c)
                break

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_F1:
            self.debug = not self.debug
            return

        if event.key == pygame.K_r:
            self._reset()
            return

    def _reset(self) -> None:
        self.state = "play"
        self.score = 0
        self.hp = 3

        self.player.rect.center = self.playfield.center
        self.player.invincible_for = 0.0
        self.player.hit_flash_for = 0.0

        self._spawn_level()

    def _read_move(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()

        x = 0
        y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += 1

        v = pygame.Vector2(x, y)
        if v.length_squared() > 0:
            v = v.normalize()
        return v

    def _apply_damage(self) -> None:
        if self.player.is_invincible or self.state != "play":
            return

        self.hp -= 1
        self.player.invincible_for = 0.8
        self.player.hit_flash_for = 0.12
        self._shake_for = 0.16

        if self.hp <= 0:
            self.state = "lose"

    def update(self, dt: float) -> None:
        if self._shake_for > 0:
            self._shake_for = max(0.0, self._shake_for - dt)

        if self.player.invincible_for > 0:
            self.player.invincible_for = max(0.0, self.player.invincible_for - dt)

        if self.player.hit_flash_for > 0:
            self.player.hit_flash_for = max(0.0, self.player.hit_flash_for - dt)

        if self.state != "play":
            self.hazards.update(dt)
            return

        move = self._read_move()

        self.player.rect.x += int(round(move.x * self.player.speed * dt))
        self.player.rect.y += int(round(move.y * self.player.speed * dt))
        self.player.rect.clamp_ip(self.playfield)

        # Pickups: coins -> score
        picked = pygame.sprite.spritecollide(self.player, self.coins, dokill=True)
        if picked:
            self.score += len(picked)
            if self.score >= self.COINS_TO_WIN:
                self.state = "win"

        # Hazards: damage
        if pygame.sprite.spritecollide(self.player, self.hazards, dokill=False):
            self._apply_damage()

        self.hazards.update(dt)

    def _camera_offset(self) -> pygame.Vector2:
        if self._shake_for <= 0:
            return pygame.Vector2(0, 0)

        strength = 8.0 * (self._shake_for / 0.16)
        return pygame.Vector2(
            random.uniform(-strength, strength),
            random.uniform(-strength, strength),
        )

    def draw(self) -> None:
        cam = self._camera_offset()

        self.screen.fill(self.palette.bg)

        pygame.draw.rect(self.screen, self.palette.panel, pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H))
        pygame.draw.line(self.screen, pygame.Color("#000000"), (0, self.HUD_H), (self.SCREEN_W, self.HUD_H), 1)

        hud = f"Score: {self.score}/{self.COINS_TO_WIN}    HP: {self.hp}"
        if self.player.is_invincible:
            hud += "    i-frames"
        self.screen.blit(self.font.render(hud, True, self.palette.text), (14, 18))
        self.screen.blit(
            self.font.render("WASD/Arrows move • F1 debug • R restart • Esc quit", True, self.palette.subtle),
            (14, 36),
        )

        # Playfield border
        pygame.draw.rect(self.screen, pygame.Color("#000000"), self.playfield.move(cam), 2)

        # Coins
        for coin in self.coins:
            visual = pygame.Rect(0, 0, coin.visual_size, coin.visual_size)
            visual.center = coin.rect.center
            pygame.draw.circle(self.screen, coin.color, (visual.centerx, visual.centery) + cam, visual.width // 2)
            pygame.draw.circle(
                self.screen,
                pygame.Color("#000000"),
                (visual.centerx, visual.centery) + cam,
                visual.width // 2,
                2,
            )

        # Hazards
        for hazard in self.hazards:
            r = hazard.rect.move(cam)
            pts = [(r.centerx, r.top), (r.right, r.bottom), (r.left, r.bottom)]
            pygame.draw.polygon(self.screen, hazard.color, pts)
            pygame.draw.polygon(self.screen, pygame.Color("#000000"), pts, 2)

        # Player (blink when invincible, flash on hit)
        pr = self.player.rect.move(cam)
        visual = pygame.Rect(0, 0, self.player.visual_size, self.player.visual_size)
        visual.center = pr.center

        player_color = self.player.color
        if self.player.hit_flash_for > 0:
            player_color = pygame.Color("#d08770")
        elif self.player.is_invincible and int(self.player.invincible_for * 18) % 2 == 0:
            player_color = pygame.Color("#d8dee9")

        pygame.draw.circle(self.screen, player_color, visual.center, visual.width // 2)
        pygame.draw.circle(self.screen, pygame.Color("#000000"), visual.center, visual.width // 2, 2)

        if self.debug:
            self._draw_debug(cam)

        if self.state == "win":
            self._draw_center_message("You win!\nPress R to restart", cam)
        elif self.state == "lose":
            self._draw_center_message("You lose\nPress R to restart", cam)

    def _draw_debug(self, cam: pygame.Vector2) -> None:
        pygame.draw.rect(self.screen, pygame.Color("#8fbcbb"), self.player.rect.move(cam), 2)
        for coin in self.coins:
            pygame.draw.rect(self.screen, pygame.Color("#ebcb8b"), coin.rect.move(cam), 2)
        for hazard in self.hazards:
            pygame.draw.rect(self.screen, pygame.Color("#bf616a"), hazard.rect.move(cam), 2)

        self.screen.blit(
            self.font.render("DEBUG: Rect hitboxes (collisions use these)", True, self.palette.text),
            (self.SCREEN_W - 320, 18),
        )

    def _draw_center_message(self, message: str, cam: pygame.Vector2) -> None:
        lines = message.split("\n")
        total_h = len(lines) * 52
        y = self.playfield.centery - total_h // 2

        overlay = pygame.Surface((self.playfield.width, self.playfield.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, self.playfield.topleft + cam)

        for line in lines:
            surf = self.big_font.render(line, True, self.palette.text)
            x = self.playfield.centerx - surf.get_width() // 2
            self.screen.blit(surf, (x, y) + cam)
            y += 52
