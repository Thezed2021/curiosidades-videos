#!/usr/bin/env python3
"""Motor de vídeo vertical (1080x1920, 30 fps) para o canal Curiosidades do Mundo.

Um vídeo é um script curto que define SEGS e as funções de cena e chama run():

    from engine import *
    SEGS = [
      dict(scene="abertura", cap="Por que o céu é azul?", say="Por que o céu é azul?"),
      ...
    ]
    def abertura(c):   # c = Ctx: c.t (s na cena), c.d (duração), c.k (0..1), c.mark(i)
        c.bg(hue=220)
        c.text(540, 700, "CÉU AZUL", 120, YELLOW, alpha=c.fade_in(0, .4))
    run(SEGS, globals(), out="video.mp4")

- cap = legenda (pode ter dígitos); say = fala (números por extenso).
- voice (opcional) = "pm_santa" (narrador, padrão), "pm_alex" (homem) ou "pf_dora" (mulher);
  speed (opcional, padrão 1.0). Útil para falas de personagens nas histórias.
- Segmentos consecutivos com a mesma scene formam UMA cena (sem transição).
- c.mark(i) = instante (s, relativo à cena) em que começa a fala do i-ésimo
  segmento daquela cena -> use para revelar elementos no momento certo.
- Variáveis de ambiente: STILLS="5,12.3,30" renderiza só esses instantes em
  PNG + folha de contato (stills/contact.png) e sai. TTS_ROOT = pasta da voz.
"""
import math, os, random, subprocess, sys, json, hashlib, shutil, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
LEAD, GAP, TAIL = 0.30, 0.28, 1.0
CAP_Y = 1560
TITLE_HOLD = 0.9  # o título de abertura (TITULO) fica sozinho na tela até aqui e some em 0.5 s
TRANS = 0.40  # duração da transição em íris
WHITE = (255, 255, 255); YELLOW = (255, 214, 10); BLACK = (0, 0, 0)
CYAN = (64, 220, 255); ORANGE = (255, 140, 40); RED = (255, 70, 70)
GREEN = (80, 230, 120); PURPLE = (170, 110, 255); GRAY = (150, 160, 175)
BRAND = "CURIOSIDADES DO MUNDO"
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ fontes
_FONT_CANDS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-ExtraBold.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_FONT_PATH = next((p for p in _FONT_CANDS if os.path.exists(p)), None)
_fonts = {}
def font(size):
    size = int(size)
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(_FONT_PATH, size) if _FONT_PATH else ImageFont.load_default()
    return _fonts[size]

# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, clamp(k))) for a, b in zip(c1, c2))

def hsv(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

# ------------------------------------------------------------------ fundo
_STARS = None
def _stars():
    global _STARS
    if _STARS is None:
        rnd = random.Random(7)
        _STARS = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.2, 3.6),
                   rnd.uniform(0, 6.28), rnd.uniform(8, 40)) for _ in range(110)]
    return _STARS

_VIG = None
def _vignette():
    global _VIG
    if _VIG is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.70)) ** 2)
        _VIG = np.clip(1.15 - 0.55 * d ** 2, 0.45, 1.0)[..., None].astype(np.float32)
    return _VIG

_GRAD = {}
def _grad(hue):
    key = int(hue) % 360
    if key not in _GRAD:
        top = np.array(hsv(key, 0.75, 0.22), np.float32)
        bot = np.array(hsv(key + 40, 0.85, 0.07), np.float32)
        k = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        col = top * (1 - k) + bot * k
        _GRAD[key] = np.repeat(col[:, None, :], W, axis=1).astype(np.uint8)
    return _GRAD[key]

# ------------------------------------------------------------------ contexto
class Ctx:
    """Tela de um quadro + utilitários de desenho com alpha."""
    def __init__(self, t, d, gt, marks, scene_idx):
        self.t, self.d, self.gt = t, d, gt
        self.k = clamp(t / d) if d > 0 else 1.0
        self._marks = marks
        self.scene_idx = scene_idx
        self.img = Image.new("RGB", (W, H), (10, 12, 24))
        self.dr = ImageDraw.Draw(self.img)

    def mark(self, i):
        return self._marks[min(i, len(self._marks) - 1)]

    def since(self, i):
        """segundos desde o início da fala do segmento i da cena (negativo antes)."""
        return self.t - self.mark(i)

    def fade_in(self, start, dur=0.4):
        return ease((self.t - start) / dur) if dur > 0 else float(self.t >= start)

    def pop(self, start, dur=0.5):
        return ease_back((self.t - start) / dur)

    # fundo animado
    def bg(self, hue=225, stars=True, drift=1.0):
        self.img.paste(Image.fromarray(_grad(hue)))
        self.dr = ImageDraw.Draw(self.img)
        if stars:
            for (x, y, r, ph, sp) in _stars():
                yy = (y - self.gt * sp * drift) % H
                a = 0.35 + 0.35 * math.sin(self.gt * 1.7 + ph)
                self.dr.ellipse([x - r, yy - r, x + r, yy + r], fill=mix((10, 12, 24), (220, 230, 255), a))

    # ------------- primitivas com alpha (desenham em camada e compõem)
    def _layer(self, box, draw_fn, alpha):
        if alpha <= 0.01:
            return
        x0, y0, x1, y1 = [int(v) for v in box]
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W, x1), min(H, y1)
        if x1 <= x0 or y1 <= y0:
            return
        lay = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(lay), x0, y0)
        if alpha < 0.999:
            a = lay.getchannel("A").point(lambda v: int(v * alpha))
            lay.putalpha(a)
        self.img.paste(lay, (x0, y0), lay)

    def circle(self, cx, cy, r, fill, alpha=1.0, outline=None, width=0, ss=3):
        """Círculo com antialiasing (máscara supersampled)."""
        if r <= 0.5 or alpha <= 0.01:
            return
        pad = width + 2
        box = (cx - r - pad, cy - r - pad, cx + r + pad, cy + r + pad)
        x0, y0, x1, y1 = [int(v) for v in box]
        if x1 - x0 > 900:  # círculo grande: sem supersampling (memória)
            ss = 1
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        bd = ImageDraw.Draw(big)
        ox, oy = (cx - x0) * ss, (cy - y0) * ss
        bd.ellipse([ox - r * ss, oy - r * ss, ox + r * ss, oy + r * ss],
                   fill=(tuple(fill) + (255,)) if fill else None,
                   outline=(tuple(outline) + (255,)) if outline else None, width=int(width * ss))
        lay = big.resize((w, h), Image.LANCZOS)
        if alpha < 0.999:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        self.img.paste(lay, (x0, y0), lay)

    def rect(self, x0, y0, x1, y1, fill, alpha=1.0, radius=0, outline=None, width=0):
        def fn(d, ox, oy):
            d.rounded_rectangle([x0 - ox, y0 - oy, x1 - ox, y1 - oy], radius=int(radius),
                                fill=(tuple(fill) + (255,)) if fill else None,
                                outline=(tuple(outline) + (255,)) if outline else None, width=int(width))
        self._layer((x0 - width, y0 - width, x1 + width + 1, y1 + width + 1), fn, alpha)

    def line(self, pts, color, width=6, alpha=1.0):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        def fn(d, ox, oy):
            d.line([(x - ox, y - oy) for x, y in pts], fill=tuple(color) + (255,), width=int(width), joint="curve")
        self._layer((min(xs) - width, min(ys) - width, max(xs) + width + 1, max(ys) + width + 1), fn, alpha)

    def arrow(self, x0, y0, x1, y1, color=WHITE, width=10, alpha=1.0, head=34, k=1.0):
        """Seta que cresce de (x0,y0) até (x1,y1) conforme k (0..1)."""
        if k <= 0.01:
            return
        xe, ye = lerp(x0, x1, k), lerp(y0, y1, k)
        self.line([(x0, y0), (xe, ye)], color, width, alpha)
        ang = math.atan2(ye - y0, xe - x0)
        p1 = (xe + head * math.cos(ang), ye + head * math.sin(ang))
        p2 = (xe + head * 0.7 * math.cos(ang + 2.4), ye + head * 0.7 * math.sin(ang + 2.4))
        p3 = (xe + head * 0.7 * math.cos(ang - 2.4), ye + head * 0.7 * math.sin(ang - 2.4))
        self.poly([p1, p2, p3], color, alpha)

    def poly(self, pts, fill, alpha=1.0):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        def fn(d, ox, oy):
            d.polygon([(x - ox, y - oy) for x, y in pts], fill=tuple(fill) + (255,))
        self._layer((min(xs) - 2, min(ys) - 2, max(xs) + 3, max(ys) + 3), fn, alpha)

    def text(self, x, y, s, size=64, color=WHITE, alpha=1.0, anchor="mm", stroke=6,
             stroke_color=BLACK, scale=1.0, maxw=None):
        """Texto com contorno. NÃO desenha se alpha < 0.02 (evita texto opaco)."""
        if alpha < 0.02 or not s:
            return
        size = size * scale
        if maxw:
            while size > 20 and font(size).getlength(s) > maxw:
                size *= 0.94
        f = font(size)
        st = int(stroke * scale) if stroke else 0
        bb = self.dr.textbbox((x, y), s, font=f, anchor=anchor, stroke_width=st)
        def fn(d, ox, oy):
            d.text((x - ox, y - oy), s, font=f, anchor=anchor, fill=tuple(color) + (255,),
                   stroke_width=st, stroke_fill=tuple(stroke_color) + (255,))
        self._layer((bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4), fn, alpha)

    def chip(self, x, y, s, size=44, bg=YELLOW, fg=BLACK, alpha=1.0, pad=26, scale=1.0):
        """Etiqueta arredondada centrada em (x,y)."""
        if alpha < 0.02 or scale <= 0.02:
            return
        f = font(size * scale)
        tw = f.getlength(s); th = size * scale
        self.rect(x - tw / 2 - pad * scale, y - th * 0.75 - pad * 0.4 * scale,
                  x + tw / 2 + pad * scale, y + th * 0.75 + pad * 0.4 * scale,
                  bg, alpha, radius=th * 0.75)
        self.text(x, y, s, size, fg, alpha, stroke=0, scale=scale)

    def bar(self, x, y, w, h, frac, color, alpha=1.0, back=(40, 46, 70), label=None):
        self.rect(x, y, x + w, y + h, back, alpha, radius=h / 2)
        if frac > 0.005:
            self.rect(x, y, x + max(h, w * clamp(frac)), y + h, color, alpha, radius=h / 2)
        if label:
            self.text(x, y - 40, label, 40, WHITE, alpha, anchor="lm", stroke=4)

    def counter(self, x, y, value, k, size=150, color=YELLOW, fmt="{:,.0f}", suffix="", alpha=1.0):
        """Número que conta de 0 até value conforme k."""
        v = value * ease_out(k)
        s = fmt.format(v).replace(",", ".") + suffix
        self.text(x, y, s, size, color, alpha)

    def glow(self, cx, cy, r, color, alpha=0.5):
        for i in range(5, 0, -1):
            self.circle(cx, cy, r * (1 + i * 0.18), color, alpha * 0.10)

    def emoji_icon(self, *a, **k):  # sem emojis: fontes do sistema não os têm
        pass


# ------------------------------------------------------------------ climas
# Estilo de trilha por gênero. Use run(..., clima="sombrio").
# VOICE_FX = False: a voz fica SEMPRE natural (decisão do canal); o clima só muda a trilha.
VOICE_FX = False
# narr = narrador (voz pm_santa); pers = falas de personagens (outras vozes).
CLIMAS = {
    "neutro":     dict(narr=dict(pitch=1.00, speed=1.00, af=""), pers=dict(af=""), music="padrao"),
    "sombrio":    dict(narr=dict(pitch=0.86, speed=0.90,
                                 af="lowpass=f=6000,aecho=0.8:0.6:70|140:0.22|0.12"),
                       pers=dict(af="aecho=0.8:0.5:60:0.15"), music="sombrio"),
    "suspense":   dict(narr=dict(pitch=0.92, speed=0.95, af="aecho=0.8:0.5:50|100:0.15|0.08"),
                       pers=dict(af=""), music="tenso"),
    "acao":       dict(narr=dict(pitch=0.95, speed=1.08, af=""), pers=dict(af=""), music="tenso"),
    "romantico":  dict(narr=dict(pitch=1.00, speed=0.93, af="lowpass=f=7000,aecho=0.8:0.4:40:0.12"),
                       pers=dict(af=""), music="romantico"),
    "comedia":    dict(narr=dict(pitch=1.04, speed=1.07, af=""), pers=dict(af=""), music="comedia"),
    "inspirador": dict(narr=dict(pitch=0.97, speed=0.95, af="aecho=0.8:0.4:40:0.10"),
                       pers=dict(af=""), music="inspirador"),
    "drama":      dict(narr=dict(pitch=0.94, speed=0.92, af="aecho=0.8:0.45:50:0.12"),
                       pers=dict(af=""), music="drama"),
}

def _fx(path, pitch=1.0, af=""):
    """Aplica pitch (sem mudar a duração) e filtros ffmpeg ao wav 24 kHz, no lugar."""
    chain = []
    if abs(pitch - 1.0) > 1e-3:
        chain.append(f"asetrate={int(24000 * pitch)},aresample=24000,atempo={1 / pitch:.5f}")
    if af:
        chain.append(af)
    if not chain:
        return
    tmp = path + ".fx.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-af", ",".join(chain),
                    "-ar", "24000", "-ac", "1", tmp], check=True)
    os.replace(tmp, path)


# ------------------------------------------------------------------ voz
def _tts(voice="pm_santa"):
    sys.path.insert(0, HERE)
    from neural_tts import TTS
    return TTS(voice=voice)

def build_voice(segs, cache_dir="voz", clima="neutro"):
    """Gera um wav 24 kHz por segmento (com cache). Aplica o clima. Retorna durações."""
    os.makedirs(cache_dir, exist_ok=True)
    cl = CLIMAS.get(clima, CLIMAS["neutro"])
    engines = {}; durs = []
    for i, s in enumerate(segs):
        voice = s.get("voice", "pm_santa")
        narr = voice == "pm_santa"
        cfg = cl["narr"] if narr else dict(pitch=1.0, speed=1.0, **cl["pers"])
        if not VOICE_FX:
            cfg = dict(pitch=1.0, speed=1.0, af="")
        speed = s.get("speed", cfg.get("speed", 1.0))
        key = f'{voice}|{speed}|{clima if VOICE_FX else "-"}|{s["say"]}'
        h = hashlib.md5(key.encode()).hexdigest()[:10]
        p = os.path.join(cache_dir, f"{i:02d}_{h}.wav")
        if not os.path.exists(p):
            if voice not in engines:
                engines[voice] = _tts(voice)
            tts = engines[voice]
            a = tts.say(s["say"], speed=speed)
            tts.save_wav(a, p)
            _fx(p, cfg.get("pitch", 1.0), cfg.get("af", ""))
        with wave.open(p) as w:
            durs.append(w.getnframes() / w.getframerate())
        s["_wav"] = p
    return durs

# ------------------------------------------------------------------ linha do tempo
def build_timeline(segs, durs):
    t = 0.0
    blocks = []  # [scene, start, end, [voice starts relativos]]
    for i, (s, d) in enumerate(zip(segs, durs)):
        new = (i == 0) or (s["scene"] != segs[i - 1]["scene"])
        if new:
            if blocks:
                blocks[-1][2] = t
            blocks.append([s["scene"], t, None, []])
            t += LEAD
        s["_t0"] = t; s["_t1"] = t + d
        blocks[-1][3].append(t - blocks[-1][1])
        t += d + GAP
    t += TAIL
    blocks[-1][2] = t
    return blocks, t

def caption_words(segs):
    """Palavras com instante de início/fim (proporcional ao nº de letras)."""
    words = []
    for s in segs:
        ws = s["cap"].split()
        if not ws:
            continue
        wts = [max(2, len(w.strip(".,!?;:"))) + 1.5 for w in ws]
        tot = sum(wts); t = s["_t0"]; dur = s["_t1"] - s["_t0"]
        group = []
        for w, wt in zip(ws, wts):
            d = dur * wt / tot
            words.append(dict(w=w, t0=t, t1=t + d, seg=s))
            t += d
    # agrupa em blocos de até 3 palavras / 20 letras, sem cruzar segmentos
    groups = []; cur = []
    for w in words:
        if cur and (cur[-1]["seg"] is not w["seg"] or len(cur) >= 3 or
                    sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 20 or
                    cur[-1]["w"][-1] in ".!?"):
            groups.append(cur); cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    for g in groups:
        for w in g:
            w["group"] = g
    return words, groups


# ------------------------------------------------------------------ render
class Video:
    def __init__(self, segs, ns, clima="neutro"):
        self.segs, self.ns, self.clima = segs, ns, clima
        durs = build_voice(segs, clima=clima)
        self.blocks, self.total = build_timeline(segs, durs)
        self.words, self.groups = caption_words(segs)
        self.nframes = int(math.ceil(self.total * FPS))

    def block_at(self, gt):
        for i, b in enumerate(self.blocks):
            if b[1] <= gt < b[2]:
                return i
        return len(self.blocks) - 1

    def render_scene(self, bi, gt):
        name, t0, t1, marks = self.blocks[bi]
        c = Ctx(gt - t0, t1 - t0, gt, marks, bi)
        self.ns[name](c)
        return c

    def captions(self, c, gt):
        g = None; cur = None
        for grp in self.groups:
            if grp[0]["t0"] - 0.05 <= gt < grp[-1]["t1"] + 0.25:
                g = grp
        if not g:
            return
        for w in g:
            if w["t0"] <= gt < w["t1"] + 0.05:
                cur = w
        if cur is None:
            cur = g[-1] if gt >= g[-1]["t0"] else g[0]
        size = 74
        f = font(size)
        sp = f.getlength(" ") * 1.9
        widths = [f.getlength(w["w"].upper()) for w in g]
        total = sum(widths) + sp * (len(g) - 1)
        scale = min(1.0, 980 / total)
        x = W / 2 - total * scale / 2
        a_in = ease((gt - g[0]["t0"] + 0.05) / 0.12)
        for w, wd in zip(g, widths):
            col = YELLOW if w is cur else WHITE
            pop = 1.0 + (0.05 * (1 - ease((gt - w["t0"]) / 0.15)) if w is cur and gt >= w["t0"] else 0)
            c.text(x + wd * scale / 2, CAP_Y, w["w"].upper(), size, col, a_in, stroke=9,
                   scale=scale * pop)
            x += (wd + sp) * scale

    def brand(self, c):
        c.text(W / 2, 96, BRAND, 34, (235, 240, 255), 0.85, stroke=4)
        c.rect(W / 2 - 60, 128, W / 2 + 60, 134, YELLOW, 0.85, radius=3)

    def title_overlay(self, c, gt, alpha=None, cover=False):
        """Título do vídeo em destaque (abertura e capa)."""
        tit = self.ns.get("TITULO")
        if not tit:
            return
        a = alpha if alpha is not None else 1.0 - ease((gt - TITLE_HOLD) / 0.5)
        if a < 0.02:
            return
        import numpy as _np
        y0, y1 = (250, 900) if cover else (560, 1260)
        if not cover:  # abertura: cena inteira escurecida + desfocada atrás do título
            bg = c.img.filter(ImageFilter.GaussianBlur(10 * a))
            lay = _np.asarray(bg).astype(_np.float32) * (1 - 0.6 * a)
        else:          # capa: degradê escuro só no alto, onde vai o título
            lay = _np.asarray(c.img).astype(_np.float32)
            yy = _np.arange(H, dtype=_np.float32)[:, None, None]
            lay = lay * (1 - 0.7 * _np.clip((1050 - yy) / 900, 0, 1))
        c.img = Image.fromarray(lay.clip(0, 255).astype(_np.uint8)); c.dr = ImageDraw.Draw(c.img)
        words = tit.upper().split()
        lines, cur = [], ""
        for w in words:
            if cur and font(118).getlength(cur + " " + w) > 940:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        lines = lines[:4]
        size = 118 if len(lines) <= 3 else 100
        ytop = (y0 + y1) / 2 - (len(lines) - 1) * size * 0.58
        for i, ln in enumerate(lines):
            col = YELLOW if i == len(lines) - 1 else WHITE
            c.text(W / 2, ytop + i * size * 1.16, ln, size, col, a, stroke=12, maxw=980,
                   scale=1.0 if cover else (1.0 + 0.04 * (1 - a)))
        sub = self.ns.get("SUBTITULO")
        if sub:
            c.chip(W / 2, ytop + len(lines) * size * 1.16 + 30, sub.upper(), 44, YELLOW, BLACK, a)

    def frame(self, fi, captions=True):
        gt = fi / FPS
        bi = self.block_at(gt)
        c = self.render_scene(bi, gt)
        img = c.img
        t_in = gt - self.blocks[bi][1]
        if bi > 0 and t_in < TRANS:
            prev = self.render_scene(bi - 1, self.blocks[bi][1] - 1e-3).img
            k = ease(t_in / TRANS)
            r = int(k * math.hypot(W, H) / 2 * 1.05)
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
            img = Image.composite(img, prev, mask)
            c.img = img; c.dr = ImageDraw.Draw(img)
            if 0 < r < 1300:
                c.dr.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], outline=YELLOW, width=8)
        arr = np.asarray(c.img).astype(np.float32) * _vignette()
        c.img = Image.fromarray(arr.clip(0, 255).astype(np.uint8)); c.dr = ImageDraw.Draw(c.img)
        if captions:
            self.title_overlay(c, gt)
        self.brand(c)
        if captions and (not self.ns.get("TITULO") or gt > TITLE_HOLD + 0.3):
            self.captions(c, gt)
        return c.img

    def cover(self, path="capa.jpg"):
        """Capa 1080x1920: cena mais forte (CAPA_T, s) + título grande."""
        t = float(self.ns.get("CAPA_T", self.total * 0.4))
        if "capa" in self.ns:  # desenho próprio da capa (sem textos), recomendado
            c = Ctx(t, self.total, t, [0], 0)
            self.ns["capa"](c)
            arr = np.asarray(c.img).astype(np.float32) * _vignette()
            c.img = Image.fromarray(arr.clip(0, 255).astype(np.uint8)); c.dr = ImageDraw.Draw(c.img)
            self.brand(c)
        else:
            img = self.frame(min(self.nframes - 1, int(t * FPS)), captions=False)
            img = img.filter(ImageFilter.GaussianBlur(4))
            c = Ctx(0, 1, t, [0], 0); c.img = img; c.dr = ImageDraw.Draw(img)
        self.title_overlay(c, 0, alpha=1.0, cover=True)
        c.img.convert("RGB").save(path, quality=90)
        return path

_V = None
def _work(fi):
    return _V.frame(fi).tobytes()


# ------------------------------------------------------------------ áudio
def _synth_music(total, sr=44100, seed=3, style="padrao"):
    """Trilha gerada por código. style: padrao sombrio tenso romantico comedia inspirador drama."""
    if style != "padrao":
        return _MUSIC[style](total, sr, seed)
    rnd = np.random.default_rng(seed)
    n = int(total * sr); t = np.arange(n) / sr
    roots = [220.0, 174.61, 261.63, 196.0]  # A3 F3 C4 G3 (i-VI-III-VII)
    bar = 4.0
    out = np.zeros(n, np.float32)
    for bi in range(int(total / bar) + 2):
        r = roots[bi % 4]
        s0 = int(bi * bar * sr); s1 = min(n, int((bi + 1) * bar * sr + 0.5 * sr))
        if s0 >= n:
            break
        tt = t[s0:s1] - bi * bar
        env = np.minimum(1, tt / 0.6) * np.exp(-np.maximum(0, tt - bar) * 6)
        chord = [r, r * 1.2599 if bi % 4 in (1,) else r * 1.1892, r * 1.4983, r * 2]
        seg = sum(np.sin(2 * np.pi * f * tt + 0.3 * np.sin(2 * np.pi * 0.2 * tt)) for f in chord)
        out[s0:s1] += (0.06 * env * seg).astype(np.float32)
    beat = 60 / 96
    for i in range(int(total / beat)):
        s0 = int(i * beat * sr); L = int(0.25 * sr)
        if s0 + L > n:
            break
        tt = np.arange(L) / sr
        kick = np.sin(2 * np.pi * (55 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)
        out[s0:s0 + L] += 0.10 * kick
        if i % 2 == 1:
            hat = rnd.normal(0, 1, int(0.05 * sr)) * np.exp(-np.arange(int(0.05 * sr)) / sr * 90)
            hat = np.diff(hat, prepend=0)
            out[s0:s0 + len(hat)] += 0.012 * hat
    return out

# ---- estilos de trilha (tudo sintetizado, sem material de terceiros)
def _env_ar(n, sr, a=0.01, r=0.3):
    t = np.arange(n) / sr
    return np.minimum(1, t / a) * np.exp(-t / r)

def _pad(total, sr, roots, ratios, bar, vol, wob=0.2, attack=0.8):
    n = int(total * sr); t = np.arange(n) / sr; out = np.zeros(n, np.float32)
    for bi in range(int(total / bar) + 2):
        s0 = int(bi * bar * sr); s1 = min(n, int((bi + 1) * bar * sr + 0.8 * sr))
        if s0 >= n:
            break
        tt = t[s0:s1] - bi * bar
        env = np.minimum(1, tt / attack) * np.exp(-np.maximum(0, tt - bar) * 4)
        r = roots[bi % len(roots)]
        rat = ratios[bi % len(ratios)] if isinstance(ratios[0], (list, tuple)) else ratios
        seg = sum(np.sin(2 * np.pi * r * q * tt + wob * np.sin(2 * np.pi * 0.15 * tt)) for q in rat)
        out[s0:s1] += (vol * env * seg).astype(np.float32)
    return out

def _hits(total, sr, period, fn, start=0.0):
    n = int(total * sr); out = np.zeros(n, np.float32); i = 0
    while True:
        s0 = int((start + i * period) * sr)
        if s0 >= n:
            break
        y = fn(i)
        e = min(n, s0 + len(y)); out[s0:e] += y[:e - s0]; i += 1
    return out

def _m_sombrio(total, sr, seed):
    rnd = np.random.default_rng(seed); n = int(total * sr); t = np.arange(n) / sr
    drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 0.5)
             + 0.35 * np.sin(2 * np.pi * 58.3 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    out = 0.07 * drone
    out += _pad(total, sr, [110.0, 103.8, 98.0, 103.8], [1, 1.189, 1.414], 6.0, 0.022, wob=0.4, attack=2.0)
    def beat(i):  # batida de coração (tum-tum)
        L = int(0.7 * sr); tt = np.arange(L) / sr; y = np.zeros(L, np.float32)
        for off, amp in ((0.0, 1.0), (0.22, 0.7)):
            k = tt - off; m = k >= 0
            y[m] += amp * np.sin(2 * np.pi * 48 * k[m]) * np.exp(-k[m] * 16)
        return 0.16 * y
    out += _hits(total, sr, 1.15, beat, 0.5)
    def shimmer(i):
        L = int(2.5 * sr); tt = np.arange(L) / sr
        f = rnd.choice([1244.5, 1318.5, 1479.9])
        return 0.012 * np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / 1.0) * np.exp(-tt * 1.2)
    out += _hits(total, sr, 7.3, shimmer, 3.0)
    return out.astype(np.float32)

def _m_tenso(total, sr, seed):
    n = int(total * sr); t = np.arange(n) / sr
    out = 0.05 * np.sin(2 * np.pi * 65.4 * t) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 4 * t)))
    out += _pad(total, sr, [130.8, 123.5], [1, 1.189, 1.498], 4.0, 0.02, attack=1.5)
    tick = lambda i: (0.05 if i % 2 == 0 else 0.03) * np.sin(2 * np.pi * 2200 * np.arange(int(0.03 * sr)) / sr) * _env_ar(int(0.03 * sr), sr, 0.001, 0.008)
    out += _hits(total, sr, 0.5, tick)
    return out.astype(np.float32)

def _pluck(f, sr, L=0.6, vol=0.08):
    n = int(L * sr); tt = np.arange(n) / sr
    return vol * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * _env_ar(n, sr, 0.005, 0.25)

def _m_romantico(total, sr, seed):
    roots = [261.6, 220.0, 174.6, 196.0]
    out = _pad(total, sr, roots, [[1, 1.26, 1.498], [1, 1.189, 1.498], [1, 1.26, 1.498], [1, 1.26, 1.498]], 4.0, 0.035)
    arp = [1, 1.26, 1.498, 2, 1.498, 1.26]
    out += _hits(total, sr, 0.5, lambda i: _pluck(roots[int(i * 0.5 / 4) % 4] * 2 * arp[i % 6], sr, 0.8, 0.035))
    return out.astype(np.float32)

def _m_comedia(total, sr, seed):
    roots = [261.6, 349.2, 392.0, 261.6]; bass = [130.8, 174.6, 196.0, 130.8]
    out = _hits(total, sr, 0.27, lambda i: _pluck(bass[int(i * 0.27 / 2.16) % 4] * (1 if i % 2 == 0 else 1.498), sr, 0.25, 0.07))
    mel = [1, 1.26, 1.498, 1.26, 2, 1.498, 1.26, 1.122]
    out += _hits(total, sr, 0.54, lambda i: _pluck(roots[int(i * 0.54 / 2.16) % 4] * 2 * mel[i % 8], sr, 0.3, 0.03), 0.27)
    return out.astype(np.float32)

def _m_inspirador(total, sr, seed):
    roots = [261.6, 196.0, 220.0, 174.6]
    out = _pad(total, sr, roots, [[1, 1.26, 1.498, 2], [1, 1.26, 1.498, 2], [1, 1.189, 1.498, 2], [1, 1.26, 1.498, 2]], 4.0, 0.03)
    n = int(total * sr); swell = np.minimum(1, np.arange(n) / sr / max(1, total * 0.7))
    out = out * (0.6 + 0.6 * swell)
    out += _hits(total, sr, 0.5, lambda i: 0.06 * np.sin(2 * np.pi * 60 * np.arange(int(.2 * sr)) / sr) * _env_ar(int(.2 * sr), sr, .002, .08))
    return out.astype(np.float32)

def _m_drama(total, sr, seed):
    roots = [220.0, 174.6, 130.8, 196.0]
    return _pad(total, sr, roots, [[1, 1.189, 1.498], [1, 1.26, 1.498], [1, 1.26, 1.498], [1, 1.26, 1.498]], 5.0, 0.04, attack=1.5)

_MUSIC = dict(sombrio=_m_sombrio, tenso=_m_tenso, romantico=_m_romantico, comedia=_m_comedia,
              inspirador=_m_inspirador, drama=_m_drama)

def _whoosh(sr=44100, L=0.5, seed=1):
    rnd = np.random.default_rng(seed)
    n = int(L * sr); x = rnd.normal(0, 1, n).astype(np.float32)
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    y = np.zeros(n, np.float32); a = 0.0
    for i in range(n):  # passa-baixas com corte variando
        c = 0.02 + 0.25 * (i / n)
        a += c * (x[i] - a); y[i] = a
    return y * env * 0.5

def build_audio(v, out_wav, sr=44100):
    n = int(v.total * sr)
    voice24 = np.zeros(int(v.total * 24000) + 24000, np.float32)
    for s in v.segs:
        with wave.open(s["_wav"]) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        p = int(s["_t0"] * 24000)
        voice24[p:p + len(a)] += a
    raw = "voz_raw.wav"; proc = "voz_proc.wav"
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes((np.clip(voice24, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                    "volume=2.2,alimiter=limit=0.89", "-ar", str(sr), proc], check=True)
    with wave.open(proc) as w:
        voice = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    music = _synth_music(v.total, sr, style=CLIMAS.get(v.clima, CLIMAS["neutro"])["music"])[:n]
    music = np.pad(music, (0, n - len(music)))
    # ducking: envelope da voz suavizada
    env = np.abs(voice)
    k = int(0.15 * sr)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1 - 0.65 * np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    fade = np.minimum(1, np.arange(n) / sr / 1.0) * np.minimum(1, (n - np.arange(n)) / sr / 1.5)
    mixd = voice + music * duck * fade * 0.55
    wh = _whoosh(sr)
    for b in v.blocks[1:]:
        p = int((b[1] - 0.15) * sr)
        if 0 <= p < n - len(wh):
            mixd[p:p + len(wh)] += wh * 0.35
    mixd /= max(1e-9, np.abs(mixd).max()) / 0.89  # pico ≈ -1 dBFS
    st = np.stack([mixd, mixd], 1)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------ principal
def contact_sheet(paths, out, cols=3):
    ims = [Image.open(p).resize((360, 640)) for p in paths]
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 360, rows * 640), (0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 360, (i // cols) * 640))
    sheet.save(out)

def run(segs, ns, out="video.mp4", clima=None):
    """clima: neutro sombrio suspense acao romantico comedia inspirador drama
    (ou defina CLIMA = "..." no script do vídeo)."""
    global _V
    clima = clima or ns.get("CLIMA", "neutro")
    v = Video(segs, ns, clima)
    _V = v
    print(f"[engine] clima {clima}; duração total {v.total:.1f}s, {v.nframes} quadros, {len(v.blocks)} cenas")
    for b in v.blocks:
        print(f"   cena {b[0]:<18} {b[1]:6.2f} -> {b[2]:6.2f}  falas em {[round(m,2) for m in b[3]]}")
    stills = os.environ.get("STILLS")
    if stills:
        os.makedirs("stills", exist_ok=True)
        paths = []
        for s in stills.split(","):
            fi = min(v.nframes - 1, int(float(s) * FPS))
            p = f"stills/s_{float(s):06.2f}.png"
            v.frame(fi).save(p); paths.append(p)
        contact_sheet(paths, "stills/contact.png")
        if ns.get("TITULO"):
            v.cover("stills/capa.jpg")
            print("[engine] capa em stills/capa.jpg")
        print("[engine] stills em stills/contact.png")
        return v
    build_audio(v, "audio.wav")
    part = out.replace(".mp4", ".part.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio.wav",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", part],
                          stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for i, b in enumerate(pool.imap(_work, range(v.nframes), chunksize=8)):
            ff.stdin.write(b)
            if i % 150 == 0:
                print(f"   quadro {i}/{v.nframes}", flush=True)
    ff.stdin.close(); ff.wait()
    if ff.returncode != 0:
        raise SystemExit("ffmpeg falhou")
    os.replace(part, out)
    if ns.get("TITULO"):
        cp = os.path.splitext(out)[0] + "_capa.jpg"
        v.cover(cp)
        print(f"[engine] capa em {cp}")
    verify(out, v.total)
    return v

def verify(path, expected):
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                         "stream=width,height,r_frame_rate,codec_name:format=duration,size",
                         "-of", "json", path], capture_output=True, text=True).stdout
    info = json.loads(pr)
    vd = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    mx = [l for l in vd.splitlines() if "max_volume" in l]
    print("[verify]", json.dumps(info["streams"]), info["format"], mx[-1].split("]")[-1] if mx else "")
    os.makedirs("check", exist_ok=True)
    dur = float(info["format"]["duration"])
    ps = []
    for i, f in enumerate(np.linspace(1, dur - 1, 9)):
        p = f"check/f{i}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{f:.2f}", "-i", path,
                        "-frames:v", "1", p])
        ps.append(p)
    contact_sheet(ps, "check/final_contact.png")
    print(f"[verify] duração {dur:.1f}s (esperado ~{expected:.1f}s); quadros em check/final_contact.png")
