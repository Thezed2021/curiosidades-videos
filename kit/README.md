# Kit de vídeos — Curiosidades do Mundo

Usado pela tarefa diária. Tudo roda num ambiente Linux novo a cada execução.

## 1. Instalar a voz (≈1–3 min)
```bash
TTS_ROOT=$HOME/tts bash kit/setup.sh
```
Compila o espeak-ng (fonemas) e baixa o Kokoro v1.0 + voz `pm_santa`, tudo do GitHub.
Termina com um teste de voz em /tmp/teste_voz.wav.

## 2. Fazer o vídeo
Copie `kit/exemplos/flamingo.py` para uma pasta de trabalho, troque SEGS e as cenas.
- `cap` = legenda (dígitos ok); `say` = fala (números por extenso).
- Segmentos seguidos com a mesma `scene` formam uma cena só; use `c.mark(i)` para
  revelar elementos quando começa a fala do i-ésimo segmento da cena.
- Mantenha elementos importantes acima de y≈1450 (legenda fica em y≈1560) e títulos
  em y≈300–450 sem encostar em desenhos.
- Primitivas em `engine.Ctx`: bg, circle, rect, line, arrow, poly, text, chip, bar,
  counter, glow; easing: ease, ease_out, ease_back, fade_in, pop.

```bash
cd pasta && TTS_ROOT=$HOME/tts STILLS=2,8,15,25,35,45 python3 video.py   # quadros-chave
# olhe stills/contact.png, corrija sobreposições
TTS_ROOT=$HOME/tts OUT=video.mp4 python3 video.py                        # render (~1,5 min)
```
O render já verifica (ffprobe, volumedetect) e grava check/final_contact.png — olhe.

### Vídeos 3D "Você é..." (noite)
`CENA3D = "cena3d.js"` no script ativa o 3D (three.js no Chromium, offline). Regras e
dicas em `noite3d/README.md`; exemplo completo em `exemplos/3d_piranha/`.

### Histórias (séries — pausadas)
`from story import *` traz personagens (`person`, com humor e pose), cenários (`cidade`,
`quarto`, `escritorio`, `ceu`), efeitos (`chuva`, `flash`) e telas (`ep_card`, `continua`).
Veja `kit/exemplos/personagens_demo.py`. Vozes por fala: campo `voice` no SEG
(`pm_santa` narrador, `pm_alex` homem, `pf_dora` mulher). Regras das séries: `series/README.md`.

### Clima (voz + trilha)
`CLIMA = "sombrio"` no script (ou `run(..., clima=...)`): neutro, sombrio, suspense, acao,
romantico, comedia, inspirador, drama. Muda só o estilo da trilha; a voz fica sempre natural
(VOICE_FX = False no engine, decisão do canal). Vídeos de curiosidade usam neutro (padrão).

### Título e capa (obrigatório em todo vídeo)
No script defina `TITULO = "..."` (3–7 palavras, chamativo; é o título que aparece SOZINHO na
tela no 1º segundo e na capa), opcional `SUBTITULO` (ex.: "Último Ônibus • Ep. 3") e uma função
`capa(c)` que desenha o visual principal do tema SEM textos, concentrado em y 950–1650 (o título
fica no alto). Planeje a 1ª cena para que seus textos entrem só depois de ~1,2 s.
O render gera `<out>_capa.jpg` (e STILLS gera `stills/capa.jpg` — OLHE a capa também).
Veja `exemplos/flamingo.py`.

### Pessoas reais (regra do canal)
Nunca use foto de pessoa real (nem baixada da internet, nem por link) e nunca desenhe o rosto
de uma pessoa real imitando a aparência dela. Para citar alguém real, use
`ficha_pessoa(c, "Nome", "quem é", "1879–1955")` (de `story.py`) e ilustre o CONTEXTO:
mapa, ano, objetos, lugares, invenção, linha do tempo. Personagens de ficção (`person`)
nunca representam pessoas reais.

## 3. Publicar
O mp4 e a capa (.jpg) vão para a branch `videos` (órfã, sobrescrita a cada dia com force-push, para o
repositório não crescer). Link público usado no Metricool:
`https://raw.githubusercontent.com/Thezed2021/curiosidades-videos/videos/<arquivo>.mp4` (e `.jpg`
da capa, usado em `videoThumbnailUrl` no Metricool)

## Pronúncia
Palavra falada errado? Acrescente em `LEX` dentro de `neural_tts.py` (palavra → IPA).
