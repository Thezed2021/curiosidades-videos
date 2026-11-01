# Noite — vídeos 3D "Você é..." (19h30)

Formato de humor em segunda pessoa: o narrador diz ao espectador o que ele É e explica
fatos reais com piadas. Ex.: "Você é uma piranha! Dentes afiados, fama de vilã de filme...
e um medo enorme de tudo." Referência pronta: `kit/exemplos/3d_piranha/`.

## Conteúdo
- Tema do canal (curiosidades), escolhendo algo que renda personagem engraçado: animais
  (sem repetir o bicho da manhã do mesmo dia), partes do corpo (um neurônio, uma hemácia, o
  apêndice), coisas da natureza (uma gota de chuva, um raio, um vulcão), comida (um grão de
  café, uma pimenta), espaço (um cometa, Plutão), objetos do dia a dia, profissões antigas
  genéricas ("você é um carteiro de 1850"). NUNCA pessoas reais nem personagens de terceiros.
- Fatos 100% verificados: ≥3 fontes lidas, números cruzados, ressalvas onde divergem.
  O humor vem do jeito de contar (exageros, comparações do dia a dia, ironia), nunca de
  inventar fato. Nada de piada ofensiva com grupos de pessoas.
- Estrutura (55–70 s): "Você é um(a) X!" + 1 frase cômica que contradiz a fama →
  3 a 5 fatos surpreendentes, cada um com uma piada → resumo engraçado → CTA
  "Segue pra descobrir o que você vai ser amanhã!".
- Voz: narrador pm_santa natural (sem efeitos). `CLIMA = "comedia"`.

## Visual 3D (three.js, renderizado no Chromium; ~0,6 s por quadro → ~20 min para 60 s)
- `CENA3D = "<caminho>/cena3d.js"` no script Python ativa o modo 3D: cada `scene` dos SEGS
  vira uma cena 3D (`update(api, c)` com `c.name`, `c.t`, `c.d`, `c.mark(i)`), e funções
  Python com o mesmo nome desenham por cima (chips, rótulos, "AU!").
- QUALIDADE DE MODELAGEM: o bicho tem de ser reconhecível pela anatomia real (silhueta, proporções,
  boca/dentes, nadadeiras/patas/asas no lugar certo, cores por região). Veja `makePiranha` em lib3d.js
  como padrão: esfera deformada por um perfil (alto/baixo/achatado), cores por vértice, mandíbula
  articulada e dentes no formato e posição reais. Os olhos podem ser cartoon; o resto, fiel.
  Para animais novos, crie uma função `makeX` no cena3d.js seguindo essa técnica (não use
  formas genéricas tipo "bola com olhos" para bichos). Faça STILLS de perto e confira.
- Monte os personagens com `kit/r3d/lib3d.js`: makePiranha, makeFish, makeQuadruped, makeBird, makeBlob
  (célula, gota, planeta, vírus...), eye(), brow(), mouth(), stage() (palco com céu em degradê,
  chão: agua/grama/areia/neve/espaco/lab), bubbles(). Crie formas novas com sphere, cone,
  cyl, capsule, box, torus. Personagem principal SEMPRE com olhos grandes e expressão
  (bravo/medo/feliz) que muda conforme a fala.
- A tela é vertical: com a câmera a ~7 de distância só cabem ~±1,2 na horizontal e ~±2 na
  vertical. Empilhe as coisas na vertical; nada importante fora disso.
- Defina também a cena `capa` no .js (personagem em pose forte, sem textos) e `TITULO`.
- Sempre STILLS primeiro e OLHE (enquadramento, objetos fora do quadro, legibilidade).
- Render em blocos (retomável): rode `RENDER3D_MAX_S=500 OUT=x.mp4 python3 x.py` em primeiro
  plano repetidamente. Se sair com código 3 ("3D PARCIAL"), rode de novo: ele pula os quadros
  prontos. Quando todos existem, ele monta o MP4. Se mudar a cena 3D depois do render, apague
  a pasta frames3d/ antes.

## Temas já feitos
- 2026-11-01 — Você é uma piranha (medrosa, cardume, troca de dentes, late) — publicado 01:31
