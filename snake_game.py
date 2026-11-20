"""
╔══════════════════════════════════════════════╗
║          NEON SNAKE  — High-Graphics         ║
║  Requires: pip install pygame                ║
║  Run:      python snake_game.py              ║
╚══════════════════════════════════════════════╝

Controls:
  Arrow keys / WASD  — Move
  P                  — Pause
  R                  — Restart (game-over screen)
  ESC                — Quit
"""

import pygame
import random
import math
import sys
import time

# ─── Constants ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 700
GRID_SIZE     = 28          # pixels per cell
COLS          = WIDTH  // GRID_SIZE
ROWS          = (HEIGHT - 80) // GRID_SIZE   # top 80 px = HUD
HUD_H         = 80
GAME_TOP      = HUD_H

FPS           = 12          # base snake speed (frames/move)
SPEED_INC     = 0.15        # speed increase per food eaten

# Neon colour palette
C_BG          = (5,   5,  18)
C_GRID        = (18,  18,  42)
C_SNAKE_HEAD  = (0,  255, 180)
C_SNAKE_BODY  = (0,  200, 120)
C_SNAKE_TAIL  = (0,  130,  80)
C_FOOD        = (255,  50,  80)
C_FOOD_GLOW   = (255, 130, 110)
C_SCORE       = (220, 220, 255)
C_WHITE       = (255, 255, 255)
C_GOLD        = (255, 215,   0)
C_PAUSE       = (100, 100, 200)
C_DEAD        = (255,  60,  60)


# ─── Helpers ────────────────────────────────────────────────────────────────
def cell_rect(col, row):
    """Return pygame.Rect for a grid cell (accounting for HUD)."""
    return pygame.Rect(col * GRID_SIZE, GAME_TOP + row * GRID_SIZE,
                       GRID_SIZE, GRID_SIZE)

def glow_surf(radius, colour, alpha=160):
    """Return a radial-gradient surface for glow effects."""
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        a = int(alpha * (1 - r / radius) ** 1.5)
        pygame.draw.circle(s, (*colour, a), (radius, radius), r)
    return s


# ─── Particle ───────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, colour):
        self.x  = x
        self.y  = y
        ang     = random.uniform(0, math.tau)
        spd     = random.uniform(1.5, 5.0)
        self.vx = math.cos(ang) * spd
        self.vy = math.sin(ang) * spd
        self.life    = random.randint(25, 55)
        self.max_life = self.life
        self.r  = random.randint(3, 7)
        self.colour = colour

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.vy   += 0.15     # gravity
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.colour, alpha), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ─── Snake ───────────────────────────────────────────────────────────────────
class Snake:
    def __init__(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.pending   = (1, 0)
        self.grow      = 0

    def set_dir(self, d):
        # Prevent 180° reversal
        if (d[0] != -self.direction[0]) or (d[1] != -self.direction[1]):
            self.pending = d

    def move(self):
        self.direction = self.pending
        hx, hy = self.body[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]

        # Wall wrap
        nx %= COLS
        ny %= ROWS

        self.body.insert(0, (nx, ny))
        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()

    def head(self):
        return self.body[0]

    def collides_self(self):
        return self.body[0] in self.body[1:]

    def draw(self, surf, tick):
        n = len(self.body)
        _glow = glow_surf(GRID_SIZE, C_SNAKE_HEAD, 120)

        for i, (col, row) in enumerate(self.body):
            t   = i / max(n - 1, 1)
            # Interpolate colour head → tail
            r   = int(C_SNAKE_HEAD[0] * (1 - t) + C_SNAKE_TAIL[0] * t)
            g   = int(C_SNAKE_HEAD[1] * (1 - t) + C_SNAKE_TAIL[1] * t)
            b   = int(C_SNAKE_HEAD[2] * (1 - t) + C_SNAKE_TAIL[2] * t)
            colour = (r, g, b)

            rect  = cell_rect(col, row)
            inset = 2
            inner = rect.inflate(-inset * 2, -inset * 2)

            # Rounded body segment
            pygame.draw.rect(surf, colour, inner, border_radius=6)

            # Head glow + eyes
            if i == 0:
                surf.blit(_glow,
                          (rect.centerx - GRID_SIZE, rect.centery - GRID_SIZE))
                self._draw_eyes(surf, rect, tick)

    def _draw_eyes(self, surf, rect, tick):
        dx, dy = self.direction
        # Rotate eye positions with direction
        eye_offsets = {
            ( 1,  0): [(-2, -5), (-2,  5)],
            (-1,  0): [(-2, -5), (-2,  5)],
            ( 0, -1): [(-5, -2), ( 5, -2)],
            ( 0,  1): [(-5,  2), ( 5,  2)],
        }
        offsets = eye_offsets.get((dx, dy), [(-2, -5), (-2, 5)])
        for ox, oy in offsets:
            cx = rect.centerx + dx * 4 + ox
            cy = rect.centery + dy * 4 + oy
            pygame.draw.circle(surf, C_WHITE,   (cx, cy), 4)
            pygame.draw.circle(surf, (10, 10, 30), (cx + dx, cy + dy), 2)


# ─── Food ───────────────────────────────────────────────────────────────────
class Food:
    def __init__(self, snake_body):
        self.pos   = self._spawn(snake_body)
        self.pulse = 0.0

    def _spawn(self, snake_body):
        occupied = set(snake_body)
        while True:
            p = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if p not in occupied:
                return p

    def respawn(self, snake_body):
        self.pos = self._spawn(snake_body)

    def draw(self, surf, tick):
        self.pulse = (self.pulse + 0.12) % math.tau
        scale = 1.0 + 0.12 * math.sin(self.pulse)
        col, row = self.pos
        rect  = cell_rect(col, row)
        r     = int(GRID_SIZE * 0.38 * scale)

        # Outer glow
        glow_r = int(GRID_SIZE * 0.9 * scale)
        _glow  = glow_surf(glow_r, C_FOOD, 110)
        surf.blit(_glow,
                  (rect.centerx - glow_r, rect.centery - glow_r))

        # Apple body
        pygame.draw.circle(surf, C_FOOD, rect.center, r)
        pygame.draw.circle(surf, C_FOOD_GLOW,
                           (rect.centerx - r // 4, rect.centery - r // 4),
                           max(2, r // 3))
        # Stem
        sx, sy = rect.centerx + 2, rect.centery - r
        pygame.draw.line(surf, (80, 200, 80), (sx, sy), (sx + 4, sy - 5), 2)


# ─── Game ───────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🐍  Neon Snake")
        self.screen   = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock    = pygame.time.Clock()

        # Pre-render grid
        self.grid_surf = self._make_grid()

        # Fonts
        self.font_big  = pygame.font.SysFont("consolas", 52, bold=True)
        self.font_med  = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_sm   = pygame.font.SysFont("consolas", 20)

        self.high_score = 0
        self._new_game()

    # ── Init / reset ──────────────────────────────────────────────────────
    def _new_game(self):
        self.snake      = Snake()
        self.food       = Food(self.snake.body)
        self.score      = 0
        self.alive      = True
        self.paused     = False
        self.particles  = []
        self.flash      = 0        # HUD score flash frames
        self.speed      = FPS      # current move interval (frames)
        self.frame_acc  = 0        # frame accumulator for speed
        self.death_time = None

    # ── Grid surface ─────────────────────────────────────────────────────
    def _make_grid(self):
        s = pygame.Surface((WIDTH, HEIGHT - HUD_H))
        s.fill(C_BG)
        for c in range(COLS + 1):
            x = c * GRID_SIZE
            pygame.draw.line(s, C_GRID, (x, 0), (x, HEIGHT - HUD_H))
        for r in range(ROWS + 1):
            y = r * GRID_SIZE
            pygame.draw.line(s, C_GRID, (0, y), (WIDTH, y))
        return s

    # ── Event handling ────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if not self.alive:
                    if event.key in (pygame.K_r, pygame.K_RETURN):
                        self._new_game()
                    return
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    self.paused = not self.paused
                dirs = {
                    pygame.K_UP:    (0, -1), pygame.K_w: (0, -1),
                    pygame.K_DOWN:  (0,  1), pygame.K_s: (0,  1),
                    pygame.K_LEFT:  (-1, 0), pygame.K_a: (-1, 0),
                    pygame.K_RIGHT: ( 1, 0), pygame.K_d: ( 1, 0),
                }
                if event.key in dirs:
                    self.snake.set_dir(dirs[event.key])

    # ── Logic ─────────────────────────────────────────────────────────────
    def _update(self):
        if not self.alive or self.paused:
            return

        self.frame_acc += 1
        if self.frame_acc < self.speed:
            return
        self.frame_acc = 0

        self.snake.move()

        if self.snake.collides_self():
            self.alive = False
            self.death_time = time.time()
            if self.score > self.high_score:
                self.high_score = self.score
            self._explode_snake()
            return

        if self.snake.head() == self.food.pos:
            self.score      += 10
            self.flash       = 20
            self.snake.grow += 4
            self._burst(self.food.pos, C_FOOD, 30)
            self.food.respawn(self.snake.body)
            self.speed = max(4, FPS - self.score * SPEED_INC / 10)

        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def _burst(self, cell, colour, count):
        col, row = cell
        rect = cell_rect(col, row)
        for _ in range(count):
            self.particles.append(
                Particle(rect.centerx, rect.centery, colour))

    def _explode_snake(self):
        for col, row in self.snake.body:
            rect = cell_rect(col, row)
            for _ in range(6):
                self.particles.append(
                    Particle(rect.centerx, rect.centery, C_SNAKE_HEAD))

    # ── Drawing ───────────────────────────────────────────────────────────
    def _draw(self, tick):
        self.screen.fill(C_BG)

        # Grid
        self.screen.blit(self.grid_surf, (0, HUD_H))

        # Particles (behind snake)
        for p in self.particles:
            p.draw(self.screen)

        # Food & snake
        if self.alive:
            self.food.draw(self.screen, tick)
            self.snake.draw(self.screen, tick)
        else:
            # Keep drawing fading particles after death
            pass

        # HUD
        self._draw_hud(tick)

        # Overlays
        if self.paused:
            self._draw_overlay("⏸  PAUSED", C_PAUSE,
                               "Press P or SPACE to resume")
        elif not self.alive:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_hud(self, tick):
        # HUD background
        hud = pygame.Surface((WIDTH, HUD_H), pygame.SRCALPHA)
        hud.fill((10, 10, 30, 220))
        self.screen.blit(hud, (0, 0))

        # Separator line
        pygame.draw.line(self.screen, C_SNAKE_HEAD,
                         (0, HUD_H - 1), (WIDTH, HUD_H - 1), 2)

        # Score
        score_col = C_GOLD if self.flash > 0 else C_SCORE
        if self.flash > 0: self.flash -= 1
        sc = self.font_big.render(f"{self.score:05d}", True, score_col)
        self.screen.blit(sc, (WIDTH // 2 - sc.get_width() // 2, 8))

        # Labels
        lbl = self.font_sm.render("SCORE", True, (120, 120, 180))
        self.screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 62))

        # High score
        hi = self.font_med.render(f"BEST  {self.high_score:05d}", True,
                                  (180, 160, 80))
        self.screen.blit(hi, (WIDTH - hi.get_width() - 20, 22))

        # Length
        ln = self.font_sm.render(
            f"LENGTH  {len(self.snake.body)}", True, (100, 200, 160))
        self.screen.blit(ln, (20, 22))

        # Speed indicator
        spd_pct = int((FPS - self.speed) / FPS * 100)
        sp = self.font_sm.render(f"SPEED  {spd_pct}%", True, (100, 160, 220))
        self.screen.blit(sp, (20, 46))

    def _draw_overlay(self, title, colour, subtitle=""):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        t = self.font_big.render(title, True, colour)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2,
                              HEIGHT // 2 - 40))
        if subtitle:
            s = self.font_sm.render(subtitle, True, C_SCORE)
            self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2,
                                  HEIGHT // 2 + 30))

    def _draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Pulsing "GAME OVER"
        pulse = 1.0 + 0.06 * math.sin(time.time() * 6)
        raw   = self.font_big.render("GAME  OVER", True, C_DEAD)
        w2, h2 = int(raw.get_width() * pulse), int(raw.get_height() * pulse)
        scaled = pygame.transform.smoothscale(raw, (w2, h2))
        self.screen.blit(scaled, (WIDTH // 2 - w2 // 2,
                                  HEIGHT // 2 - h2 // 2 - 40))

        # New best?
        if self.score == self.high_score and self.score > 0:
            nb = self.font_med.render("🏆  NEW HIGH SCORE!", True, C_GOLD)
            self.screen.blit(nb, (WIDTH // 2 - nb.get_width() // 2,
                                   HEIGHT // 2 + 28))

        restart = self.font_sm.render("Press R or ENTER to restart",
                                      True, (180, 180, 220))
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2,
                                    HEIGHT // 2 + 70))

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        tick = 0
        while True:
            self._handle_events()
            self._update()
            self._draw(tick)
            tick += 1
            self.clock.tick(60)   # render at 60 fps; snake moves at `speed`


# ─── Entry ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()