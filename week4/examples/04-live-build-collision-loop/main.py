import pygame

from live_build_collision_loop.game import Game


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Week 4 — Live Build Collision Loop")

    clock = pygame.time.Clock()
    running = True

    game = Game()

    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
