"""Personagens e cenários para os episódios da noite (séries).

    from engine import *
    from story import *

    LOOK = dict(skin=PELE[2], hair=(40,30,25), hair_style="curto", shirt=(60,120,200),
                pants=(40,45,60), shoes=(30,30,30), extras=["barba"])
    def cena(c):
        cidade(c, noite=True)
        person(c, 540, 1380, 1.0, LOOK, mood="medo", pose="andando", t=c.t)

Guarde o LOOK de cada personagem no arquivo da série para ele ser IGUAL em todos os episódios.
Moods: neutro feliz triste medo surpreso raiva determinado apaixonado cansado
Poses: parado andando correndo bracos_cima aponta celular abraco(estende os braços) maos_rosto
hair_style: curto longo careca rabo boné cacheado coque
extras: barba oculos mochila gravata cicatriz brinco
"""
import math, random
from engine import (W, H, Ctx, clamp, ease, ease_out, ease_back, lerp, mix, hsv,
                    WHITE, BLACK, YELLOW, RED, ORANGE, CYAN, GRAY)

PELE = [(255, 224, 196), (241, 194, 160), (210, 160, 120), (170, 115, 80), (120, 80, 55), (85, 55, 40)]


# ------------------------------------------------------------------ personagem
def person(c, x, y, s=1.0, look=None, mood="neutro", pose="parado", t=0.0, alpha=1.0, flip=False, blink=True):
    """Personagem estilizado de frente. (x, y) = ponto entre os pés. Altura ≈ 760*s."""
    if alpha < 0.02:
        return
    L = dict(skin=PELE[1], hair=(45, 35, 30), hair_style="curto", shirt=(70, 130, 210),
             pants=(45, 50, 70), shoes=(30, 30, 35), extras=[])
    L.update(look or {})
    sk, hr, sh, pa, so = L["skin"], L["hair"], L["shirt"], L["pants"], L["shoes"]
    ex = L["extras"]
    breathe = math.sin(t * 2.2) * 4 * s
    walk = pose in ("andando", "correndo")
    sp = 7.0 if pose == "correndo" else 4.2
    ph = math.sin(t * sp) if walk else 0.0
    amp = (0.45 if pose == "correndo" else 0.25)
    bob = abs(math.sin(t * sp)) * (14 if pose == "correndo" else 6) * s if walk else 0
    hipY = y - 270 * s - bob
    # pernas
    for side, k in ((-1, ph), (1, -ph)):
        hx = x + side * 40 * s
        ang = k * amp
        fx = hx + math.sin(ang) * 260 * s
        fy = hipY + math.cos(ang) * 260 * s
        c.line([(hx, hipY), (fx, fy)], pa, 52 * s, alpha)
        c.circle(fx + 14 * s * (1 if not flip else -1), fy + 6 * s, 30 * s, so, alpha)
    # tronco
    top = hipY - 255 * s + breathe
    c.rect(x - 92 * s, top, x + 92 * s, hipY + 20 * s, sh, alpha, radius=50 * s)
    if "gravata" in ex:
        c.poly([(x - 14 * s, top + 10 * s), (x + 14 * s, top + 10 * s), (x + 20 * s, top + 150 * s),
                (x, top + 175 * s), (x - 20 * s, top + 150 * s)], (180, 30, 40), alpha)
    if "mochila" in ex:
        c.line([(x - 70 * s, top + 20 * s), (x - 70 * s, top + 150 * s)], (60, 40, 30), 14 * s, alpha)
        c.line([(x + 70 * s, top + 20 * s), (x + 70 * s, top + 150 * s)], (60, 40, 30), 14 * s, alpha)
    # braços
    shY = top + 40 * s
    arms = {
        "parado": [(-1, 0.15, 0.1), (1, -0.15, -0.1)],
        "andando": [(-1, -ph * 0.4 + 0.1, 0.1), (1, ph * 0.4 - 0.1, -0.1)],
        "correndo": [(-1, -ph * 0.9 + 0.2, 1.2), (1, ph * 0.9 - 0.2, -1.2)],
        "bracos_cima": [(-1, 2.6, 0.2), (1, -2.6, -0.2)],
        "aponta": [(-1, 0.15, 0.1), (1, -1.6, 0.0)],
        "celular": [(-1, 0.15, 0.1), (1, -0.4, 2.2)],
        "abraco": [(-1, 1.3, 0.3), (1, -1.3, -0.3)],
        "maos_rosto": [(-1, 2.4, -4.24), (1, -2.4, 4.24)],
    }.get(pose, [(-1, 0.15, 0.1), (1, -0.15, -0.1)])
    hands = []
    for side, a1, a2 in arms:
        sx = x + side * 92 * s
        ex_ = sx - math.sin(a1) * 130 * s
        ey = shY + math.cos(a1) * 130 * s
        hx2 = ex_ + math.sin(a1 + a2) * 120 * s * -1
        hy2 = ey + math.cos(a1 + a2) * 120 * s
        c.line([(sx, shY), (ex_, ey), (hx2, hy2)], sh, 40 * s, alpha)
        c.circle(hx2, hy2, 22 * s, sk, alpha)
        hands.append((hx2, hy2))
    if pose == "celular":
        hx2, hy2 = hands[1]
        c.rect(hx2 - 22 * s, hy2 - 55 * s, hx2 + 22 * s, hy2 + 10 * s, (25, 25, 30), alpha, radius=8 * s)
        c.rect(hx2 - 17 * s, hy2 - 50 * s, hx2 + 17 * s, hy2 + 4 * s, (120, 200, 255), alpha * (0.6 + 0.4 * math.sin(t * 3)), radius=5 * s)
    # pescoço e cabeça
    c.rect(x - 24 * s, top - 40 * s, x + 24 * s, top + 10 * s, sk, alpha, radius=10 * s)
    hy = top - 105 * s
    hs = L["hair_style"]
    if hs in ("longo",):
        for side in (-1, 1):
            c.rect(x + side * 92 * s - (0 if side < 0 else 52 * s), hy - 40 * s,
                   x + side * 92 * s + (52 * s if side < 0 else 0), hy + 170 * s, hr, alpha, radius=24 * s)
    c.circle(x, hy, 85 * s, sk, alpha)
    c.circle(x - 85 * s, hy + 8 * s, 16 * s, sk, alpha); c.circle(x + 85 * s, hy + 8 * s, 16 * s, sk, alpha)
    if hs == "curto":
        c.poly([(x - 88 * s, hy - 5 * s), (x - 80 * s, hy - 60 * s), (x - 30 * s, hy - 95 * s), (x + 40 * s, hy - 95 * s),
                (x + 85 * s, hy - 55 * s), (x + 90 * s, hy - 5 * s), (x + 60 * s, hy - 45 * s), (x - 50 * s, hy - 50 * s)], hr, alpha)
    elif hs in ("longo", "rabo", "coque"):
        c.poly([(x - 92 * s, hy + 20 * s), (x - 85 * s, hy - 60 * s), (x - 20 * s, hy - 98 * s), (x + 50 * s, hy - 92 * s),
                (x + 92 * s, hy - 40 * s), (x + 92 * s, hy + 20 * s), (x + 55 * s, hy - 40 * s), (x - 60 * s, hy - 45 * s)], hr, alpha)
        if hs == "rabo":
            c.line([(x + 80 * s, hy - 40 * s), (x + 130 * s, hy + 20 * s + math.sin(t * 3) * 6 * s), (x + 115 * s, hy + 110 * s)], hr, 34 * s, alpha)
        if hs == "coque":
            c.circle(x, hy - 105 * s, 38 * s, hr, alpha)
    elif hs == "cacheado":
        for i in range(11):
            a = math.pi + i / 10 * math.pi
            c.circle(x + math.cos(a) * 82 * s, hy + math.sin(a) * 78 * s - 10 * s, 34 * s, hr, alpha)
    elif hs == "boné":
        c.poly([(x - 90 * s, hy - 20 * s), (x - 70 * s, hy - 85 * s), (x + 70 * s, hy - 85 * s), (x + 90 * s, hy - 20 * s)], hr, alpha)
        c.rect(x - 20 * s, hy - 32 * s, x + 140 * s, hy - 14 * s, hr, alpha, radius=8 * s)
    # rosto
    face(c, x, hy, s, mood, t, alpha, blink)
    if "oculos" in ex:
        for dx in (-32, 32):
            c.circle(x + dx * s, hy + 2 * s, 26 * s, None, alpha, outline=(30, 30, 30), width=5 * s)
        c.line([(x - 6 * s, hy), (x + 6 * s, hy)], (30, 30, 30), 5 * s, alpha)
    if "barba" in ex:
        c.poly([(x - 80 * s, hy + 10 * s), (x - 60 * s, hy + 75 * s), (x, hy + 95 * s), (x + 60 * s, hy + 75 * s),
                (x + 80 * s, hy + 10 * s), (x + 45 * s, hy + 40 * s), (x - 45 * s, hy + 40 * s)], hr, alpha)
        c.line([(x - 22 * s, hy + 50 * s), (x + 22 * s, hy + 50 * s)], mix(sk, BLACK, .45), 6 * s, alpha)
    if "cicatriz" in ex:
        c.line([(x + 40 * s, hy - 40 * s), (x + 58 * s, hy + 20 * s)], (170, 80, 80), 5 * s, alpha)
    if "brinco" in ex:
        c.circle(x - 86 * s, hy + 30 * s, 7 * s, YELLOW, alpha); c.circle(x + 86 * s, hy + 30 * s, 7 * s, YELLOW, alpha)
    if pose == "maos_rosto":
        for hx2, hy2 in hands:
            c.circle(hx2, hy2, 24 * s, sk, alpha)
    if mood == "medo":
        c.circle(x + 70 * s, hy - 40 * s, 9 * s, (150, 210, 255), alpha * 0.9)  # gota de suor
    if mood == "triste":
        ty = hy + 25 * s + ((t * 60) % 60) * s
        c.circle(x - 32 * s, ty, 7 * s, (120, 190, 255), alpha * 0.8)
    if mood == "apaixonado":
        for i in range(3):
            k = ((t * 0.6 + i / 3) % 1)
            hx, hy3 = x + (i - 1) * 60 * s, hy - 130 * s - k * 120 * s
            _heart(c, hx, hy3, 0.45 * s, (255, 80, 130), alpha * (1 - k))


def face(c, x, y, s, mood, t, alpha, blink=True):
    ink = (35, 30, 35)
    closed = blink and (t % 3.7) < 0.12
    eyeY = y - 2 * s
    for dx in (-32, 32):
        if closed or mood == "cansado":
            c.line([(x + dx * s - 14 * s, eyeY + (6 if mood == "cansado" else 0) * s), (x + dx * s + 14 * s, eyeY + (6 if mood == "cansado" else 0) * s)], ink, 6 * s, alpha)
        else:
            r = 15 * s if mood in ("surpreso", "medo") else 11 * s
            c.circle(x + dx * s, eyeY, r, WHITE, alpha)
            c.circle(x + dx * s + 2 * s, eyeY + 2 * s, r * 0.6, ink, alpha)
    # sobrancelhas
    br = {"raiva": 0.45, "determinado": 0.3, "triste": -0.4, "medo": -0.35, "surpreso": -0.1, "cansado": -0.2}.get(mood, 0.0)
    for side in (-1, 1):
        bx = x + side * 32 * s; by = y - 32 * s - (10 * s if mood == "surpreso" else 0)
        c.line([(bx - 18 * s, by - side * br * 18 * s * -1), (bx + 18 * s, by + side * br * 18 * s * -1)], ink, 7 * s, alpha)
    # boca
    my = y + 40 * s
    if mood in ("feliz", "apaixonado"):
        pts = [(x + math.cos(a) * 30 * s, my - 8 * s + math.sin(a) * 22 * s) for a in [i / 10 * math.pi for i in range(11)]]
        c.line(pts, ink, 6 * s, alpha)
    elif mood in ("triste", "cansado"):
        pts = [(x + math.cos(a) * 24 * s, my + 18 * s - math.sin(a) * 14 * s) for a in [i / 10 * math.pi for i in range(11)]]
        c.line(pts, ink, 6 * s, alpha)
    elif mood in ("surpreso", "medo"):
        c.circle(x, my + 4 * s, (16 if mood == "surpreso" else 12) * s, ink, alpha)
    elif mood == "raiva":
        c.line([(x - 26 * s, my + 6 * s), (x + 26 * s, my)], ink, 7 * s, alpha)
    else:
        c.line([(x - 20 * s, my + 4 * s), (x + 20 * s, my + 4 * s)], ink, 6 * s, alpha)


def _heart(c, x, y, s, col, alpha):
    c.circle(x - 22 * s, y - 10 * s, 26 * s, col, alpha)
    c.circle(x + 22 * s, y - 10 * s, 26 * s, col, alpha)
    c.poly([(x - 47 * s, y - 2 * s), (x + 47 * s, y - 2 * s), (x, y + 52 * s)], col, alpha)


# ------------------------------------------------------------------ cenários
def ceu(c, top, bot):
    """Céu em degradê (substitui c.bg)."""
    import numpy as np
    from PIL import Image, ImageDraw
    k = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    col = np.array(top, np.float32) * (1 - k) + np.array(bot, np.float32) * k
    c.img.paste(Image.fromarray(np.repeat(col[:, None, :], W, axis=1).astype(np.uint8)))
    c.dr = ImageDraw.Draw(c.img)


def cidade(c, noite=True, chao=1380, seed=2, fogo=False):
    """Skyline com janelas acesas. fogo=True: prédios quebrados e céu vermelho (apocalipse)."""
    if fogo:
        ceu(c, (60, 10, 10), (200, 70, 20))
    elif noite:
        ceu(c, (8, 10, 30), (40, 30, 70))
        c.circle(830, 330, 70, (240, 240, 220), 1); c.glow(830, 330, 70, (240, 240, 220), 0.3)
    else:
        ceu(c, (90, 170, 240), (200, 230, 255))
        c.circle(830, 330, 80, (255, 230, 120), 1)
    rnd = random.Random(seed)
    x = -20
    while x < W + 20:
        w = rnd.randint(110, 200); h = rnd.randint(300, 760)
        col = (25, 28, 45) if noite or fogo else (120, 130, 160)
        if fogo:
            pts = [(x, chao), (x, chao - h), (x + w * 0.4, chao - h + rnd.randint(20, 90)), (x + w * 0.7, chao - h + 30), (x + w, chao - h + rnd.randint(60, 150)), (x + w, chao)]
            c.poly(pts, (30, 15, 15))
        else:
            c.rect(x, chao - h, x + w, chao, col)
            for wy in range(int(chao - h + 30), chao - 40, 60):
                for wx in range(x + 20, x + w - 30, 45):
                    on = rnd.random() < (0.45 if noite else 0.0)
                    if on:
                        c.rect(wx, wy, wx + 22, wy + 30, (255, 220, 120))
        x += w + rnd.randint(0, 20)
    c.rect(0, chao, W, H, (20, 20, 25) if (noite or fogo) else (70, 75, 85))
    if fogo:
        for i in range(30):
            ph = (c.gt * 0.3 + i / 30) % 1
            px = (i * 137) % W
            c.circle(px + math.sin(c.gt + i) * 20, lerp(chao, 300, ph), 4, (255, 160, 60), (1 - ph))


def quarto(c, parede=(70, 80, 110), chao_y=1380, noite=True):
    ceu(c, parede, mix(parede, BLACK, .4))
    # janela
    c.rect(640, 420, 960, 820, (20, 25, 50) if noite else (150, 200, 255), 1, radius=10)
    if noite:
        c.circle(870, 520, 40, (240, 240, 220), 1)
    c.rect(640, 420, 960, 820, None, 1, radius=10, outline=(230, 230, 230), width=14)
    c.line([(800, 420), (800, 820)], (230, 230, 230), 10)
    c.rect(0, chao_y, W, H, mix(parede, (90, 60, 40), .6))


def escritorio(c, chao_y=1380):
    ceu(c, (200, 205, 215), (150, 155, 170))
    for i in range(3):
        c.rect(80 + i * 330, 380, 300 + i * 330, 700, (230, 235, 245), 1, radius=8)
    c.rect(0, chao_y, W, H, (110, 110, 120))
    c.rect(560, 1080, 1060, 1120, (120, 85, 60), 1, radius=6)  # mesa
    c.rect(740, 900, 960, 1060, (30, 30, 35), 1, radius=8)  # monitor
    c.rect(755, 915, 945, 1045, (90, 160, 230), 1, radius=4)
    c.rect(840, 1060, 860, 1085, (30, 30, 35), 1)


def chuva(c, n=90, alpha=0.6, seed=5):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(0, W); sp = rnd.uniform(900, 1500)
        y = (rnd.uniform(0, H) + c.gt * sp) % H
        c.line([(x, y), (x - 8, y + 40)], (170, 190, 230), 3, alpha)


def flash(c, start, dur=0.25, col=WHITE):
    k = (c.t - start) / dur
    if 0 <= k <= 1:
        c.rect(0, 0, W, H, col, 0.8 * (1 - k))


def legenda_fala(c, x, y, txt, alpha=1.0, size=46, cor=WHITE):
    """Balão de fala acima do personagem (use pouco: a legenda principal já mostra a fala)."""
    if alpha < 0.02:
        return
    from engine import font
    f = font(size); w = f.getlength(txt)
    c.rect(x - w / 2 - 30, y - 50, x + w / 2 + 30, y + 40, cor, alpha, radius=40)
    c.poly([(x - 20, y + 38), (x + 20, y + 38), (x, y + 75)], cor, alpha)
    c.text(x, y - 4, txt, size, BLACK, alpha, stroke=0)


def ep_card(c, serie, ep, total, alpha=1.0):
    """Etiqueta fixa do episódio no topo (abaixo da marca)."""
    c.chip(540, 215, f"{serie.upper()} • EP. {ep}/{total}", 38, (255, 255, 255), BLACK, alpha)


def continua(c, start, txt="CONTINUA..."):
    a = c.fade_in(start, .4)
    c.rect(0, 0, W, H, BLACK, 0.55 * a)
    c.text(540, 860, txt, 110, YELLOW, a, scale=c.pop(start, .5))
    c.text(540, 1000, "SEGUE PRA NÃO PERDER O PRÓXIMO", 44, WHITE, c.fade_in(start + .4, .4))
