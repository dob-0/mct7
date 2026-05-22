import math
import random

from modes.base import C, Mode


class Eye(Mode):
    NAME = 'EYE'
    ORDER = 22

    def __init__(self):
        self.cache = []
        self.cache_sz = (0, 0)

    def _precompute(self, w, h):
        self.cache_sz = (w, h)
        cx, cy = w / 2.0, h / 2.0
        aspect = 2.2
        scale = min(w, h * aspect)
        self.cache = []
        for y in range(h):
            row = []
            for x in range(w):
                dx = (x - cx) / aspect
                dy = y - cy
                dist = math.sqrt(dx * dx + dy * dy) * aspect / scale
                angle = math.atan2(dy, dx / aspect) if (dx != 0 or dy != 0) else 0.0
                row.append((dist, angle))
            self.cache.append(row)

    def render(self, buf, w, h, t, frame, cfg, pal, syms):
        if self.cache_sz != (w, h):
            self._precompute(w, h)

        audio  = float(cfg.get('audio_level',    0.0) or 0.0)
        peak   = float(cfg.get('audio_peak',     0.0) or 0.0)
        glitch = float(cfg.get('glitch_intensity', 0.3) or 0.3)
        energy = max(0.0, min(1.0, audio * 0.7 + peak * 0.5))

        primary   = C[pal['p']]
        secondary = C[pal['s']]
        accent    = C[pal['a']]
        dark      = C['dim']
        white     = C['white']

        breath = math.sin(t * 0.9) * 0.03 + math.sin(t * 1.7) * 0.015
        pupil  = max(0.04, 0.13 + breath - energy * 0.04)
        iris   = 0.40 + breath * 0.4
        outer  = 0.60
        rot    = t * 0.12

        for y in range(h - 1):
            row = self.cache[y]
            for x in range(w):
                dist, angle = row[x]
                fiber  = math.sin(angle * 14 + rot + dist * 5.0) * 0.5 + 0.5
                ripple = math.sin(dist * 8.0 - t * 2.5) * 0.5 + 0.5

                if dist < pupil * 0.5:
                    buf[y][x] = None

                elif dist < pupil:
                    buf[y][x] = ('░', dark) if random.random() < 0.12 + energy * 0.1 else None

                elif dist < iris * 0.45:
                    v = fiber * 0.6 + ripple * 0.4
                    if v > 0.65:
                        buf[y][x] = (random.choice(['█', '▓']), primary)
                    elif v > 0.35:
                        buf[y][x] = (random.choice(['▓', '▒']), secondary)
                    else:
                        buf[y][x] = (random.choice(['▒', '░']), dark)

                elif dist < iris:
                    if fiber > 0.72 and random.random() < 0.55:
                        buf[y][x] = (random.choice(['│', '╎', '╷', '◈', '▸']), accent)
                    elif fiber > 0.48:
                        col = primary if ripple > 0.5 else secondary
                        buf[y][x] = (random.choice(['▓', '▒', '░']), col)
                    elif fiber > 0.25:
                        buf[y][x] = (random.choice(['░', '▒']), dark)
                    else:
                        buf[y][x] = None

                elif dist < outer:
                    if random.random() < 0.06 + energy * 0.05:
                        buf[y][x] = (random.choice(['░', '·', '─']), dark)
                    else:
                        buf[y][x] = None

                else:
                    buf[y][x] = (random.choice(syms), dark) if random.random() < 0.016 + energy * 0.02 else None

        # Glitch scanlines
        if random.random() < glitch * 0.22:
            gy = random.randint(0, h - 2)
            for x in range(w):
                if random.random() < 0.5:
                    buf[gy][x] = (random.choice(syms), dark if random.random() < 0.6 else primary)

        # Highlight gleam (light reflection on iris)
        gx = int(w * 0.42)
        gy_gleam = int(h * 0.38)
        if 0 <= gx < w and 0 <= gy_gleam < h - 1:
            d, _ = self.cache[gy_gleam][gx]
            if pupil < d < iris:
                buf[gy_gleam][gx] = ('█', white)
                for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = gx + ddx, gy_gleam + ddy
                    if 0 <= nx < w and 0 <= ny < h - 1 and random.random() < 0.6:
                        buf[ny][nx] = ('▓', accent)
