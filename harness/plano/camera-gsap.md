# Câmera, desmontagem e apresentação das peças (sessão de câmera)

Dono: sessão de câmera (branch `claude/apresentacao-camera-gsap`). Texto dos beats: sessão de roteiro conciso. Decisões que mudam a lista de beats vão com cópia para a orquestradora.

## 1. Decisões do autor (2026-11-11)

| # | Proposta | Resposta do autor |
|---|---|---|
| 1 | Câmera em arco orbital com GSAP | Concordou. Manter a explosão como é hoje, e **poder tirar as peças da posição da placa** para mostrá-las melhor ao público (não ficar preso ao eixo de explosão) |
| 2 | Enquadramento automático | Sim. Pediu também **luz e contraste melhores e fundo mais claro** |
| 3 | Coreografia da desmontagem (parafusos, descolar, viajar, escalonar) | "Top, podemos experimentar" |
| 4 | Resolver a base (carcaça com a grade da face B) | Plano aprovado. Pediu pesquisa com agentes Sonnet nas placas irmãs (5090, 5080, 50xx e 40xx FE, RTX 6000 Ada) para fechar o que não sabemos. Relatório em `pesquisa-placas-irmas.md` |
| 5 | Câmera parada durante o texto | Aprovado |

## 2. Arquitetura

- **Câmera orbital.** `timeline.js` interpola o alvo em linha reta, e a posição em coordenadas esféricas em torno dele: distância em log, azimute pelo menor ângulo, elevação. Assim a câmera contorna a placa em vez de atravessá-la. `seek(t)` continua determinístico (tudo vem da timeline GSAP pausada).
- **Desmontagem coreografada.** Arquivo `src/desmontagem.json`, que complementa o `explode_cad` do GLB sem refazê-lo:
  - por estágio: fixadores (giram e saem pelo eixo antes da peça), "descolar" (1,5 mm no início), viagem com `expo.out` e escalonamento entre as peças do mesmo estágio;
  - E8 (`inferred`, com aviso na tela): a carcaça com a face B sai para -z sem levar os filhos (o viewer compensa), o que deixa as aletas e a câmara de vapor à vista.
- **Vitrine.** Num beat, uma peça pode sair da posição explodida para um ponto de apresentação diante da câmera e girar para mostrar a melhor face. O resto fica ao fundo. A posição e a rotação de vitrine são `illustrative`, ou seja, apresentação e não montagem; a ordem de desmontagem continua a do teardown.
- **Herói.** Vista explodida completa, com volta lenta em torno da placa, no fim do E8 e antes do mergulho no chip.

## 3. Procedência dos movimentos

- Ordem E1 a E7: `confirmed` (teardown da própria placa). As peças saem pela **face B** (lado oposto aos ventiladores, -z). A carcaça, com a grade da face B e o cooler, fica como corpo único.
- E8 e a abertura da carcaça: `inferred`, porque não há foto do interior. Ver a pesquisa das placas irmãs.
- Giro de parafuso, descolar, vitrine e herói: `illustrative` (gesto de apresentação).

## 4. Combinado com o roteiro (pendente)

- A desmontagem é um beat com vários estágios e uma só fala (campo `explode_seq`), não uma sequência de beats mudos.
- Duração mínima da entrada de câmera: 2,0 s para troca pequena e 3,0 s para troca grande. Cada estágio da sequência dura cerca de 2,2 s.
