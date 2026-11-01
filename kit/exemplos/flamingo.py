#!/usr/bin/env python3
"""Por que o flamingo é cor-de-rosa?"""
import os, sys, math, random
sys.path.insert(0, os.environ.get("KIT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from engine import *

PINK = (255, 105, 160); PALE = (245, 205, 220); GRAYF = (165, 165, 172)
CARROT = (255, 135, 30); TOMATO = (235, 50, 45); LEAF = (60, 190, 90)

SEGS = [
    dict(scene="abertura", cap="Flamingo nasce cor-de-rosa?", say="Flamingo nasce cor-de-rosa?"),
    dict(scene="abertura", cap="Não! O filhote sai do ovo cinza.", say="Não! O filhote sai do ovo cinza."),
    dict(scene="comida", cap="O rosa vem do que ele come:", say="O rosa vem do que ele come:"),
    dict(scene="comida", cap="algas e camarõezinhos de água salgada, as artêmias.",
         say="algas e camarõezinhos de água salgada, as artêmias."),
    dict(scene="pigmento", cap="Eles têm carotenoides,", say="Eles têm carotenoides,"),
    dict(scene="pigmento", cap="os mesmos pigmentos da cenoura e do tomate.",
         say="os mesmos pigmentos da cenoura e do tomate."),
    dict(scene="processo", cap="O corpo do flamingo processa esses pigmentos e manda para as penas novas.",
         say="O corpo do flamingo processa esses pigmentos e manda para as penas novas."),
    dict(scene="tempo", cap="Por isso o filhote leva uns 2 a 3 anos para ficar rosa.",
         say="Por isso o filhote leva uns dois a três anos para ficar rosa."),
    dict(scene="zoo", cap="Sem esse pigmento, ele vai desbotando.", say="Sem esse pigmento, ele vai desbotando."),
    dict(scene="zoo", cap="Nos zoológicos, a ração leva pigmento extra para manter a cor.",
         say="Nos zoológicos, a ração leva pigmento extra para manter a cor."),
    dict(scene="maquiagem", cap="E tem mais: o flamingo-comum usa maquiagem!",
         say="E tem mais: o flamingo comum usa maquiagem!"),
    dict(scene="maquiagem", cap="Ele espalha nas penas um óleo rosado de uma glândula perto da cauda.",
         say="Ele espalha nas penas um óleo rosado, de uma glândula perto da cauda."),
    dict(scene="maquiagem", cap="E fica mais colorido na época de conquistar parceiros.",
         say="E fica mais colorido na época de conquistar parceiros."),
    dict(scene="final", cap="Flamingo é, literalmente, o que ele come.", say="Flamingo é, literalmente, o que ele come."),
    dict(scene="final", cap="Segue para mais curiosidades!", say="Segue para mais curiosidades!"),
]

# ------------------------------------------------------------ desenhos
def flamingo(c, x, y, s=1.0, col=PINK, alpha=1.0, head_down=0.0, bob=0.0, leg_up=True):
    """Flamingo estilizado; (x,y) = centro do corpo. head_down 0..1 abaixa a cabeça."""
    if alpha < 0.02:
        return
    dark = mix(col, (0, 0, 0), 0.25)
    y = y + math.sin(bob) * 6 * s
    # pernas
    lc = mix(col, (90, 60, 70), 0.35)
    c.line([(x - 10 * s, y + 60 * s), (x - 10 * s, y + 330 * s)], lc, 9 * s, alpha)
    if leg_up:
        c.line([(x + 15 * s, y + 60 * s), (x + 20 * s, y + 175 * s), (x - 5 * s, y + 200 * s)], lc, 9 * s, alpha)
    else:
        c.line([(x + 15 * s, y + 60 * s), (x + 20 * s, y + 330 * s)], lc, 9 * s, alpha)
    # corpo (cluster de círculos) + asa
    for dx, dy, r in [(-60, 0, 72), (10, -10, 85), (70, 10, 62), (110, 25, 40)]:
        c.circle(x + dx * s, y + dy * s, r * s, col, alpha)
    c.circle(x + 30 * s, y - 5 * s, 55 * s, dark, alpha * 0.7)
    c.poly([(x + 120 * s, y + 10 * s), (x + 175 * s, y + 40 * s), (x + 110 * s, y + 45 * s)], dark, alpha)
    # pescoço em S
    hd = clamp(head_down)
    pts = []
    for i in range(16):
        u = i / 15
        nx = x - 90 * s - 40 * s * math.sin(u * math.pi) + lerp(0, -40 * s, hd) * u
        ny = y - 30 * s - lerp(260 * s, -120 * s, hd) * u
        pts.append((nx, ny))
    c.line(pts, col, 26 * s, alpha)
    hx, hy = pts[-1]
    c.circle(hx, hy, 30 * s, col, alpha)
    # bico (dobrado, ponta preta)
    dirx = -1
    c.poly([(hx - 20 * s, hy - 10 * s), (hx - 75 * s, hy + 5 * s), (hx - 70 * s, hy + 30 * s), (hx - 15 * s, hy + 18 * s)],
           (245, 240, 230), alpha)
    c.poly([(hx - 55 * s, hy + 2 * s), (hx - 80 * s, hy + 8 * s), (hx - 75 * s, hy + 34 * s), (hx - 60 * s, hy + 26 * s)],
           (30, 30, 35), alpha)
    c.circle(hx + 6 * s, hy - 8 * s, 6 * s, (20, 20, 20), alpha)

def chick(c, x, y, s=1.0, col=GRAYF, alpha=1.0, t=0):
    for dx, dy, r in [(0, 0, 70), (-40, -20, 45), (40, -15, 45), (0, 40, 50)]:
        c.circle(x + dx * s, y + dy * s, r * s, mix(col, WHITE, 0.15), alpha)
    hx, hy = x - 55 * s, y - 85 * s + math.sin(t * 6) * 4
    c.line([(x - 30 * s, y - 40 * s), (hx, hy)], col, 30 * s, alpha)
    c.circle(hx, hy, 38 * s, mix(col, WHITE, 0.2), alpha)
    c.poly([(hx - 25 * s, hy), (hx - 70 * s, hy + 8 * s), (hx - 25 * s, hy + 16 * s)], (60, 60, 65), alpha)
    c.circle(hx + 4 * s, hy - 8 * s, 6 * s, BLACK, alpha)
    for lx in (-15, 20):
        c.line([(x + lx * s, y + 60 * s), (x + lx * s, y + 150 * s)], (110, 110, 115), 8 * s, alpha)

def egg(c, x, y, s, alpha, crack=0.0, wob=0.0):
    rx, ry = 120 * s, 160 * s
    ang = math.sin(wob) * 0.12 * crack
    # ovo como polígono rotacionado
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        px = rx * math.cos(a); py = ry * math.sin(a) * (1 + 0.12 * math.sin(a))
        pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
    c.poly(pts, (250, 245, 232), alpha)
    if crack > 0.05:
        zz = [(x - 110 * s, y - 10 * s)]
        for i in range(1, 8):
            zz.append((x - 110 * s + i * 31 * s, y + (-25 if i % 2 else 15) * s))
        n = max(2, int(len(zz) * clamp(crack)))
        c.line(zz[:n], (80, 70, 60), 7 * s, alpha)

def shrimp(c, x, y, s, col, alpha, t):
    pts = [(x + math.cos(a) * 40 * s, y + math.sin(a) * 30 * s) for a in [i / 10 * 3.3 + 0.2 for i in range(11)]]
    c.line(pts, col, 16 * s, alpha)
    c.circle(pts[0][0], pts[0][1], 9 * s, col, alpha)
    for i in range(3):
        c.line([(x - 10 * s + i * 12 * s, y + 25 * s), (x - 14 * s + i * 12 * s, y + 42 * s + math.sin(t * 20 + i) * 4)],
               col, 4 * s, alpha)

def carrot(c, x, y, s, alpha):
    c.poly([(x - 55 * s, y - 120 * s), (x + 55 * s, y - 120 * s), (x, y + 150 * s)], CARROT, alpha)
    for a in (-0.4, 0, 0.4):
        c.line([(x, y - 120 * s), (x + math.sin(a) * 80 * s, y - 120 * s - math.cos(a) * 90 * s)], LEAF, 18 * s, alpha)
    for i in range(3):
        c.line([(x - 30 * s + i * 8 * s, y - 60 * s + i * 50 * s), (x - 5 * s + i * 8 * s, y - 55 * s + i * 50 * s)],
               (200, 100, 20), 5 * s, alpha)

def tomato(c, x, y, s, alpha):
    c.circle(x, y, 100 * s, TOMATO, alpha)
    c.circle(x - 35 * s, y - 35 * s, 22 * s, (255, 140, 130), alpha * 0.7)
    for a in range(5):
        an = a / 5 * 2 * math.pi
        c.line([(x, y - 92 * s), (x + math.cos(an) * 40 * s, y - 92 * s + math.sin(an) * 18 * s)], LEAF, 12 * s, alpha)

def feather(c, x, y, s, col, alpha, ang=-0.5):
    ca, sa = math.cos(ang), math.sin(ang)
    def R(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    pts = [R(0, -200 * s)]
    for i in range(1, 20):
        u = i / 20
        pts.append(R(90 * s * math.sin(u * math.pi) * (1 - 0.3 * u), -200 * s + 400 * s * u))
    for i in range(19, 0, -1):
        u = i / 20
        pts.append(R(-80 * s * math.sin(u * math.pi) * (1 - 0.3 * u), -200 * s + 400 * s * u))
    c.poly(pts, col, alpha)
    c.line([R(0, -200 * s), R(0, 260 * s)], mix(col, WHITE, 0.5), 7 * s, alpha)
    for i in range(1, 9):
        yy = -170 * s + i * 42 * s
        c.line([R(0, yy), R(60 * s, yy - 30 * s)], mix(col, BLACK, 0.15), 3 * s, alpha)
        c.line([R(0, yy), R(-55 * s, yy - 30 * s)], mix(col, BLACK, 0.15), 3 * s, alpha)

def heart(c, x, y, s, col, alpha):
    c.circle(x - 22 * s, y - 10 * s, 26 * s, col, alpha)
    c.circle(x + 22 * s, y - 10 * s, 26 * s, col, alpha)
    c.poly([(x - 47 * s, y - 2 * s), (x + 47 * s, y - 2 * s), (x, y + 52 * s)], col, alpha)

def water(c, top=1180, col=(40, 120, 190), alpha=0.9):
    pts = [(0, H)]
    for i in range(0, W + 41, 40):
        pts.append((i, top + math.sin(i / 90 + c.gt * 2.2) * 14))
    pts.append((W, H))
    c.poly(pts, col, alpha)

# ------------------------------------------------------------ cenas
def abertura(c):
    c.bg(hue=320)
    m1 = c.mark(1)
    a = c.fade_in(0.0, 0.4)
    c.text(540, 330, "FLAMINGO", 120, WHITE, a, scale=0.9 + 0.1 * c.pop(0, .5))
    c.text(540, 470, "NASCE ROSA?", 110, PINK, c.fade_in(0.35, .4), scale=c.pop(0.35, .5))
    crack = clamp((c.t - 0.8) / max(0.5, m1 - 0.8))
    if c.t < m1 + 0.3:
        egg(c, 540, 930, 1.3, 1 - ease((c.t - m1) / 0.3), crack, c.t * 18)
    if c.t >= m1:
        k = c.pop(m1, 0.6)
        chick(c, 560, 960, 1.6 * max(0.05, k), GRAYF, clamp(k), c.t)
        c.text(830, 620, "NÃO!", 130, RED, c.fade_in(m1, .2), scale=1.6 - 0.6 * ease((c.t - m1) / .3))
        c.chip(540, 1310, "FILHOTE = CINZA", 54, (210, 210, 215), BLACK, c.fade_in(m1 + .5, .3),
               scale=c.pop(m1 + .5, .4))

def comida(c):
    c.bg(hue=200)
    m1 = c.mark(1)
    water(c, 1080)
    rnd = random.Random(4)
    # algas e artêmias flutuando
    for i in range(22):
        bx = rnd.uniform(60, 1020); by = rnd.uniform(1120, 1420)
        x = bx + math.sin(c.gt * 0.8 + i) * 25; y = by + math.cos(c.gt * 1.1 + i) * 12
        if i % 2:
            c.circle(x, y, rnd.uniform(9, 16), (70, 200, 110) if i % 4 == 1 else (220, 80, 70),
                     c.fade_in(m1 + i * 0.05, .3))
        else:
            shrimp(c, x, y, 0.8, (255, 120, 100), c.fade_in(m1 + 0.6 + i * 0.05, .3), c.gt + i)
    hd = ease((c.t - 0.6) / 1.0)
    flamingo(c, 640, 760, 1.15, PINK, c.fade_in(0, .4), head_down=hd, bob=c.gt * 2)
    c.text(540, 300, "VOCÊ É O QUE", 84, WHITE, c.fade_in(0.1, .3))
    c.text(540, 400, "COME", 120, YELLOW, c.fade_in(0.3, .3), scale=c.pop(0.3, .5))
    c.chip(260, 1000, "ALGAS", 50, (80, 220, 120), BLACK, c.fade_in(m1 + .2, .3), scale=c.pop(m1 + .2, .4))
    c.chip(800, 1000, "ARTÊMIAS", 50, (255, 140, 120), BLACK, c.fade_in(m1 + 1.6, .3), scale=c.pop(m1 + 1.6, .4))

def pigmento(c):
    c.bg(hue=25)
    m1 = c.mark(1)
    k = c.pop(0.1, .6)
    c.chip(540, 360, "CAROTENOIDES", 72, ORANGE, BLACK, c.fade_in(0.1, .3), scale=k)
    # cadeia de molécula (polieno) desenhando
    n = 12; prog = clamp((c.t - 0.3) / 1.6)
    pts = [(160 + i * 69, 600 + (40 if i % 2 else -40)) for i in range(n)]
    shown = max(2, int(n * prog))
    c.line(pts[:shown], (255, 200, 120), 10, c.fade_in(0.3, .3))
    for i, p in enumerate(pts[:shown]):
        c.circle(p[0], p[1], 16, (255, 160, 60), 1)
    carrot(c, 300, 1030, 1.25 * max(0.05, c.pop(m1 + 0.9, .5)), c.fade_in(m1 + 0.9, .3))
    tomato(c, 780, 1060, 1.3 * max(0.05, c.pop(m1 + 1.8, .5)), c.fade_in(m1 + 1.8, .3))
    c.text(300, 1260, "CENOURA", 50, CARROT, c.fade_in(m1 + 1.1, .3))
    c.text(780, 1260, "TOMATE", 50, TOMATO, c.fade_in(m1 + 2.0, .3))
    c.text(540, 780, "MESMO PIGMENTO!", 66, WHITE, c.fade_in(m1 + 0.2, .3), scale=c.pop(m1 + 0.2, .4))

def processo(c):
    c.bg(hue=280)
    d = c.d
    steps = [("COMIDA", 300, (255, 140, 120)), ("CORPO", 640, (255, 200, 90)), ("PENAS NOVAS", 980, PINK)]
    for i, (lbl, y, col) in enumerate(steps):
        t0 = 0.2 + i * (d * 0.28)
        c.chip(300, y, lbl, 52, col, BLACK, c.fade_in(t0, .3), scale=c.pop(t0, .4))
        if i < 2:
            c.arrow(300, y + 70, 300, steps[i + 1][1] - 80, WHITE, 10, 1, k=ease((c.t - t0 - 0.3) / 0.6))
    # partículas descendo
    for j in range(10):
        ph = (c.gt * 0.6 + j / 10) % 1
        c.circle(170 + math.sin(j) * 15, lerp(340, 940, ph), 9, ORANGE, 0.8 * c.fade_in(0.8, .4))
    kcol = ease((c.t - d * 0.55) / (d * 0.35))
    feather(c, 760, 760, 1.25, mix(GRAYF, PINK, kcol), c.fade_in(0.3, .4), ang=-0.35 + math.sin(c.gt) * 0.05)
    c.text(760, 1120, "CINZA", 56, mix(GRAYF, WHITE, .3), 1 - kcol)
    c.text(760, 1120, "ROSA!", 64, PINK, kcol)

def tempo(c):
    c.bg(hue=330)
    d = c.d
    k = ease((c.t - 0.3) / (d - 1.0))
    c.text(540, 300, "2 A 3 ANOS", 120, YELLOW, c.fade_in(0.1, .3), scale=c.pop(0.1, .5))
    # linha do tempo
    x0, x1, y = 140, 940, 1330
    c.bar(x0, y, x1 - x0, 26, k, PINK)
    for i, lbl in enumerate(["0", "1", "2", "3"]):
        xx = lerp(x0, x1, i / 3)
        c.circle(xx, y + 13, 20, PINK if k >= i / 3 else (70, 76, 100), 1)
        c.text(xx, y + 80, lbl + (" ANOS" if i == 3 else ""), 44, WHITE, 1)
    col = mix(GRAYF, PINK, k)
    if k < 0.45:
        chick(c, 540, 900, 1.4 + k, col, 1, c.t)
    else:
        flamingo(c, 600, 760, 0.8 + 0.35 * k, col, ease((k - 0.45) / 0.1), bob=c.gt * 2)
        chick(c, 540, 900, 1.4 + k, col, 1 - ease((k - 0.45) / 0.1), c.t)

def zoo(c):
    c.bg(hue=210)
    m1 = c.mark(1)
    fade = ease(c.t / max(0.5, m1))
    back = ease((c.t - m1 - 1.0) / 2.0)
    col = mix(mix(PINK, PALE, fade), PINK, back)
    flamingo(c, 600, 880, 1.05, col, 1, bob=c.gt * 2)
    c.chip(540, 300, "SEM PIGMENTO", 60, (220, 220, 230), BLACK, c.fade_in(0.2, .3) * (1 - c.fade_in(m1, .3)))
    c.text(540, 450, "DESBOTA", 100, PALE, c.fade_in(0.5, .3) * (1 - c.fade_in(m1, .3)))
    # ração
    a = c.fade_in(m1 + 0.3, .3)
    if a > 0:
        c.chip(540, 300, "RAÇÃO DO ZOO", 60, YELLOW, BLACK, a, scale=c.pop(m1 + .3, .4))
        c.rect(220, 1230, 560, 1330, (150, 160, 180), a, radius=40)
        for i in range(14):
            c.circle(250 + (i * 23) % 290, 1230 - 10 - (i % 3) * 18, 16, (255, 120, 80), a)
        c.chip(780, 1280, "+ PIGMENTO", 48, ORANGE, BLACK, c.fade_in(m1 + 0.8, .3), scale=c.pop(m1 + .8, .4))

def maquiagem(c):
    c.bg(hue=300)
    m1, m2 = c.mark(1), c.mark(2)
    c.text(540, 300, "MAQUIAGEM", 120, PINK, c.fade_in(0.2, .3), scale=c.pop(0.2, .5))
    c.text(540, 420, "DE FLAMINGO", 80, WHITE, c.fade_in(0.4, .3))
    deep = ease((c.t - m1 - 0.8) / 2.5)
    col = mix(PALE, (255, 70, 120), deep)
    fx, fy = 560, 850
    flamingo(c, fx, fy, 1.05, col, 1, bob=c.gt * 2)
    # glândula perto da cauda + óleo subindo ao pescoço
    gx, gy = fx + 165, fy + 30
    ga = c.fade_in(m1, .3)
    c.glow(gx, gy, 24, YELLOW, 0.8 * ga)
    c.circle(gx, gy, 18, YELLOW, ga)
    c.chip(gx - 20, gy + 120, "GLÂNDULA", 44, YELLOW, BLACK, c.fade_in(m1 + 1.2, .3), scale=c.pop(m1 + 1.2, .4))
    for j in range(8):
        ph = (c.gt * 0.7 + j / 8) % 1
        px = lerp(gx, fx - 120, ph); py = lerp(gy, fy - 240, ph) - math.sin(ph * math.pi) * 120
        c.circle(px, py, 11, (255, 90, 150), ga * (0.4 + 0.6 * math.sin(ph * math.pi)))
    if c.t > m2:
        for j in range(6):
            ph = ((c.t - m2) * 0.5 + j / 6) % 1
            heart(c, 180 + j * 140, lerp(1380, 1000, ph), 0.8, (255, 70, 120), c.fade_in(m2, .3) * (1 - ph))

def final(c):
    c.bg(hue=330)
    m1 = c.mark(1)
    flamingo(c, 600, 900, 1.1, PINK, c.fade_in(0, .3), bob=c.gt * 2)
    c.text(540, 300, "VOCÊ É", 90, WHITE, c.fade_in(0.1, .3))
    c.text(540, 420, "O QUE COME", 110, YELLOW, c.fade_in(0.3, .3), scale=c.pop(.3, .5))
    c.chip(540, 1320, "SEGUE PARA MAIS!", 58, YELLOW, BLACK, c.fade_in(m1, .3), scale=c.pop(m1, .5))

if __name__ == "__main__":
    run(SEGS, globals(), out=os.environ.get("OUT", "flamingo.mp4"))
