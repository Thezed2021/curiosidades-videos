import os, sys
sys.path.insert(0, os.environ.get("KIT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from engine import *
from story import *
A = dict(skin=PELE[3], hair=(30,25,20), hair_style="curto", shirt=(200,70,60), pants=(40,45,70), extras=["barba"])
B = dict(skin=PELE[1], hair=(120,60,30), hair_style="longo", shirt=(90,170,120), pants=(50,50,60), extras=["brinco"])
C = dict(skin=PELE[0], hair=(230,200,90), hair_style="rabo", shirt=(250,200,60), pants=(60,60,90), extras=["oculos","mochila"])
D = dict(skin=PELE[5], hair=(20,20,20), hair_style="cacheado", shirt=(60,60,70), pants=(30,30,40), extras=["gravata"])
SEGS=[dict(scene=n, cap="teste", say="teste") for n in ["a","b","c","d"]]
def a(c):
    cidade(c, noite=True); chuva(c)
    person(c, 300, 1380, 0.85, A, "medo", "andando", c.t)
    person(c, 780, 1380, 0.85, B, "surpreso", "aponta", c.t)
def b(c):
    cidade(c, fogo=True)
    person(c, 540, 1380, 1.0, C, "determinado", "correndo", c.t)
def c(c_):
    quarto(c_)
    person(c_, 330, 1380, 0.85, D, "triste", "maos_rosto", c_.t)
    person(c_, 760, 1380, 0.85, B, "apaixonado", "abraco", c_.t)
def d(c):
    escritorio(c)
    person(c, 330, 1380, 0.85, A, "raiva", "celular", c.t); person(c, 760, 1380, 0.8, C, "cansado", "parado", c.t)
    ep_card(c, "Plantão", 3, 10)
    continua(c, 0.5)
run(SEGS, globals(), out="t.mp4")
