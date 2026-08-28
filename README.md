# House Flipper — Platina (PT-BR)

Guia de platina do **House Flipper** (jogo base) em português, empacotado como
plugin do [Streamer Sidekick](https://github.com/ricardothezouro-debug) na
categoria `platina` (aba **Platinas**).

> Este repositório era um app desktop separado (`app.py` + CustomTkinter). Foi
> reescrito como plugin do Sidekick e o guia foi **ampliado e corrigido** — veja
> [O que mudou](#o-que-mudou-em-relação-ao-app-antigo).

| Conteúdo | Qtd. |
|---|---:|
| Passos cronológicos (5 fases) | 29 |
| Compradores, com perfil e receita | 10 |
| Troféus do jogo base | 24 |
| Casas compráveis (checklist do Game Over) | 37 |
| Slots do contador de vendas | 50 |
| Notas sobre as ordens / Perfectionist | 5 |
| Perks na ordem recomendada | 8 |
| Segredos e easter eggs | 7 |
| Imagens (retratos, ícones, plantas, capturas) | 48 |
| Fontes cruzadas | 6 |
| **Itens marcáveis no total** | **165** |

## As 10 abas

| # | Aba | O que tem |
|---|-----|-----------|
| 01 | Passo a passo | 29 passos em 5 fases: preparação, ordens, os 10 compradores, o Game Over e o fechamento. Cada passo diz o que fazer, onde, quando e **por que naquele momento**. |
| 02 | Compradores | Metade da platina. Cada card traz o **perfil** que o jogo pontua (limpeza, cor, piso, nº de cômodos, exigências) e a **receita testada** (casa, preço e itens exatos), com o retrato do comprador. |
| 03 | 24 Troféus | Nome, tier, requisito conferido e o atalho mais curto, com o ícone de cada troféu. Filtro por texto, tier e "só pendentes". |
| 04 | 37 Casas | Checklist do Game Over com preço e metragem de cada casa, e quais são casas de troféu. |
| 05 | 50 Vendas | Contador do Senior Estate Agent, com os marcos 10 e 20 destacados. |
| 06 | Ordens | Por que o Perfectionist é o troféu que mais trava platina, e como conferir no Mail Archive. |
| 07 | Perks | A ordem de perks que realmente importa (são 54 em 6 árvores; nenhum troféu exige completá-las). |
| 08 | Segredos | A sala secreta, o Knock knock, o Psychomanteum, Room 404 e as baratas. |
| 09 | Mapas / Imagens | As plantas das casas de troféu e capturas do jogo, com a fonte de cada imagem. |
| 10 | Fontes | Os 6 guias cruzados na elaboração da rota. |

## Recursos

- **Busca global** no topo: procura ao mesmo tempo em passos, compradores,
  troféus, casas e segredos, ignorando acentuação e maiúsculas. Digite
  `Chang Choi`, `sauna`, `Alone Home` ou `barata`.
- **Progresso salvo automaticamente** em
  `%APPDATA%\StreamerSidekick\platinas\house-flipper\progress.json` — fora da
  pasta do plugin, então **sobrevive a atualizações**.
- **Exportar / Importar progresso** em JSON, para levar a run para outro PC.
- **Imagens com cache em disco**: baixadas uma vez e reaproveitadas — depois da
  primeira visita, funcionam offline.

## Antes de começar (os dois passos que mais custam caro)

1. **Mude a moeda do jogo para EURO (€).** Negotiator (50.000) e Millionaire
   (1.000.000) comparam valores em euro; em outra moeda os limiares não batem
   com os guias e há relatos dos dois troféus não saírem.
2. **Desinstale as DLCs.** Perfectionist exige 100% em *todas* as ordens e
   Game Over exige vender *todas* as casas compráveis — com DLC instalada, as
   ordens e as casas das expansões entram na conta.

## O que mudou em relação ao app antigo

O guia anterior tinha 24 tarefas e citava ~16 troféus. Esta versão foi
reescrita cruzando seis fontes; as correções principais:

**Troféus que faltavam** — o app não listava `Knock, knock` (era só uma dica),
`You're doing it wrong`, `Junior Estate Agent` (10 vendas),
`Estate Agent` (20 vendas) nem a própria platina. Agora são os **24** oficiais
(1 platina, 7 ouro, 8 prata, 8 bronze).

**Requisitos corrigidos:**

| Troféu | Antes | Correto |
|---|---|---|
| Do it ASAP | "menos de 30 segundos" | **menos de 1 minuto** |
| Negotiator | "lucro máximo na Alone Home" | **ganho de 50.000 € na negociação** |
| Millionaire | "1 milhão na sala secreta da House hiding something" | **1.000.000 € ganhos no total** (a sala secreta só ajuda) |
| Mystery | "Mr. Mystery" | o nome é **Mystery** |
| Game Over | "vender todas as casas restantes" | **as 37 casas do jogo base**, listadas uma a uma |

**Compradores conferidos** — várias duplas comprador↔casa do app estavam
trocadas (por exemplo *Burned House* era atribuída ao Dolan Trusk, quando é a
casa do Gorgio Shanua; *Alleyway of Lights* não é a casa da Veronica). Agora
cada comprador traz o **perfil de preferências** — que é o mecanismo real do
leilão — mais uma receita testada e, quando as fontes divergem, a alternativa
anotada.

**A lógica da rota** — o app mandava "repetir a Turtle House para farmar" as 50
vendas. Como as 37 casas do Game Over **já contam como vendas**, a rota agora
encadeia: Game Over → 37 vendas → faltam 13 no First Office (a casa mais
barata). Também faz o *Mystery* (casa suja) **antes** do *Alpha Male*, porque os
dois usam a mesma casa e assim ela só é limpa uma vez.

**Imagens** — o app não tinha nenhuma. Agora são 48: os 10 retratos de
comprador, 23 ícones de troféu, as plantas das casas de troféu e capturas do
jogo.

## Instalação

Pelo Streamer Sidekick: aba **Platinas** → card **“+”** → **House Flipper —
Platina**.

## Rodar standalone (sem o Sidekick)

```bash
pip install -r requirements.txt
set PYTHONPATH=src
python -m platina_house_flipper
```

## Entrada para o `platinas.json` do Sidekick

Também disponível no arquivo [`platinas-entry.json`](platinas-entry.json):

```json
{
  "id": "house-flipper",
  "name": "House Flipper — Platina",
  "description": "Guia PT-BR do jogo base: rota cronológica, os 10 compradores com receita, as 37 casas e os 24 troféus.",
  "repo": "ricardothezouro-debug/House-fliper-assistente-de-platina",
  "ref": "master",
  "version": "1.0.0",
  "src_subdir": "src",
  "module": "platina_house_flipper.module",
  "accent": "#4F8DFF",
  "icon": "src/platina_house_flipper/assets/brand/icon.png",
  "min_sidekick_version": "0.6.0",
  "changelog": "Primeira versão como plugin do Sidekick."
}
```

## Estrutura

```
src/platina_house_flipper/
  __init__.py
  module.py          contrato do plugin: module_info() / build_page() / help_text()
  page.py            a página: as 10 abas, busca global, filtros e progresso
  guide_data.py      TODO o conteúdo do guia (único arquivo específico do jogo)
  progress.py        formato das chaves de progresso
  storage.py         progresso em %APPDATA% (genérico do template)
  image_loader.py    download de imagens com cache em disco (genérico do template)
  __main__.py        execução standalone
  assets/brand/icon.png
```

### Diferenças em relação aos arquivos genéricos do template

Duas mudanças em `image_loader.py`, as mesmas do guia de DREDGE:

1. **Cabeçalhos de navegador** nas requisições — vários hosts de wiki e de guia
   devolvem 403 para um `User-Agent` genérico sem `Referer`/`Sec-Fetch-*`.
2. **`ImageLoader.shutdown()`**, chamado no `aboutToQuit` e no `closeEvent` da
   página. Sem isso, fechar o app com um download em andamento destrói um
   `QThread` ainda rodando e o Qt aborta o processo.

`page.py` também é próprio: o template genérico renderiza uma lista simples de
troféus, o que descartaria 9 das 10 abas. O contrato do `PLUGIN_STANDARD.md`
(`module_info()` / `build_page()`) e os `objectName`s do design system são
respeitados, e as dependências são só PySide6 + stdlib.

## Créditos

Guia não oficial, sem vínculo com a Frozen District / Empyrean. As imagens são
de terceiros e estão creditadas na aba **Mapas / Imagens**; as fontes da rota
estão na aba **Fontes**.
