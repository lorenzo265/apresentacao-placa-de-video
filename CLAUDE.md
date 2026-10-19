# Apresentação da RTX PRO 6000 Blackwell

Apresentação cinematográfica e interativa de uma placa de vídeo NVIDIA RTX PRO 6000 Blackwell: modelo 3D desmontável, câmera que se aproxima de cada peça e uma linha de chamada até uma caixa de texto com a explicação. Idioma do conteúdo: PT-BR.

## Estrutura

- `harness/`: camada técnica (spec, modelagem, storyboard, viewer). Comece por `harness/ARCHITECTURE.md`, que é a fonte de verdade.
- `vault/`: vault Obsidian com a camada editorial (briefing, pesquisa, roteiro, ensaios). Tem o próprio `vault/CLAUDE.md`, que vale para tudo dentro de `vault/`.
- `.claude/agents/`: subagentes do harness, com o modelo de cada um no frontmatter.
- `.claude/skills/`: skills do projeto (`gpu-assembly-proposal`).

## Regras do projeto

1. **Procedência em tudo.** Toda peça e afirmação é `confirmed`, `derived`, `inferred` ou `illustrative`. Nunca apresente `inferred` como fato. Detalhes em `harness/ARCHITECTURE.md`.
2. **Sem fonte, sem fato.** Não invente números nem citações. Lacuna vira pendência.
3. **Quem cria não aprova.** `visual-qa` e `fact-checker` são sempre agentes separados de quem produziu.
4. **Gates humanos** nas fases F0, F2 e F6 (ver arquitetura).
5. **Orquestrador:** sessão principal em Fable 5.1 (`/model`). Justificativa em `harness/ARCHITECTURE.md`, seção 6.1.
6. **Vault:** use a skill `obsidian-vault-organizer` para qualquer organização dentro de `vault/`. Não mexa em `vault/.obsidian/`.
7. **Git:** um commit por mudança lógica, mensagem curta em PT-BR. Não reescreva histórico.

## Estado atual

- Placa escolhida: RTX PRO 6000 Blackwell (variante a confirmar: Workstation ou Max-Q).
- Fase atual: F0 concluída, falta F1 (pesquisa e spec).
- Pendências de briefing (público, tempo de fala, prazo) estão em `vault/CLAUDE.md`.
