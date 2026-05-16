import math
import random
import re

from modes.base import C, Mode


class Split(Mode):
    NAME = 'SPLIT'
    ORDER = 21

    def render(self, buf, w, h, t, frame, cfg, pal, syms):
        audio = float(cfg.get('audio_level', 0.0) or 0.0)
        peak = float(cfg.get('audio_peak', 0.0) or 0.0)
        cam = max(float(cfg.get('camera4_motion', 0.0) or 0.0), float(cfg.get('camera2_motion', 0.0) or 0.0))
        energy = max(0.0, min(1.0, audio * 0.6 + peak * 0.6 + cam * 0.75))
        tf = frame * (0.02 + energy * 0.045)
        primary = C[pal['p']]
        secondary = C[pal['s']]
        accent = C[pal['a']]
        dark = C['dim']
        title = re.sub(r'\s+', ' ', str(cfg.get('bridge_title') or cfg.get('flash_text') or 'BR_ID_GE')).upper().strip() or 'BR_ID_GE'

        for y in range(h):
            for x in range(w):
                if y % 5 == 0 and random.random() < 0.16:
                    buf[y][x] = (random.choice(['-', '.']), dark)
                elif x > w * 0.50 and random.random() < 0.05 + energy * 0.03:
                    buf[y][x] = (random.choice(['░', '▒']), primary)
                else:
                    buf[y][x] = None

        cx = w * 0.76
        for y in range(h):
            band = int((y / max(1, h)) * 11)
            shift = math.sin(tf * 2.1 + band * 0.85) * (2.0 + energy * 6.0)
            for x in range(int(w * 0.45), w):
                dx = (x - shift - cx) / max(1.0, w * 0.18)
                dy = (y - h * 0.53) / max(1.0, h * 0.38)
                arc = 1.0 / (0.28 + dx * dx * 1.2 + dy * dy * 1.8)
                wave = math.sin((x * 0.08) - tf * 2.0 + y * 0.03) * 0.28
                v = arc + wave
                if v > 2.1:
                    buf[y][x] = ('█', C['white'])
                elif v > 1.8:
                    buf[y][x] = (random.choice(['█', '▓']), accent)
                elif v > 1.5:
                    buf[y][x] = (random.choice(['▓', '▒']), secondary)
                elif v > 1.28 and random.random() < 0.75:
                    buf[y][x] = (random.choice(['▒', '░']), primary)

        title_y = max(2, h // 2)
        title_x = max(2, (w - len(title)) // 2)
        for i, ch in enumerate(title[: max(0, w - title_x - 2)]):
            if ch != ' ':
                self.put(buf, title_x + i, title_y, ch, C['white'], w, h)
        for x in range(max(0, title_x), min(w, title_x + len(title))):
            self.put(buf, x, title_y + 2, '-', primary, w, h)
