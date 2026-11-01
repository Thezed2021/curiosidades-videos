#!/usr/bin/env python3
"""Você é uma piranha! — vídeo 3D de humor (noite)."""
import os, sys
sys.path.insert(0, os.environ.get("KIT", "/home/claude/curiosidades-videos/kit"))
from engine import *

CENA3D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cena3d.js")
CLIMA = "comedia"
TITULO = "Você é uma piranha!"

SEGS = [
    dict(scene="abertura", cap="Você é uma piranha!", say="Você é uma piranha!"),
    dict(scene="abertura", cap="Dentes afiados, fama de vilã de filme... e um medo enorme de tudo.",
         say="Dentes afiados, fama de vilã de filme. E um medo enorme de tudo."),
    dict(scene="cardume", cap="Sério. Você anda em cardume não pra caçar, mas pra não virar comida.",
         say="Sério. Você anda em cardume não pra caçar, mas pra não virar comida."),
    dict(scene="cardume", cap="Boto, jacaré, ave e até o pirarucu querem você no cardápio.",
         say="Boto, jacaré, ave, e até o pirarucu, querem você no cardápio."),
    dict(scene="nervosa", cap="Cientistas viram que, num grupo pequeno, você fica tão nervosa que respira mais rápido.",
         say="Cientistas viram que, num grupo pequeno, você fica tão nervosa que respira mais rápido."),
    dict(scene="nervosa", cap="Com a galera toda junta, você se acalma bem mais rápido.",
         say="Com a galera toda junta, você se acalma bem mais rápido."),
    dict(scene="cardapio", cap="E o seu cardápio? Peixes, insetos, restos... e até frutas e plantas.",
         say="E o seu cardápio? Peixes, insetos, restos. E até frutas e plantas."),
    dict(scene="dentes", cap="Mas a dentadura é nível profissional: os dentes se encaixam como uma serra.",
         say="Mas a dentadura é nível profissional: os dentes se encaixam como uma serra."),
    dict(scene="dentes", cap="Quando gastam, você troca todos de um lado da boca de uma vez. Os novos já esperam embaixo.",
         say="Quando gastam, você troca todos de um lado da boca de uma vez. Os novos já esperam embaixo."),
    dict(scene="late", cap="Ah, e se alguém te provoca... você late.", say="Ah, e se alguém te provoca... você late."),
    dict(scene="late", cap="Sério! Músculos vibram sua bexiga natatória e sai um som parecido com latido.",
         say="Sério! Músculos vibram sua bexiga natatória, e sai um som parecido com latido."),
    dict(scene="final", cap="Resumindo: você é um peixinho medroso com uma dentadura incrível.",
         say="Resumindo: você é um peixinho medroso, com uma dentadura incrível."),
    dict(scene="final", cap="Fama de monstro, alma de sardinha.", say="Fama de monstro, alma de sardinha."),
]

# camadas 2D opcionais por cima do 3D (chips, rótulos). c.t, c.mark(i) funcionam igual.
def cardume(c):
    m1 = c.mark(1)
    c.chip(540, 330, "ANDA EM GRUPO = PROTEÇÃO", 46, YELLOW, BLACK, c.fade_in(0.6, .3), scale=c.pop(0.6, .4))
    for i, (lbl, x, y) in enumerate([("BOTO", 820, 520), ("JACARÉ", 250, 1160)]):
        c.chip(x, y, lbl, 42, RED, WHITE, c.fade_in(m1 + 0.6 + i * 0.8, .3), scale=c.pop(m1 + 0.6 + i * 0.8, .4))

def nervosa(c):
    a = c.fade_in(c.mark(0) + 2.6, .3) * (1 - c.fade_in(c.mark(1), .3))
    c.chip(540, 360, "RESPIRAÇÃO ACELERADA", 50, RED, WHITE, a, scale=c.pop(c.mark(0) + 2.6, .4))
    c.chip(540, 360, "GRUPO GRANDE = CALMA", 50, GREEN, BLACK, c.fade_in(c.mark(1), .3), scale=c.pop(c.mark(1), .4))

def cardapio(c):
    for i, (lbl, x, y) in enumerate([("PEIXES", 260, 820), ("INSETOS", 840, 640), ("FRUTAS", 300, 430), ("PLANTAS", 840, 1000)]):
        c.chip(x, y, lbl, 42, WHITE, BLACK, c.fade_in(0.6 + i * 0.6, .3), scale=c.pop(0.6 + i * 0.6, .4))

def dentes(c):
    c.chip(540, 330, "ENCAIXE DE SERRA", 50, YELLOW, BLACK, c.fade_in(0.5, .3) * (1 - c.fade_in(c.mark(1) + 0.6, .3)),
           scale=c.pop(0.5, .4))
    c.chip(540, 330, "TROCA DE UM LADO TODO", 50, RED, WHITE, c.fade_in(c.mark(1) + 0.6, .3), scale=c.pop(c.mark(1) + 0.6, .4))
    a = c.fade_in(c.mark(1) + 2.6, .3)
    c.chip(540, 1330, "DENTES NOVOS!", 50, GREEN, BLACK, a, scale=c.pop(c.mark(1) + 2.6, .4))

def late(c):
    for k in range(3):
        st = c.mark(0) + 1.8 + k * 0.5
        c.text(760 + k * 40, 620 - k * 90, "AU!", 110 - k * 10, YELLOW, c.fade_in(st, .15) * (1 - c.fade_in(st + 1.2, .3)),
               scale=c.pop(st, .3))

def final(c):
    c.chip(540, 1320, "MEDROSA, MAS AFIADA", 50, YELLOW, BLACK, c.fade_in(c.mark(1), .3), scale=c.pop(c.mark(1), .5))

if __name__ == "__main__":
    run(SEGS, globals(), out=os.environ.get("OUT", "piranha.mp4"))
