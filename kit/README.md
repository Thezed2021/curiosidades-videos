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

## 3. Publicar
O mp4 vai para a branch `videos` (órfã, sobrescrita a cada dia com force-push, para o
repositório não crescer). Link público usado no Metricool:
`https://raw.githubusercontent.com/Thezed2021/curiosidades-videos/videos/<arquivo>.mp4`

## Pronúncia
Palavra falada errado? Acrescente em `LEX` dentro de `neural_tts.py` (palavra → IPA).
