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

## 2026-11-09 (hardware físico e planos v0.2)
- Oito fontes novas em `02-Pesquisa/` sobre a placa física: datasheet oficial, teardown da própria placa (Gamers Nexus), três análises de terceiros e três fontes da RTX 5090 Founders Edition. Todas com `status: rascunho`, lidas por resumo automático.
- `Plano de pesquisa` e `Requisitos da disciplina` atualizados com o status dessas fontes. Novo alvo 8 (normas de conectores).
- Fora do vault: `harness/STATUS.md` (acompanhamento), `harness/design/assembly-plan.md` e `harness/story/video-plan.md`.
- Nenhuma nota do roteiro foi alterada. Pendências que seguem abertas: duração do seminário, divisão de trabalho, revisão da seção `08`, fontes das seções `10` e `11`.

## 2026-11-09 (auditoria do hardware físico)
- O `fact-checker` reabriu as fontes principais e não aprovou na primeira passada: 3 achados que bloqueavam e 16 ajustes. Relatório em `harness/qa/fact-check-fisico.md`.
- Notas de Jon Peddie, Puget e sabareesh passaram de `procedencia: confirmed` para `derived` (revisores que não são fonte oficial nem teardown). A decisão de ampliar `confirmed` ficou para o grupo.

## 2026-11-09 (artigo entregue, MMU, interrupções, normas e fotos)
- Artigo do grupo (Warp 32) entregue como documentação escrita. Revisão em `harness/qa/revisao-artigo.md`.
- 27 fontes novas em `02-Pesquisa/`: 10 de MMU, interrupções e limites (as que o artigo cita e o código aberto do driver) e 17 de normas (conector de 16 pinos, slot PCIe, DisplayPort, GDDR7). Todas com `status: rascunho`.
- Seções `10` e `11` deixaram de estar sem fonte. Seção `08` ganhou a evidência da lista oficial de instruções e uma conclusão revisada, ainda em `status: revisar`. Seções `07` e `12` ganharam os limites oficiais (255 registradores por thread, 48 warps por SM).
- Duração do seminário registrada no `CLAUDE.md` do vault, no briefing e nas decisões: 15 a 20 minutos.
- Pendências que seguem abertas: aprovação da conclusão da seção `08`, divisão da fala, auditoria da segunda leva de fontes.

## 2026-11-09 (proposta entregue)
- Recebido o PDF da proposta entregue em 26/10 (2 páginas). Arquivado em `01-Briefing/Proposta entregue 2026-10-26.pdf` e transcrito em `01-Briefing/Proposta formal.md`, com `status: pronto`.
- O rascunho longo de 19/10 foi movido para `_arquivo/Proposta formal - rascunho de 2026-10-19.md`, sem apagar nada. Os links `[[Proposta formal]]` continuam valendo e agora apontam para a versão entregue.
- A divisão da fala do seminário passou a seguir a definição de tarefas da proposta.

## 2026-11-09 (auditoria da segunda leva)
- O `fact-checker` não aprovou na primeira passada: 7 achados que bloqueavam, 13 ajustes e 9 notas. Relatório em `harness/qa/fact-check-segunda-leva.md`.
- O principal: a revisão do artigo acusava quatro afirmações que têm fonte oficial (quatro escalonadores por SM, divergência, compilação do PTX pelo driver, GSP em RISC-V). Revisão reescrita.
- Notas do roteiro corrigidas: `06` e `07` (Fig. 5 do whitepaper: quatro blocos por SM, quatro bancos de 16.384 registradores), `08` (evidências e frase do seminário), `10` (conta dos bits por tamanho de página, GB202 listado na família GB20x), `11` (interrupção legada, falhas de página, GSP, e a leitura sobre os SMs marcada como análise do grupo).

