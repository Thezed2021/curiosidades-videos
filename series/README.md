# Séries da noite (19h30)

Histórias de ficção em episódios, com um personagem principal por série.

## Regras
- Cada série tem **no máximo 10 episódios** (pode ter menos se a história fechar bem).
  Quando acabar, a próxima execução cria uma série NOVA com outro personagem e outro gênero.
- Gêneros variados e sem se prender a uma lista: apocalipse zumbi, trabalho, amor, vida dando
  certo, fracasso e recomeço, mistério, suspense, ficção científica, comédia, drama de família,
  sobrevivência, viagem no tempo, golpe/assalto, escola, esporte, sobrenatural leve...
  Evite repetir o gênero das 2 séries anteriores.
- Cada episódio: NO MÍNIMO 60 s (alvo 65–90 s), começa com "Anteriormente..." curto (1 frase, exceto no ep. 1),
  tem conflito, virada, e termina com GANCHO forte para o próximo + tela "CONTINUA...".
  O último episódio fecha a história (pode deixar uma pontinha) e anuncia "Nova série amanhã".
- Ficção 100% inventada: sem pessoas reais, marcas reais ou fatos reais distorcidos.
  Adequada às regras do YouTube/TikTok/Instagram: sem gore explícito, sem sexo, sem ódio,
  sem incentivar automutilação ou crimes. Tensão e emoção, sim; violência gráfica, não.
- CLIMA da série (defina `CLIMA = "..."` no script; fica igual em todos os episódios):
  sombrio (terror, zumbi, sobrenatural) · suspense (mistério, investigação) · acao (perseguição,
  sobrevivência, golpe) · romantico (amor) · comedia · inspirador (vida dando certo, superação) ·
  drama (perda, fracasso, família). Ele muda SÓ a trilha: a voz fica sempre natural, sem efeitos.
- Narrador: voz pm_santa. Falas de personagens podem usar pm_alex (homem) ou pf_dora (mulher)
  com o campo `voice` do SEG. Mantenha sempre a MESMA voz para o mesmo personagem.
- Visual: `kit/story.py` (person, cidade, quarto, escritorio, chuva, flash, ep_card, continua).
  O LOOK de cada personagem fica salvo no arquivo da série e é copiado igual em todo episódio.

## Arquivos
- `atual.md` — aponta a série em andamento (nome do arquivo) ou "nenhuma".
- `NN-slug.md` — bíblia da série, criada no episódio 1:

```
# <Título da série>
Gênero: ...           Clima: sombrio|suspense|acao|romantico|comedia|inspirador|drama
Total planejado: N episódios (≤10)
Premissa: 2–3 frases.
Personagens:
- <Nome> (protagonista, voz pf_dora): personalidade...
  LOOK = dict(skin=PELE[2], hair=(..), hair_style="...", shirt=(..), pants=(..), extras=[...])
Arco planejado (1 linha por episódio, pode ajustar no caminho):
1. ...
Episódios publicados:
- Ep. 1 (AAAA-MM-DD): resumo em 2 frases. Gancho: ...
```

## Séries concluídas
(nenhuma ainda)
