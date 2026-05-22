import math
import random
import re

from modes.base import C, Mode


class Poster(Mode):
    NAME = 'POSTER'
    ORDER = 18

    def _write(self, buf, w, h, x, y, text, col):
        if y < 0 or y >= h:
            return
        for i, ch in enumerate(text[: max(0, w - x)]):
            if ch != ' ':
                self.put(buf, x + i, y, ch, col, w, h)

    def _hline(self, buf, w, h, x0, x1, y, ch, col):
        if y < 0 or y >= h:
            return
        for x in range(max(0, x0), min(w, x1)):
            self.put(buf, x, y, ch, col, w, h)

    def _title_text(self, cfg):
        title = str(cfg.get('event_title') or cfg.get('bridge_title') or cfg.get('flash_text') or 'MUTATION').upper()
        return re.sub(r'\s+', ' ', title).strip() or 'MUTATION'

    def render(self, buf, w, h, t, frame, cfg, pal, syms):
        audio = float(cfg.get('audio_level', 0.0) or 0.0)
        peak = float(cfg.get('audio_peak', 0.0) or 0.0)
        cam = max(float(cfg.get('camera4_motion', 0.0) or 0.0), float(cfg.get('camera2_motion', 0.0) or 0.0))
        energy = max(0.0, min(1.0, audio * 0.8 + peak * 0.45 + cam * 0.9))
        tf = frame * (0.025 + energy * 0.06)
        primary = C[pal['p']]
        secondary = C[pal['s']]
        accent = C[pal['a']]
        dark = C['dim']
        title = self._title_text(cfg)

        for y in range(h):
            for x in range(w):
                if y % 4 == 0 and random.random() < 0.12 + energy * 0.08:
                    buf[y][x] = (random.choice(['-', '.']), dark)
                elif random.random() < 0.018 + energy * 0.02:
                    buf[y][x] = (random.choice(['░', '▒']), primary)
                else:
                    buf[y][x] = None

        cx, cy = w * 0.70, h * 0.53
        for y in range(h):
            for x in range(w):
                dx = (x - cx) / max(1.0, w * 0.24)
                dy = (y - cy) / max(1.0, h * 0.34)
                field = 1.0 / (0.22 + dx * dx + dy * dy)
                ripple = math.sin(x * 0.12 - tf * 2.0) * 0.16 + math.cos(y * 0.22 + tf) * 0.12
                v = field + ripple * (1.0 + energy * 0.6)
                if v > 3.2:
                    buf[y][x] = (random.choice(['█', '▓']), C['white'] if random.random() < 0.28 else accent)
                elif v > 2.2:
                    buf[y][x] = (random.choice(['▓', '▒']), secondary)
                elif v > 1.55 and random.random() < 0.70:
                    buf[y][x] = (random.choice(['▒', '░']), primary)

        title_y = max(2, h // 2)
        title_x = max(2, (w - len(title)) // 2)
        self._write(buf, w, h, title_x + 1, title_y + 1, title, dark)
        self._write(buf, w, h, title_x, title_y, title, C['white'])
        self._hline(buf, w, h, title_x, min(w, title_x + len(title)), title_y + 2, '-', primary)
