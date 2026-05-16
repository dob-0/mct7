import math
import random
import re

from modes.base import C, Mode


class Split(Mode):
    NAME = 'SPLIT'
    ORDER = 21

    def _first(self, cfg, key, fallback):
        value = cfg.get(key)
        if value is None:
            return fallback
        text = str(value).strip()
        return text or fallback

    def _parts(self, value, fallback):
        raw = str(value or '|'.join(fallback))
        items = [part.strip() for part in re.split(r'[|\n]+', raw) if part.strip()]
        return items or fallback

    def render(self, buf, w, h, t, frame, cfg, pal, syms):
        audio = float(cfg.get('audio_level', 0.0) or 0.0)
        peak = float(cfg.get('audio_peak', 0.0) or 0.0)
        cam = max(
            float(cfg.get('camera4_motion', 0.0) or 0.0),
            float(cfg.get('camera2_motion', 0.0) or 0.0),
        )
        energy = max(0.0, min(1.0, audio * 0.6 + peak * 0.6 + cam * 0.75))
        tf = frame * (0.02 + energy * 0.045)
        primary = C[pal['p']]
        secondary = C[pal['s']]
        accent = C[pal['a']]
        dark = C['dim']

        title = self._first(cfg, 'bridge_title', cfg.get('flash_text', 'STITCH')).upper()
        kicker = self._first(cfg, 'bridge_kicker', 'GYUMRI <-> MUNICH').upper()
        latency = self._first(cfg, 'bridge_latency', '121-228MS').upper()
        node_a = self._first(cfg, 'bridge_node_a', self._first(cfg, 'bridge_where', 'LATENT SPACE')).upper()
        node_b = self._first(cfg, 'bridge_node_b', 'MUNICH [STEEL]').upper()
        signals_a = self._parts(cfg.get('bridge_signals_a'), ['AI STITCH', 'SHARED BODY', 'GHOST HAND', 'LATENT HANDSHAKE', 'ARMENIAN EMOTION'])
        signals_b = self._parts(cfg.get('bridge_signals_b'), ['GERMAN LIGHT', 'DIGITAL ARCHITECTURE', 'NETWORK LAG', 'RECIPROCAL TRAP', 'POINT CLOUDS'])
        footer = self._first(cfg, 'bridge_footer', 'TELE-SYMBIOTIC XR PERFORMANCE').upper()

        for y in range(h):
            for x in range(w):
                if y % 5 == 0 and random.random() < 0.16:
                    buf[y][x] = (random.choice(['─', '·']), dark)
                elif x > w * 0.50 and random.random() < 0.05 + energy * 0.03:
                    buf[y][x] = (random.choice(['░', '▒']), primary)
                else:
                    buf[y][x] = None

        # sliced chrome mass on right
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

        meta = f'{kicker} {latency}'
        mx = max(2, int(w * 0.08))
        my = max(2, h // 9)
        for i, ch in enumerate(meta[: max(0, w - mx - 2)]):
            if ch != ' ':
                self.put(buf, mx + i, my, ch, C['white'], w, h)
        title_y = my + 3
        title_x = max(2, (w - len(title)) // 2)
        for i, ch in enumerate(title[: max(0, w - title_x - 2)]):
            if ch != ' ':
                self.put(buf, title_x + i, title_y, ch, C['white'], w, h)
        for x in range(max(0, title_x), min(w, title_x + len(title) - 4)):
            self.put(buf, x, title_y + 2, '─', primary, w, h)

        left_x = max(2, int(w * 0.08))
        y0 = title_y + 5
        sections = [
            (node_a, signals_a, y0),
            (node_b, signals_b, y0 + 2 + len(signals_a) * 2),
        ]
        for si, (label, signals, sy) in enumerate(sections):
            for i, ch in enumerate(label):
                if ch != ' ':
                    self.put(buf, left_x + i, sy, ch, C['white'], w, h)
            for li, name in enumerate(signals):
                row_y = sy + 2 + li * 2
                col = C['white'] if (li + si) % 2 == 0 else accent
                for i, ch in enumerate(name.upper()[: max(0, w - left_x - 2)]):
                    if ch != ' ':
                        self.put(buf, left_x + i, row_y, ch, col, w, h)

        fy = max(1, h - 3)
        for i, ch in enumerate(footer[: max(0, w - left_x - 2)]):
            if ch != ' ':
                self.put(buf, left_x + i, fy, ch, C['white'], w, h)
