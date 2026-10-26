# Log de organização

## 2026-10-19
- Vault criado com a estrutura padrão: `00-Inbox` a `05-Ensaio`, `Templates`, `_arquivo`, `Painel.base` e `CLAUDE.md`.
- Briefing inicial, decisões do projeto e plano de pesquisa em `01-Briefing/`.
- Roteiro provisório com 12 seções em `03-Roteiro/`, todas com `status: rascunho` e sem fontes.
- Pendências: público, tempo de fala, prazo e variante da placa (ver `CLAUDE.md`).

## 2026-10-19 (atualização)
- Preenchidos público, variante (Workstation Edition) e prazos no `CLAUDE.md` do vault e no briefing. Duração do seminário segue pendente.
- Criada `01-Briefing/Requisitos da disciplina.md` com o enunciado resumido, datas, tabela de cobertura do roteiro v1 e proposta de roteiro v2.
- Roteiro v1 não foi alterado. A reestruturação aguarda confirmação.

## 2026-10-19 (roteiro v2)
- Roteiro v2 confirmado. As 12 seções do v1 foram movidas para `_arquivo/roteiro-v1/` sem alteração. Criadas 14 seções novas em `03-Roteiro/`.
- Novas propriedades nas seções: `nivel`, `itens_enunciado`. `Painel.base` filtra por `03-Roteiro/`, então o arquivo não aparece.
- Duas fontes lidas e registradas em `02-Pesquisa/`. `Requisitos da disciplina` agora traz a cobertura do v2, o status das fontes e os achados da primeira rodada.
- Proposta formal de 2026-10-26 rascunhada em `01-Briefing/Proposta formal.md`.

## 2026-10-19 (fontes de instruções)
- Cinco fontes novas em `02-Pesquisa/`: PTX ISA, CUDA Binary Utilities, compute capability, artigo da Volta e artigo da Blackwell (GB203).
- Seção `08` reescrita com o que é confirmado, o que foi observado em experimento, o que é derivado e a análise RISC ou CISC. Seções `06`, `07`, `09` e `12` ganharam os fatos novos.
- Exemplo SAXPY compilado para `sm_120` em `harness/examples/saxpy/`.
- Definidos no `CLAUDE.md` da raiz os tipos de modelo por skill e por agente (A fable, B opus, C sonnet, D haiku), com regras de escalada.

## 2026-10-19 (auditoria das fontes de instruções)
- O `fact-checker` reabriu as fontes e achou 2 erros que bloqueavam (largura da instrução declarada no apêndice do Binary Utilities; operando de constante em instruções aritméticas) e 13 ajustes. Todos corrigidos. Relatório em `harness/qa/fact-check-isa.md`.
- Seção `08` agora com `status: revisar` (a classificação RISC ou CISC precisa de revisão humana). Notas de PTX, Binary Utilities, Volta e Blackwell (GB203) passaram a `status: pronto`; a nota da Ampere segue rascunho, sem auditoria.

## 2026-10-26 (proposta e rodada de fontes)
- PDF da proposta gerado em `entregas/proposta-2026-10-26/` (grupo Warp 32, 5 integrantes) a partir de [[Proposta formal]]. Estilo pedido pelo grupo: Arial 12, fundo branco, só tópicos.
- Quatro fontes novas em `02-Pesquisa/`: guia CUDA, driver aberto (MMU), driver aberto (interrupções e GSP) e teardown com conector de energia. Todas `status: rascunho`, em auditoria. Autoria do artigo da Ampere conferida no arXiv.
- Seções `02`, `03`, `05`, `07`, `09`, `10`, `11` e `12` ganharam as fontes novas em `fontes`. `10` e `11` têm um aviso de síntese pendente (tipo A: Fable ou Opus). Nenhum link quebrado.
- `Requisitos da disciplina`, `Decisões do projeto`, `Plano de pesquisa` e `Briefing` atualizados. Pendências abertas: grupo de 5 contra o limite de 4 do enunciado, e divisão de tarefas.
- Versão direta da proposta em .docx (2 páginas: dados do grupo, proposta, tarefas, cronograma e objetivo), gerada por `entregas/proposta-2026-10-26/build_docx.js` a partir de `grupo.json`. O PDF longo continua como versão detalhada.
