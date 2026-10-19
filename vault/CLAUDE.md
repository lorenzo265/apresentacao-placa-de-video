# Vault: apresentação da RTX PRO 6000 Blackwell

Regras para o agente que organiza este vault (skill `obsidian-vault-organizer`). Este arquivo vale para tudo dentro de `vault/`.

## Projeto

- **Tema:** tour 3D interativo e cinematográfico de uma placa NVIDIA RTX PRO 6000 Blackwell, desmontada peça a peça, com explicação extensa de como cada parte funciona.
- **Idioma:** PT-BR.
- **Entregável:** viewer web (Three.js) gerado pelo harness em `../harness/`, mais um vídeo opcional do tour. O vault guarda o conteúdo editorial que alimenta esse viewer.

## Pendências de briefing (preencher e remover daqui)

| Item | Valor |
|---|---|
| Público | **pendente** |
| Tempo de fala / duração do tour | **pendente** |
| Prazo | **pendente** |
| Variante da placa | **pendente** (Workstation Edition ~600 W ou Max-Q ~300 W) |

Enquanto estes campos estiverem pendentes, o agente não deve avisar sobre estouro de tempo (rotina 2 da skill) e não deve preencher `prazo` nas notas.

## Regras específicas deste vault

1. **Procedência.** Toda nota de seção tem `procedencia_esperada` (`confirmed`, `derived`, `inferred` ou `illustrative`). Afirmações sobre peças `inferred` usam linguagem de probabilidade. Detalhes em `../harness/ARCHITECTURE.md`.
2. **Sem fonte, sem fato.** Número ou característica da placa só entra numa nota com fonte linkada em `fontes`. Sem fonte, vira pendência visível.
3. **Ligação com o harness.** Cada nota de `03-Roteiro/` tem `part_id`, igual ao `id` da peça em `design/assembly.json`. Não renomeie `part_id` sem avisar.
4. **Notas de fonte** (`02-Pesquisa/`): resumo com palavras próprias, 2 a 5 pontos úteis, link e data de acesso. O trecho bruto fica em `../harness/spec/sources/`, não aqui.
5. **Textos finais do viewer** ficam em `../harness/content/pt-BR/` e nascem das notas do roteiro. A nota do vault é a fonte editorial.
6. Não mexa em `.obsidian/`.
