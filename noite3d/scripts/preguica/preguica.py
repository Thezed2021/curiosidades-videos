#!/usr/bin/env python3
"""Você é uma preguiça! — vídeo 3D de humor (noite)."""
import os, sys
sys.path.insert(0, os.environ.get("KIT", "/home/claude/curiosidades-videos/kit"))
from engine import *

CENA3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cena3d.js")
CLIMA = "comedia"
TITULO = "Você é uma preguiça!"

SEGS = [
    dict(scene="abertura", cap="Você é uma preguiça!", say="Você é uma preguiça!"),
    dict(scene="abertura", cap="Fama de dorminhoca... mas tenho uma notícia: você nem dorme tanto assim.",
         say="Fama de dorminhoca. Mas tenho uma notícia: você nem dorme tanto assim."),
    dict(scene="sono", cap="Preguiças monitoradas na mata, no Panamá, dormiram cerca de 9 horas e meia por dia.",
         say="Preguiças monitoradas na mata, no Panamá, dormiram cerca de nove horas e meia por dia."),
    dict(scene="sono", cap="Umas 6 horas a menos que no cativeiro. Dorminhoca mesmo é a preguiça de zoológico.",
         say="Umas seis horas a menos que no cativeiro. Dorminhoca mesmo é a preguiça de zoológico."),
    dict(scene="digestao", cap="Seu drama é o cardápio: folhas, que dão pouquíssima energia.",
         say="Seu drama é o cardápio: folhas, que dão pouquíssima energia."),
    dict(scene="digestao", cap="Digerir uma refeição pode levar semanas, até cerca de um mês. Não é estômago, é fila de banco.",
         say="Digerir uma refeição pode levar semanas, até cerca de um mês. Não é estômago, é fila de banco."),
    dict(scene="banheiro", cap="E o banheiro? Mais ou menos uma vez por semana, você desce da árvore só pra isso.",
         say="E o banheiro? Mais ou menos uma vez por semana, você desce da árvore só pra isso."),
    dict(scene="banheiro", cap="E volta até um terço mais leve. A dieta mais rápida da floresta.",
         say="E volta até um terço mais leve. A dieta mais rápida da floresta."),
    dict(scene="nado", cap="Mas te joga num rio... e você vira atleta.",
         say="Mas te joga num rio, e você vira atleta."),
    dict(scene="nado", cap="Nada umas 3 vezes mais rápido do que anda, e pode prender o fôlego por até cerca de 40 minutos.",
         say="Nada umas três vezes mais rápido do que anda, e pode prender o fôlego por até cerca de quarenta minutos."),
    dict(scene="algas", cap="Ah, e no seu pelo crescem algas. Você fica esverdeada e some no meio das folhas.",
         say="Ah, e no seu pelo crescem algas. Você fica esverdeada e some no meio das folhas."),
    dict(scene="final", cap="Resumindo: você não é preguiçosa. Você é econômica.",
         say="Resumindo: você não é preguiçosa. Você é econômica."),
    dict(scene="final", cap="Não é preguiça. É modo economia de bateria.",
         say="Não é preguiça. É modo economia de bateria."),
]

def sono(c):
    m1 = c.mark(1)
    a = c.fade_in(1.4, .3) * (1 - c.fade_in(m1, .3))
    c.chip(540, 330, "NA NATUREZA: ~9,6 h/DIA", 50, YELLOW, BLACK, a, scale=c.pop(1.4, .4))
    c.chip(540, 330, "NO CATIVEIRO: ~6 h A MAIS", 50, ORANGE, BLACK, c.fade_in(m1 + 0.3, .3), scale=c.pop(m1 + 0.3, .4))
    for k in range(3):
        st = 0.4 + k * 0.6
        ph = ((c.t - st) % 1.8) / 1.8 if c.t > st else 0
        c.text(700 + k * 50 + ph * 40, 640 - k * 70 - ph * 60, "z", 70 + k * 18, WHITE,
               c.fade_in(st, .3) * (1 - ph) * (1 - c.fade_in(c.d - 0.4, .3)))

def digestao(c):
    m1 = c.mark(1)
    c.chip(540, 330, "FOLHA = POUCA ENERGIA", 48, GREEN, BLACK, c.fade_in(0.6, .3) * (1 - c.fade_in(m1, .3)), scale=c.pop(0.6, .4))
    a = c.fade_in(m1 + 0.2, .3)
    k = ease((c.t - m1 - 0.4) / 3.2)
    if a > 0:
        c.chip(540, 330, f"DIGESTÃO: DIA {int(1 + 29 * k)}", 54, YELLOW, BLACK, a, scale=c.pop(m1 + 0.2, .4))

def banheiro(c):
    m1 = c.mark(1)
    c.chip(540, 330, "~1 VEZ POR SEMANA", 52, YELLOW, BLACK, c.fade_in(1.2, .3) * (1 - c.fade_in(m1, .3)), scale=c.pop(1.2, .4))
    c.chip(540, 330, "ATÉ 1/3 MAIS LEVE", 54, GREEN, BLACK, c.fade_in(m1 + 0.4, .3), scale=c.pop(m1 + 0.4, .4))

def nado(c):
    m1 = c.mark(1)
    c.chip(540, 330, "3x MAIS RÁPIDA NA ÁGUA", 50, CYAN, BLACK, c.fade_in(m1 + 0.4, .3) * (1 - c.fade_in(m1 + 3.2, .3)), scale=c.pop(m1 + 0.4, .4))
    c.chip(540, 330, "FÔLEGO: ATÉ ~40 MIN", 52, YELLOW, BLACK, c.fade_in(m1 + 3.3, .3), scale=c.pop(m1 + 3.3, .4))

def algas(c):
    c.chip(540, 330, "ALGAS NO PELO = CAMUFLAGEM", 46, GREEN, BLACK, c.fade_in(1.6, .3), scale=c.pop(1.6, .4))

def final(c):
    c.chip(540, 1330, "MODO ECONOMIA", 56, YELLOW, BLACK, c.fade_in(c.mark(1) + 0.4, .3), scale=c.pop(c.mark(1) + 0.4, .5))

if __name__ == "__main__":
    run(SEGS, globals(), out=os.environ.get("OUT", "preguica.mp4"))
