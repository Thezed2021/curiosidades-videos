#!/usr/bin/env python3
"""Série ÚLTIMO ÔNIBUS — Episódio 1 (teste)."""
import os, sys, math, random
sys.path.insert(0, os.environ.get("KIT", "/home/claude/curiosidades-videos/kit"))
from engine import *
from story import *

CLIMA = "sombrio"
TITULO = "Ele pegou o último ônibus"
SUBTITULO = "Último Ônibus • Ep. 1"
SERIE, EP, TOTAL = "Último Ônibus", 1, 8
BRUNO = dict(skin=PELE[3], hair=(25, 20, 18), hair_style="curto", shirt=(70, 90, 140),
             pants=(35, 38, 50), shoes=(20, 20, 22), extras=["mochila"])
CELIA = dict(skin=PELE[1], hair=(200, 200, 205), hair_style="coque", shirt=(40, 70, 60),
             pants=(30, 35, 40), extras=["oculos"])

N = "pm_santa"; B = "pm_alex"; C = "pf_dora"
SEGS = [
    dict(scene="ponto", cap="Todo dia, Bruno pega o último ônibus das 23h47.",
         say="Todo dia, Bruno pega o último ônibus das onze e quarenta e sete.", voice=N),
    dict(scene="ponto", cap="Cansado, com fome, só querendo chegar em casa.",
         say="Cansado, com fome, só querendo chegar em casa.", voice=N),
    dict(scene="ponto", cap="Mas hoje ele chegou vazio. E a motorista sabia o nome dele.",
         say="Mas hoje, ele chegou vazio. E a motorista sabia o nome dele.", voice=N),
    dict(scene="dentro", cap="Boa noite, Bruno. Senta lá no fundo.", say="Boa noite, Bruno. Senta lá no fundo.", voice=C),
    dict(scene="dentro", cap="Como a senhora sabe meu nome?", say="Como a senhora sabe meu nome?", voice=B),
    dict(scene="dentro", cap="Eu sei de tudo, menino. Inclusive que essa é a sua última viagem.",
         say="Eu sei de tudo, menino. Inclusive, que essa é a sua última viagem.", voice=C),
    dict(scene="fundo", cap="As luzes apagaram. E alguém chamou o nome dele lá do fundo.",
         say="As luzes apagaram. E alguém chamou o nome dele, lá do fundo.", voice=N),
    dict(scene="fundo", cap="Bruno olhou... e viu um homem igualzinho a ele.",
         say="Bruno olhou. E viu um homem igualzinho a ele.", voice=N),
    dict(scene="acorda", cap="Bruno piscou... e acordou na própria cama.", say="Bruno piscou. E acordou na própria cama.", voice=N),
    dict(scene="acorda", cap="Foi só um sonho...", say="Foi só um sonho.", voice=B),
    dict(scene="acorda", cap="O mesmo despertador. O mesmo cheiro de café.",
         say="O mesmo despertador. O mesmo cheiro de café.", voice=N),
    dict(scene="celular", cap="Até que viu a data no celular: era quinta-feira. De novo.",
         say="Até que viu a data no celular. Era quinta feira. De novo.", voice=N),
    dict(scene="final", cap="E lá fora, parado na frente da casa dele...", say="E lá fora, parado na frente da casa dele.", voice=N),
    dict(scene="final", cap="Não... não pode ser.", say="Não. Não pode ser.", voice=B),
    dict(scene="final", cap="estava o último ônibus.", say="estava o último ônibus.", voice=N),
]

# ------------------------------------------------------------ desenhos
def onibus(c, x, y, s=1.0, alpha=1.0, farol=1.0, letreiro="23:47"):
    """Ônibus de lado; (x,y) = canto inferior esquerdo da carroceria."""
    w, h = 900 * s, 360 * s
    c.rect(x, y - h, x + w, y, (225, 225, 230), alpha, radius=40 * s)
    c.rect(x, y - h * 0.32, x + w, y - h * 0.18, (200, 60, 50), alpha)
    for i in range(6):
        wx = x + 40 * s + i * 135 * s
        c.rect(wx, y - h + 50 * s, wx + 110 * s, y - h + 170 * s, (30, 40, 60), alpha, radius=10 * s)
    c.rect(x + w - 120 * s, y - h + 50 * s, x + w - 30 * s, y - 40 * s, (40, 50, 70), alpha, radius=10 * s)  # porta
    c.rect(x + 60 * s, y - h - 10 * s, x + 380 * s, y - h + 40 * s, (20, 20, 20), alpha, radius=8 * s)
    c.text(x + 220 * s, y - h + 15 * s, letreiro, 36 * s, (255, 170, 40), alpha, stroke=0)
    for wx in (x + 170 * s, x + w - 210 * s):
        c.circle(wx, y, 60 * s, (25, 25, 25), alpha); c.circle(wx, y, 25 * s, (120, 120, 125), alpha)
    if farol > 0.01:
        c.circle(x + w - 10 * s, y - 70 * s, 22 * s, (255, 245, 200), alpha * farol)
        c.glow(x + w - 10 * s, y - 70 * s, 40 * s, (255, 240, 180), 0.6 * alpha * farol)

def poste(c, x, chao, alpha=1.0, piscando=0.0):
    c.line([(x, chao), (x, chao - 620)], (60, 60, 70), 14, alpha)
    c.line([(x, chao - 620), (x + 110, chao - 620)], (60, 60, 70), 12, alpha)
    on = 1.0 if piscando == 0 else (1.0 if math.sin(c.gt * 23) > -0.3 else 0.15)
    c.circle(x + 110, chao - 600, 22, (255, 230, 150), alpha * on)
    c.poly([(x + 90, chao - 590), (x + 130, chao - 590), (x + 260, chao), (x - 40, chao)], (255, 230, 150), 0.10 * alpha * on)

def placa_ponto(c, x, chao):
    c.line([(x, chao), (x, chao - 380)], (90, 90, 100), 10)
    c.rect(x - 60, chao - 470, x + 60, chao - 380, (30, 110, 200), 1, radius=10)
    c.text(x, chao - 425, "PONTO", 30, WHITE, 1, stroke=0)

# ------------------------------------------------------------ cenas
def ponto(c):
    cidade(c, noite=True, seed=7); chuva(c, 70, 0.5)
    m1 = c.mark(2)
    poste(c, 120, 1380, piscando=1.0)
    placa_ponto(c, 330, 1380)
    person(c, 330, 1380, 0.62, BRUNO, "cansado" if c.t < m1 else "surpreso", "celular" if c.t < m1 else "parado", c.t)
    # ônibus chegando
    k = ease_out((c.t - (m1 - 0.8)) / 2.2)
    bx = lerp(1150, 420, k)
    onibus(c, bx, 1330, 0.75, c.fade_in(m1 - 0.8, .2), farol=1)
    ep_card(c, SERIE, EP, TOTAL, c.fade_in(0, .3))
    c.text(540, 340, "23:47", 130, (255, 170, 40), c.fade_in(0.2, .3), scale=c.pop(0.2, .5))
    c.text(540, 460, "O ÚLTIMO DA NOITE", 50, WHITE, c.fade_in(0.5, .3))

def dentro(c):
    ceu(c, (25, 28, 40), (12, 12, 18))
    # janelas com luzes passando
    for i in range(3):
        wx = 60 + i * 340
        c.rect(wx, 330, wx + 300, 720, (10, 12, 25), 1, radius=20)
        for j in range(4):
            lx = wx + 300 - ((c.gt * 420 + j * 170 + i * 60) % 420)
            if wx + 10 < lx < wx + 290:
                c.circle(lx, 470 + (j % 2) * 120, 14, (255, 210, 120), 0.8)
        c.rect(wx, 330, wx + 300, 720, None, 1, radius=20, outline=(70, 75, 90), width=10)
    for i in range(4):  # bancos
        c.rect(40 + i * 260, 1180, 220 + i * 260, 1290, (60, 30, 30), 1, radius=20)
    c.rect(0, 1380, W, H, (30, 30, 35))
    sway = math.sin(c.gt * 1.6) * 6
    m1, m2 = c.mark(1), c.mark(2)
    falando_c = c.t < m1 or c.t >= m2
    person(c, 300 + sway, 1380, 0.8, CELIA, "neutro" if c.t < m2 else "determinado", "aponta" if c.t < m1 else "parado", c.t)
    person(c, 770 + sway, 1380, 0.8, BRUNO, "surpreso" if c.t < m2 else "medo", "parado", c.t)
    # luz piscando na fala final
    if c.t > m2 + 2.0:
        c.rect(0, 0, W, H, (120, 0, 0), 0.18 * (0.5 + 0.5 * math.sin(c.gt * 12)))

def fundo(c):
    ceu(c, (8, 8, 12), (2, 2, 4))
    m1 = c.mark(1)
    for i in range(4):
        c.rect(40 + i * 260, 1180, 220 + i * 260, 1290, (30, 15, 15), 1, radius=20)
    c.rect(0, 1380, W, H, (12, 12, 15))
    turn = c.fade_in(m1, .4)
    person(c, 300, 1380, 0.8, BRUNO, "medo", "parado", c.t, alpha=0.95)
    # o "outro" Bruno no fundo, na sombra
    sombra = dict(BRUNO); sombra["shirt"] = (35, 45, 70); sombra["skin"] = (95, 70, 55)
    a = c.fade_in(m1 + 0.6, 1.2)
    c.glow(790, 960, 120, (180, 40, 40), 0.35 * a)
    person(c, 790, 1300, 0.62, sombra, "neutro", "parado", c.t * 0.3, alpha=a, blink=False)
    c.text(540, 380, "QUEM É ELE?", 90, RED, c.fade_in(m1 + 1.6, .3), scale=c.pop(m1 + 1.6, .4))
    flash(c, c.d - 0.25, 0.25)

def acorda(c):
    quarto(c, parede=(150, 170, 200), noite=False)
    m1 = c.mark(1)
    c.rect(150, 1140, 930, 1300, (240, 240, 245), 1, radius=30)  # cama
    c.rect(150, 1180, 930, 1300, (90, 120, 190), 1, radius=30)
    flash(c, 0, 0.6)
    # despertador
    c.rect(80, 820, 360, 980, (30, 30, 35), 1, radius=30)
    m2 = c.mark(2)
    shake = math.sin(c.gt * 60) * 6 if (c.t < m1 or c.t > m2) else 0
    c.text(220 + shake, 900, "06:00", 90, (255, 80, 60), 1, stroke=0)
    mood = "surpreso" if c.t < m1 else ("feliz" if c.t < m2 else "medo")
    person(c, 560, 1380, 0.85, BRUNO, mood, "maos_rosto" if (c.t < m1 or c.t > m2) else "parado", c.t)
    ep_card(c, SERIE, EP, TOTAL)

def celular(c):
    ceu(c, (15, 18, 30), (5, 5, 10))
    k = c.pop(0.0, .5)
    cx, cy = 540, 820
    c.rect(cx - 250 * k, cy - 460 * k, cx + 250 * k, cy + 460 * k, (20, 20, 22), 1, radius=50 * k)
    c.rect(cx - 225 * k, cy - 430 * k, cx + 225 * k, cy + 430 * k, (40, 60, 110), 1, radius=34 * k)
    if k > 0.8:
        c.text(cx, cy - 250, "06:00", 120, WHITE, 1, stroke=0)
        c.text(cx, cy - 140, "QUINTA-FEIRA", 52, WHITE, c.fade_in(0.6, .3), stroke=0)
        c.text(cx, cy - 80, "6 DE MARÇO", 40, (200, 210, 230), c.fade_in(0.8, .3), stroke=0)
        a = c.fade_in(c.mark(0) + 2.4, .3)
        c.rect(cx - 200, cy + 40, cx + 200, cy + 200, (240, 240, 245), a, radius=24)
        c.text(cx, cy + 90, "Ontem também era", 34, BLACK, a, stroke=0)
        c.text(cx, cy + 145, "6 de março.", 34, BLACK, a, stroke=0)
        c.text(cx, 1390, "DE NOVO.", 110, RED, c.fade_in(c.d - 1.6, .2), scale=c.pop(c.d - 1.6, .4))

def final(c):
    cidade(c, noite=False, seed=11)
    m1 = c.mark(1)
    # casa
    c.rect(560, 820, 1000, 1380, (230, 200, 160), 1)
    c.poly([(530, 830), (780, 640), (1030, 830)], (150, 70, 60), 1)
    c.rect(700, 960, 850, 1110, (140, 190, 230), 1, radius=8)
    person(c, 775, 1105, 0.28, BRUNO, "surpreso" if c.t < m1 else "medo", "parado", c.t)  # na janela
    c.rect(700, 1060, 850, 1110, (230, 200, 160), 1)
    m2 = c.mark(2)
    a = c.fade_in(m2 - 0.3, .5)
    onibus(c, -40, 1400, 0.62, a, farol=0.5 + 0.5 * math.sin(c.gt * 8))
    c.rect(0, 0, W, H, (0, 0, 0), 0.25 * a)
    continua(c, c.d - 1.6)

def capa(c):
    cidade(c, noite=True, seed=7); chuva(c, 70, 0.5)
    poste(c, 120, 1500)
    onibus(c, 260, 1450, 0.8, 1, farol=1)
    person(c, 170, 1500, 0.55, BRUNO, "medo", "parado", 0.0)
    c.glow(900, 1300, 140, (200, 40, 40), 0.4)

if __name__ == "__main__":
    run(SEGS, globals(), out=os.environ.get("OUT", "ep.mp4"))
