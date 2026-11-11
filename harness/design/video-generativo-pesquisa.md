# Vídeo generativo para o tour: Higgsfield e alternativas

Pesquisa de 2026-11-10. Só leitura de documentação e testes publicados; nenhuma conta criada, nenhuma chave usada, nada gasto. Procedência desta nota: o que está em "Lido na fonte" veio de página aberta; "Terceiros" veio de blog, agregador ou concorrente; "Não verificado" é o que não deu para confirmar.

## 1. Resposta curta

**Higgsfield: em parte, e não com a garantia que o projeto exige.**

- Existe vídeo para vídeo no Higgsfield, mas ele é guiado por preset e prompt. A documentação da API do restilizador (`genjutsu/restyle`) lista só cinco entradas: `video_url`, `preset_id`, `image_urls`, `prompt`, `resolution`. **Não há parâmetro de profundidade, contorno, máscara, seed, duração ou fps.** O esquema recusa campos extras (`additionalProperties: false`). Ou seja, não há controle estrutural explícito: a forma é "preservada" porque o modelo copia o vídeo de entrada, não porque nós a imponhamos.
- A própria documentação de ferramentas do Higgsfield avisa que rostos, texto e texturas finas "podem ser reconstruídos de forma imprecisa". Para o nosso caso (grades com lâminas de 1,5 mm, pás, texto pequeno, contagem de componentes) isso é o ponto fraco.
- Não achei nenhum teste publicado, de terceiros, com objeto técnico ou produto passando por esse modo. A evidência de fidelidade é só da marca. Tudo o que se sabe de fidelidade fina vem de avisos genéricos.

**Melhor alternativa para controle de forma:** Wan 2.2 Fun Control (ou Wan 2.1 VACE) com profundidade e contorno por quadro, rodando em ComfyUI. É o único caminho documentado em que o mapa por quadro governa a forma. Exige GPU (24 GB testada pela documentação oficial; não temos GPU aqui, então seria GPU alugada). Entre as APIs prontas, **Luma Modify Video em modo `adhere`** é a que tem um botão explícito de aderência à fonte e preço claro.

**Comparação com o Blender:** o render de raios mantém câmera, forma, texto e contagem exatos, porque é a nossa geometria. Medi 61 s por quadro 1080p a 32 amostras e 186 s a 128 amostras, em 4 núcleos de CPU, numa cena de produto simples. É lento, mas totalmente determinístico, sem custo e sem conta.

**Regra de procedência:** qualquer quadro passado por IA generativa vira `illustrative`, mesmo que o contorno bata. Não entra em beat que explica.

## 2. Higgsfield: o que existe hoje

Lido na fonte (docs.higgsfield.ai e higgsfield.ai, acessadas em 2026-11-10), salvo indicação.

| Modo | Entrada aceita | Duração | Resolução | Controle de câmera / estrutura | Preço | API |
|---|---|---|---|---|---|---|
| Genjutsu Restyle (`/higgsfield/genjutsu/restyle/v1.0`) | vídeo (até 200 MiB), `preset_id` obrigatório, até 5 imagens, prompt | fonte de 4 a 30 s; acima de 30 s usa só os 30 primeiros; saída "pode diferir" da fonte em duração e fps | 480p, 720p (padrão), 1080p | nenhum parâmetro de profundidade, contorno, seed, aspecto ou fps | não consta na doc; cobrança por segundo de fonte arredondado para cima | sim |
| Genjutsu Motion Transfer (`.../motion-transfer/v1.0`) | vídeo + 1 a 8 imagens + prompt | 4 a 30 s | 480p, 720p, 1080p | transfere movimento de um vídeo para outro sujeito ou cena; "câmera e enquadramento como filmados" segundo o blog da marca | 15 s: 45 / 105 / 300 créditos (480p / 720p / 1080p), cerca de US$ 2,21 / 5,15 / 14,70 a US$ 49 por 1.000 créditos (blog Higgsfield, preços de 2026-11-02) | sim |
| Genjutsu Object Swap (`.../object-swap/v1.0`) | vídeo + imagens de referência | 4 a 30 s | até 1080p | troca objeto mantendo o resto | 15 s: 48 / 112 / 320 créditos | sim |
| Kling 3.0 Omni Edit e FLUX 3 Video Edit (restilização por prompt na interface) | vídeo + prompt | não declarado na página | não declarado | a página diz que preserva "movimento e composição"; não cita profundidade nem contorno | sem preço na página | não confirmado |
| Seedance 2.5 Edit | clipe + prompt ou área marcada ("Draw to Edit") | não declarado | 720p citado | edição por região | não listado | não confirmado |
| Depth Map | vídeo | não declarado | não declarado | **gera** mapa de profundidade; a documentação não diz que ele alimente a restilização | 21 créditos para 15 s em 720p | só interface confirmada |
| Cinema Studio 4.0 / Kling 3.0 / Veo 3.1 / Seedance / Wan / MiniMax | texto, imagem, quadros inicial e final (conforme modelo) | 3 a 30 s conforme modelo (comparativo da marca, 2026-10-20) | 480p a 4K conforme modelo | Cinema Studio: mais de 30 presets de câmera + prompt; "não garante precisão quadro a quadro" | varia; "mais caro" no 1080p | API pública mostra 480p a 720p e 4 a 30 s para Cinema Studio |
| DoP (modelo próprio) | uma imagem + preset de câmera; segundo a terceiros aceita quadro final | 5 s citado por agregador | até 2K segundo terceiros | presets de zoom, dolly, pan, orbit etc. | Lite 5 / Turbo 16 / Preview 23 créditos (agregador, não verificado) | endpoint `higgsfield-ai/dop/preview` listado |

Notas de procedência da tabela:
- Preços em dólar partem de US$ 49 por 1.000 créditos (plano Plus, segundo a marca). O preço da API fica "no console" (console.higgsfield.ai, exige login) e **não consegui ler**. O preço da restilização (`restyle`) não está documentado em lugar nenhum que eu tenha aberto.
- Cobrança por tentativa: a página de ferramentas diz que "cada operação é cobrada separadamente e novas tentativas aumentam o total".
- Sobre a pergunta de quanto vale a geração base de terceiros (Kling, Veo, Wan, Seedance): o comparativo da marca de 2026-10-20 diz que o Wan 3.0 **não** tem restilização por vídeo de referência (diferente das versões anteriores), e que o Seedance 2.5 aceita até 10 clipes de entrada.
- Autenticação da API: cabeçalho `Authorization: Key ID:SECRET`, chaves criadas no Console. Saídas ficam disponíveis por pelo menos 7 dias.

### Termos de uso (versão de 2026-10-23)
- Você responde pelo que envia (3.1) e declara que não infringe marca nem direito de terceiros (4.2c). O texto não trata de marcas que apareçam na saída; a liberação de direitos é sua (13.2).
- A empresa pode usar entradas e saídas para treinar e melhorar a IA (4.4), salvo contrato empresarial. **Isso significa que o modelo 3D renderizado e as imagens da placa seriam enviados e poderiam entrar em treino.** Para uso acadêmico é aceitável; registrar.
- Saídas: sem reivindicação de propriedade e uso comercial permitido (4.4); não remover marcas de procedência (5.5); não apresentar saída como feita por humano (11.7).
- O logotipo NVIDIA e o texto "RTX PRO 6000" que o projeto decidiu manter no modelo ficam na nossa responsabilidade (uso educacional já registrado em `ARCHITECTURE.md`, seção 5.2).

## 3. A pergunta central: controle estrutural no Higgsfield?

**Não encontrei.** Evidência:
1. Esquema do restyle e do motion transfer: só preset, prompt, imagens de referência e resolução. Lido na doc oficial.
2. Página de vídeo para vídeo: "Profundidade, contorno ou controle estrutural: não mencionado." A promessa é de manter movimento e composição.
3. A ferramenta Depth Map existe, mas separada; a doc não a liga à restilização.
4. Aviso da própria marca: faces, texto e texturas finas "podem ser reconstruídos de forma imprecisa", e "o aprimoramento não recupera detalhe que nunca foi capturado". Produto trocado por referência "pode distorcer" com ângulo diferente.
5. Nenhum teste independente com produto ou objeto técnico foi achado (busca nesta data). Um concorrente (Luma) observa que o Higgsfield gera clipes inteiros e não dá controle por camada; fonte interessada.

Conclusão: o modelo copia a fonte de forma implícita. Fidelidade a grade de 1,5 mm, pá e texto é **desconhecida e provavelmente baixa**; só um teste nosso responde.

## 4. Alternativas

| Opção | Vídeo para vídeo / estrutura | Duração máx. | Custo (fonte) | GPU própria? | Controle de forma | Evidência |
|---|---|---|---|---|---|---|
| Luma Modify Video (`ray-2`, `ray-flash-2`) | 9 modos: `adhere_1..3` (segue de perto), `flex_1..3`, `reimagine_1..3`; `first_frame` opcional | 10 s (ray-2), 15 s (ray-flash-2), 100 MB | ray-2 US$ 0,01582 por milhão de pixels (720p, 5 s, 16:9 = US$ 1,75); ray-flash-2 US$ 0,00544 (US$ 0,60 no mesmo exemplo) | não | médio: botão de aderência, mas sem mapa por quadro | doc oficial lida (docs.lumalabs.ai) |
| Runway Aleph 2.0 | edição por texto de um clipe, mantém movimento e enquadramento (terceiros) | 2 a 30 s segundo agregadores; um comparativo cita 5 s para o Aleph anterior; conflito | 28 créditos/s (mín. 56), US$ 0,01 por crédito = US$ 0,28/s (doc oficial de preços lida) | não | médio-baixo: sem parâmetro estrutural conhecido | preço oficial; limites de terceiros |
| Kling O1 / O3 (via API Runway ou outros) | edição de vídeo por texto e referência | 10 s citado por agregador | O3 Standard/Pro: 13 / 17 créditos/s na tabela da Runway | não | médio-baixo | só agregadores |
| **Wan 2.2 14B Fun Control** (ComfyUI) | **profundidade, contorno (canny), MLSD e pose por quadro** guiam a geração | 81 quadros por passada a 16 fps nos exemplos; sem limite declarado | software aberto; GPU: ver abaixo | sim ou GPU alugada | **alto**: o mapa governa a forma | doc oficial ComfyUI lida |
| **Wan 2.1 VACE** (ComfyUI) | vídeo de controle de profundidade, referência, primeiro e último quadro | exemplos de 49 e 81 quadros | idem | sim ou alugada | **alto** | doc oficial ComfyUI lida |
| Higgsfield Genjutsu Restyle | ver seção 3 | 4 a 30 s | ver seção 2 | não | baixo-médio | doc oficial |

Números oficiais de hardware (docs.comfy.org, lidos em 2026-11-10):
- VACE 14B: modelo de cerca de 32 GB; 1.3B: cerca de 7 GB. O 1.3B só faz 480p; o 14B faz 480p e 720p. Dimensões múltiplas de 16.
- Em RTX 4090: 720x1280 com 81 quadros levou cerca de 40 minutos; 640x640 com 49 quadros cerca de 7 minutos.
- Fun Control 14B em RTX 4090D (24 GB): 640x640, 81 quadros, FP8 usou 83% da VRAM; cerca de 520 s sem LoRA de 4 passos e cerca de 79 a 138 s com ela, com "possível perda de dinâmica".
- Mapas de profundidade vêm do nó `comfyui_controlnet_aux` (Depth Anything V2); o canny já vem no ComfyUI.
- Não verificado: preço de aluguel de GPU. Não coloco valor.

**Qual dá mais controle de forma:** Wan Fun Control/VACE com profundidade + canny, porque as entradas são nossos mapas por quadro. Limitações reais: resolução nativa baixa (480p a 720p), 81 quadros por passada (cerca de 5 s a 16 fps), emendas entre passadas, e nenhum teste publicado de render 3D de objeto técnico para fotorrealista que eu tenha encontrado. Ressalva: a menção "mais controles aumentam a fidelidade estrutural e reduzem a liberdade de estilo" é de um guia de terceiros.

## 5. Alternativa sem IA: Blender Cycles (medido)

Teste real nesta máquina (4 núcleos de CPU, 15 GB de RAM, sem GPU), `bpy` 5.3.0 instalado em ambiente virtual no scratchpad:
- Cena: corpo escuro metálico, 2 ventiladores com 9 pás cada, 80 lâminas finas de 3 mm como grade, piso, 2 luzes de área, desnoiser OpenImageDenoise.
- 1920x1080, 32 amostras: **60,7 s por quadro**.
- 1920x1080, 128 amostras: **185,7 s por quadro**.
- Um clipe de 5 s a 30 fps (150 quadros): cerca de 2,5 h (32 amostras) ou 7,7 h (128 amostras). Um tour de 20 minutos seria inviável em CPU inteiro, mas trechos escolhidos (abertura, teaser) são viáveis, e a CPU tem o computador livre para rodar durante a noite.
- Limitação: cena de brinquedo. A placa real tem muito mais geometria e materiais; o tempo cresce. Não medi o Eevee (exige OpenGL, não testado). Os arquivos do teste ficam no scratchpad da sessão, fora do repositório.
- O Blender não muda a forma: usa o GLB do `build123d` (seção 5.2 da arquitetura). Câmera, tempo, contagem de pás e texto saem idênticos ao tour. Mantém `confirmed` e `derived` quando a peça vier assim.

| Critério | IA generativa (Higgsfield, Luma, Runway) | Wan + ControlNet | Blender Cycles |
|---|---|---|---|
| Fidelidade de forma | não garantida, varia por quadro | alta no contorno, risco em detalhe fino | exata (é a nossa geometria) |
| Controle de câmera e tempo | só o que a fonte carrega | idem | total |
| Aparência "comercial" | alta | média-alta | alta com bom material e luz, depende do trabalho de arte |
| Custo | créditos | GPU alugada | zero além da luz |
| Tempo por 5 s | minutos | minutos a dezenas de minutos | horas em CPU |
| Procedência | `illustrative` | `illustrative` | herda a das peças |
| Dependência externa | conta paga, termos, treino com nossos dados | poucas | nenhuma |

## 6. Riscos para este projeto

1. **Alucinação de geometria:** modelos de vídeo reconstroem o que não enxergam; contagem de pás, lâminas da grade e conectores podem mudar entre quadros. Os avisos oficiais do Higgsfield já preveem isso para detalhe fino.
2. **Texto e logotipo deformados:** "RTX PRO 6000" e o logotipo lateral podem sair errados; um erro de letra numa placa NVIDIA é erro factual visível.
3. **Cintilação:** terceiros relatam "respiração" de textura e cintilação em restilização forte ou alta resolução. Não achei teste com objeto técnico.
4. **Emendas:** limites por passada (10 s Luma ray-2, 81 quadros Wan, 4 a 30 s Higgsfield). Duração e fps de saída do Higgsfield restyle "podem diferir" da fonte, o que quebra o sincronismo com o tour determinístico.
5. **Prazo:** seminário em 2026-11-16, seis dias. Um teste barato cabe; produção em massa de vídeo não cabe junto com os atos 0 a 3 e o `assembly.json`.
6. **Custo e conta paga:** exige cadastro, cartão e créditos; a API do Higgsfield só aparece no console com login.
7. **Dados:** os termos permitem treino com entradas e saídas; nosso modelo e fotos de referência seriam enviados.
8. **Procedência:** todo quadro gerado é `illustrative`. Regra já registrada: só abertura ou teaser, nunca beat que explica.

## 7. Plano de teste barato

Objetivo: medir o desvio de forma, não julgar beleza.

**Trecho:** 4 a 5 s de uma volta em torno da placa montada, enquadrando os dois ventiladores e o texto do X central. 4 s é o mínimo do Higgsfield. Use o `harness/tools/capture.cjs` a 1920x1080 e 30 fps.

**Entradas a gerar (todas já saem do viewer, pouco trabalho):**
1. Vídeo colorido (mp4 em H.264) do trecho.
2. Mapa de profundidade por quadro (para Wan).
3. Contorno por quadro (canny ou contorno do renderizador).
4. Quadro inicial e final (PNG do primeiro e último quadro), para os modos que aceitam.
5. Referência de contagem: números de pás e de lâminas, direto do CSV de medidas.

**Teste A, Higgsfield:** `restyle` em 720p com um preset de aparência de render de produto, prompt curto ("render de produto, fundo escuro, sem alterar a forma"), e depois o mesmo trecho em 1080p. Rodar uma vez cada. Registrar créditos consumidos e as durações de saída.

**Teste B, Luma:** `ray-flash-2`, modo `adhere_2` e `adhere_3`, 720p, 5 s. Custo documentado: cerca de US$ 0,60 por passada.

**Teste C (opcional), Wan Fun Control:** só se houver GPU alugada de 24 GB; usar profundidade + canny, 81 quadros. Custo de aluguel: não verificado.

**Controle:** o mesmo trecho renderizado no Blender Cycles a 32 amostras (cerca de 2,5 h de CPU para 150 quadros; para o teste, 30 quadros dá cerca de 30 min).

**Medições:**
1. Reamostrar o vídeo gerado para 30 fps e para o nosso número de quadros.
2. Extrair contornos nos dois vídeos (canny com os mesmos limiares) e medir a distância média entre contornos em pixels, em 10 quadros espaçados. Registrar o desvio máximo na região dos ventiladores.
3. Contar pás e lâminas visíveis quadro a quadro contra o CSV.
4. Ler o texto do X central e do logotipo quadro a quadro; marcar quadros ilegíveis.
5. Cintilação: diferença média entre quadros consecutivos em regiões estáticas da carcaça, comparada com o nosso vídeo.
6. Critério de aprovação sugerido (a confirmar com o autor): desvio de contorno médio abaixo de 3 px a 1080p, contagem de pás correta em 100% dos quadros, texto legível em ao menos 90%. Se falhar, a IA não entra nem como teaser sem a marca de ilustrativo bem visível.

**Custo estimado (apenas valores documentados):**
- Higgsfield: restyle de 5 s. Preço do restyle não documentado; como referência, Motion Transfer 720p custa 105 créditos por 15 s (cerca de US$ 5,15), então 5 s seria da ordem de 35 créditos, cerca de US$ 1,70, **se** o preço for proporcional (não verificado). Duas passadas: poucos dólares.
- Luma ray-flash-2: cerca de US$ 0,60 por passada de 5 s em 720p; duas passadas, cerca de US$ 1,20.
- Runway Aleph 2.0: 5 s × 28 = 140 créditos = US$ 1,40.
- Total para A + B: abaixo de US$ 5. Planos mensais do Higgsfield podem exigir assinatura (preço da assinatura não verificado).

**O que precisa do autor:** conta e créditos na plataforma escolhida (ou do orquestrador, com a aprovação do autor), e a decisão de enviar o render do nosso modelo a um serviço que pode treinar com ele.

**Como a chave entra sem passar pelo chat:** a sessão tem a ferramenta `request_credential`, que abre um formulário seguro e salva a credencial no ambiente; o proxy injeta o cabeçalho. Para o Higgsfield, o host é `api.higgsfield.ai` e o cabeçalho é `Authorization: Key ID:SECRET` (esquema de duas partes, que o formulário pode não aceitar; nesse caso o autor roda o script localmente com as variáveis `HF_API_KEY_ID` e `HF_API_KEY_SECRET` no shell dele). Nunca colar chave no chat nem no repositório.

## 8. Lacunas desta pesquisa

- Não li o catálogo de presets do Higgsfield nem o console de API (exigem login).
- Não li as páginas de preços do Higgsfield (a página retornou só título) nem o artigo de ajuda da Runway sobre Aleph (403). Limites do Aleph vêm de agregadores e se contradizem (2 a 30 s contra 5 s).
- Não achei teste independente de fidelidade fina (grade, pá, texto) em nenhum dos serviços, com objeto técnico.
- Preços de GPU alugada e preço de assinatura Higgsfield não verificados.
- Datas de blogs da Higgsfield (outubro e novembro de 2026) vêm da própria marca.

## 9. Fontes (acessadas em 2026-11-10)

- Higgsfield, visão geral da API: https://docs.higgsfield.ai (lida)
- Higgsfield, referência de modelos: https://docs.higgsfield.ai/docs/models.md (lida)
- Higgsfield, Genjutsu: https://docs.higgsfield.ai/docs/models/genjutsu.md (lida)
- Higgsfield, Genjutsu Restyle: https://docs.higgsfield.ai/docs/models/genjutsu/restyle.md (lida)
- Higgsfield, Genjutsu Motion Transfer: https://docs.higgsfield.ai/docs/models/genjutsu/motion-transfer.md (lida)
- Higgsfield, guia de vídeo da API: https://docs.higgsfield.ai/docs/guides/video.md (lida)
- Higgsfield, vídeo para vídeo: https://higgsfield.ai/video-to-video (lida; marca)
- Higgsfield, como editar vídeo com IA: https://higgsfield.ai/blog/how-to-edit-videos-with-ai (lida; marca)
- Higgsfield, Genjutsu (preços de 2026-11-02): https://higgsfield.ai/blog/higgsfield-genjutsu (lida; marca)
- Higgsfield, comparativo de modelos de 2026-10-20: https://higgsfield.ai/blog/5-Best-AI-Video-Models-2026-Tested-Compared (lida; marca)
- Higgsfield, termos de uso de 2026-10-23: https://higgsfield.ai/terms (lida)
- Higgsfield, preços: https://higgsfield.ai/pricing (sem conteúdo útil)
- XiaoHu.AI, controle de câmera do Higgsfield: https://xiaohu.ai/en/article/higgsfield-ai-video-camera-control/ (lida; terceiro, sem ano explícito)
- The Neuron, resenha do Higgsfield: https://www.theneuron.ai/tools/our-honest-review-of-higgsfield/review/ (lida; listagem, sem teste)
- Luma, resenha do Higgsfield: https://lumalabs.ai/news/higgsfield-review (só trecho de busca; concorrente)
- Luma, Modify Video: https://docs.lumalabs.ai/docs/modify-video (lida)
- Runway, preços da API: https://docs.dev.runwayml.com/guides/pricing/ (lida)
- Runway, agregadores do Aleph: https://www.runcomfy.com/models/runwayml/runway-aleph-2/video-to-video (só trecho de busca)
- ComfyUI, Wan VACE: https://docs.comfy.org/tutorials/video/wan/vace (lida)
- ComfyUI, Wan 2.2 Fun Control: https://docs.comfy.org/tutorials/video/wan/wan2-2-fun-control.md (lida)
- Atlabs, Runway Aleph contra Luma Modify: https://www.atlabs.ai/blog/runway-aleph-vs-luma-modify-video (só trecho de busca; terceiro)
- Kling O1, agregador: https://www.eachlabs.ai/kling/kling-o1/kling-o1-video-to-video-edit (só trecho de busca)
- Medição do Blender: executada nesta sessão com `bpy` 5.3.0, CPU de 4 núcleos, 2026-11-10.
