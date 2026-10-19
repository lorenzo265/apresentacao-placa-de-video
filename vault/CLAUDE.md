# Vault: apresentação da RTX PRO 6000 Blackwell

Regras para o agente que organiza este vault (skill `obsidian-vault-organizer`). Este arquivo vale para tudo dentro de `vault/`.

## Projeto

- **Tema:** tour 3D interativo e cinematográfico de uma placa NVIDIA RTX PRO 6000 Blackwell (Workstation Edition), desmontada em níveis, com explicação extensa de como cada parte funciona.
- **Contexto:** trabalho de Arquitetura da disciplina de Organização e Arquitetura de Computadores, em grupo de até 4. O enunciado cobra registradores, instruções, CISC/RISC, MMU, interrupções, gerenciamento de memória, pipeline e cache. Ver [[Requisitos da disciplina]].
- **Idioma:** PT-BR.
- **Entregável:** viewer web (Three.js) gerado pelo harness em `../harness/`, mais um vídeo opcional do tour. O vault guarda o conteúdo editorial que alimenta esse viewer.

## Dados do briefing

| Item | Valor |
|---|---|
| Público | Estudante de computação e o professor. Rigor de engenharia, explicado para um estudante acompanhar |
| Profundidade e quantidade de conteúdo | Sem limite definido pelo grupo |
| Duração do seminário | **pendente** (perguntar ao professor) |
| Prazos | 2026-10-26 proposta, 2026-11-09 texto, 2026-11-16 seminário |
| Variante da placa | Workstation Edition |

Enquanto a duração do seminário estiver pendente, o agente não avisa sobre estouro de tempo (rotina 2 da skill). Os prazos das entregas estão em [[Requisitos da disciplina]].

## Regras específicas deste vault

1. **Procedência.** Toda nota de seção tem `procedencia_esperada` (`confirmed`, `derived`, `inferred` ou `illustrative`). Afirmações sobre peças `inferred` usam linguagem de probabilidade. Detalhes em `../harness/ARCHITECTURE.md`.
2. **Sem fonte, sem fato.** Número ou característica da placa só entra numa nota com fonte linkada em `fontes`. Sem fonte, vira pendência visível.
3. **Ligação com o harness.** Cada nota de `03-Roteiro/` tem `part_id`, igual ao `id` da peça em `design/assembly.json`. Não renomeie `part_id` sem avisar.
4. **Notas de fonte** (`02-Pesquisa/`): resumo com palavras próprias, 2 a 5 pontos úteis, link e data de acesso. O trecho bruto fica em `../harness/spec/sources/`, não aqui.
5. **Textos finais do viewer** ficam em `../harness/content/pt-BR/` e nascem das notas do roteiro. A nota do vault é a fonte editorial.
6. Não mexa em `.obsidian/`.
7. **Cobertura do enunciado.** O roteiro precisa cobrir cada item exigido pelo professor. Quando um item não existir na GPU ou não for público, a nota diz isso de forma explícita, com a razão. Atualize a tabela de cobertura em [[Requisitos da disciplina]] a cada mudança no roteiro.
