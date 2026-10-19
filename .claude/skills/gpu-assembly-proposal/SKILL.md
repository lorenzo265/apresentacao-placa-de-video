---
name: gpu-assembly-proposal
description: Propõe a arquitetura provável (peças, quantidades, topologia) de subsistemas de uma placa de vídeo cujo interior não é público, sempre com procedência, confiança e justificativa. Use ao montar design/assembly.json de uma GPU NVIDIA workstation, quando for preciso decidir como é a parte que não temos acesso (VRM, camadas do PCB, interior do cooler, package do chip).
---

# gpu-assembly-proposal

Transforma "não sabemos como é por dentro" em uma **proposta de engenharia rastreável**, nunca em fato disfarçado.

## Entradas
- `spec/card.spec.json` (fatos com procedência)
- `spec/sources/` (datasheets, teardowns)
- lista de **placas análogas** (mesmo chip no consumo, geração anterior pro), preenchida na etapa 2

## Níveis de procedência (obrigatório em toda peça)
| Nível | Significa | Exemplo |
|---|---|---|
| `confirmed` | Fonte oficial ou teardown **desta** placa | Saídas de vídeo, conector de energia, slots |
| `derived` | Visto em placa irmã com o mesmo chip ou geração | Layout de memória ao redor do die |
| `inferred` | Engenharia plausível, sem evidência direta | Número exato de fases do VRM |
| `illustrative` | Só didático | Estruturas internas do die |

Nunca promova um nível sem evidência nova. Na dúvida, rebaixe.

## Método

1. **Enumere os subsistemas** que toda placa desse tipo tem: package da GPU (die, substrato, stiffener), memória, entrega de energia (conector, filtros, fases, controladores), PCB (camadas, slot PCIe), térmica (base, câmara de vapor/heatpipes, aletas, pads, ventilador), mecânica (shroud, backplate, bracket, parafusos), I/O (saídas de vídeo), sensores e proteções.
2. **Classifique cada item**: o que a fonte já mostra x o que falta.
3. **Escolha análogos** para o que falta. Prefira, nesta ordem: (a) placa de consumo com o mesmo chip e teardown público, (b) a geração anterior da mesma linha, (c) prática de mercado para a mesma classe de potência. Registre qual análogo foi usado e por quê.
4. **Proponha com números**, e não com adjetivos. Dê valor central e faixa (ex.: "fases de GPU: 20 (faixa 18-24)"). Dê cada parâmetro que a modelagem precisa: contagem, dimensões, posição relativa, material.
5. **Atribua procedência e confiança (0 a 1)** com `rationale` de uma ou duas frases e as `alternatives_considered`.
6. **Rode as verificações de consistência** (abaixo). Se algo não fecha, ajuste a proposta ou rebaixe a confiança.
7. **Escreva o texto de aviso** (`viewer_disclaimer`) para cada peça `inferred` ou `illustrative`, em PT-BR claro.
8. **Entregue** `design/proposal.json` (estruturado) e `design/proposal.md` (leitura humana, com tabela resumo e lista de dúvidas abertas).

## Verificações de consistência (as contas precisam fechar)
- **Memória:** `chips x largura por chip = largura do barramento` (considerando o modo clamshell, se houver) e `chips x capacidade por chip = capacidade total`.
- **Energia:** capacidade somada das fases da GPU e da memória >= TBP / tensão de núcleo, com margem. Corrente do conector de energia >= TBP / 12 V, com margem.
- **Térmica:** área de aletas e vazão do ventilador plausíveis para o TBP. Compare com o análogo.
- **Geometria:** a soma das espessuras (PCB + componentes + cooler + shroud) respeita a espessura de slot do spec. Nenhuma peça colide com a vizinha.
- **Montagem:** cada peça tem a fixação que a prende (parafuso, clipe, solda), e a ordem de desmontagem é fisicamente possível.

## Formato de saída (`design/proposal.json`, por peça)
```json
{
  "id": "power.vrm.gpu",
  "provenance": "inferred",
  "confidence": 0.55,
  "analog": "teardown da placa irmã com o mesmo chip",
  "parameters": {"phases": {"value": 20, "range": [18, 24]}, "stage": "DrMOS"},
  "rationale": "Mesma classe de potência do análogo, com folga de projeto para carga sustentada.",
  "alternatives_considered": ["16 fases de maior corrente"],
  "consistency_checks": {"power_budget": "ok", "geometry": "ok"},
  "viewer_disclaimer": "Estrutura provável: a NVIDIA não publica o número exato de fases."
}
```

## Regras
- Nunca apresente `inferred` como `confirmed`, nem em nome de peça, comentário ou texto.
- Não reproduza esquemáticos ou arquivos proprietários vazados. Use só fontes públicas e raciocínio de engenharia.
- Se uma verificação de consistência falha, **não esconda**: registre em `open_questions`.
- A proposta é revisada por humano antes de virar modelagem (gate da fase F2).
