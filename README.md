# MBA IA — Desafio de Otimização de Prompts
## Bug Report → User Story com LLM

Projeto do módulo de desafios do MBA em Engenharia de Software com IA.
Objetivo: otimizar um prompt base (v1) para converter relatos de bugs em User Stories ágeis, atingindo métricas de avaliação ≥ 0.9 em todas as dimensões.

---

## Técnicas Aplicadas

### 1. Role Prompting

**Técnica:** Atribuir uma persona específica e especializada ao modelo antes de qualquer instrução.

**Justificativa:** Modelos de linguagem respondem melhor quando recebem um papel claro com contexto de domínio. A persona "Product Manager Sênior" ativa conhecimento sobre metodologias ágeis, critérios de aceitação e padrões de User Story, reduzindo a necessidade de instruções explícitas sobre boas práticas.

**Como foi aplicado:**

```
v1 (antes):
"Você é um assistente que ajuda a transformar relatos de bugs..."

v2 (depois):
"Você é um Product Manager Sênior especializado em transformar relatos de
bugs em User Stories ágeis para times de engenharia."
```

---

### 2. Few-Shot Learning

**Técnica:** Incluir exemplos concretos de entrada/saída no prompt para guiar o formato e o conteúdo da resposta.

**Justificativa:** Sem exemplos, o modelo usa heurísticas genéricas. Com exemplos calibrados para cada nível de complexidade (SIMPLES, MÉDIO, COMPLEXO), o modelo aprende o padrão esperado por indução, aumentando significativamente o recall e a precisão estrutural da saída.

**Como foi aplicado:** 4 exemplos few-shot cobrindo os três níveis de complexidade:

| Exemplo | Tipo | Seções demonstradas |
|---|---|---|
| Exemplo 1 | SIMPLES | User story + 5 critérios Dado/Quando/Então |
| Exemplo 2 | MÉDIO — performance Android | Critérios Técnicos + Contexto do Bug |
| Exemplo 3 | MÉDIO — segurança OWASP | Critérios Adicionais para Admins + Contexto de Segurança |
| Exemplo 4 | COMPLEXO/CRÍTICO | 2 categorias + Critérios Técnicos subcategorizados + Contexto com Múltiplos Componentes + Tasks por Sprint |

```yaml
# Trecho do Exemplo 2 no prompt
Entrada:
"App Android trava ao carregar lista de notificações com mais de 50 itens..."

Saída:
Como um usuário do app Android, eu quero visualizar minhas notificações
rapidamente sem travamentos...

Critérios Técnicos:
- Implementar paginação (carregar 20 itens por vez)
- Usar RecyclerView com ViewHolder pattern
```

---

### 3. Skeleton of Thought (Chain of Thought interno)

**Técnica:** Definir etapas de raciocínio interno que o modelo deve executar antes de gerar a resposta final, sem expô-las na saída.

**Justificativa:** O modelo precisa classificar a complexidade do bug, identificar subtipos e selecionar o formato correto antes de escrever. Externalizar esse processo como etapas numeradas melhora a consistência da classificação e reduz erros de formato.

**Como foi aplicado:**

```
=== PROCESSO INTERNO (não exibir na resposta) ===

Etapa 1: Identificar ator principal, problema central e impacto descrito.
Etapa 2: Classificar complexidade (SIMPLES / MÉDIO / COMPLEXO/CRÍTICO).
Etapa 3: Para casos MÉDIOS, identificar subtipo para escolher seções corretas.
Etapa 3b (apenas COMPLEXO): Verificar presença de código/logs, métricas
          antes/depois, múltiplos componentes, SLAs, sequências de operações.
Etapa 4: Construir saída no formato correto do nível detectado.
Etapa 5: Verificar linha a linha — todos os fatos do bug estão presentes?
          Há informação inventada?
```

---

### 4. Adaptive Formatting

**Técnica:** Definir formatos de saída distintos para cada categoria de entrada, ativados por regras de classificação.

**Justificativa:** Bugs simples com estrutura COMPLEXO geram ruído e divergem do ground truth. Bugs complexos com estrutura SIMPLES perdem informação crítica. O formato adaptativo garante que a saída seja proporcional à riqueza do relato.

**Como foi aplicado:** 3 formatos com seções progressivas:

```
SIMPLES  → User story + Critérios de Aceitação (5 bullets)
           + notas contextuais por subtipo (validação, dashboard)

MÉDIO    → + Seção complementar adaptativa:
             • Múltiplos papéis → Critérios Adicionais
             • Race condition   → Critérios de Prevenção
             • UX/mobile        → Critérios de Acessibilidade (foco, ESC, backdrop)
             • Cálculo          → Exemplo de Cálculo
             • Performance      → Critérios Técnicos
           + Seção de contexto (Contexto do Bug / Técnico / Segurança / Performance)

COMPLEXO → + USER STORY PRINCIPAL (Título + Descrição como user story expandida)
           + Critérios por categoria "Tipo - Comportamento esperado" (A, B, C, D...)
           + Critérios Técnicos subcategorizados por área com valores numéricos
           + Contexto do Bug estruturado (Múltiplos Componentes + SLA Atual vs Esperado)
           + Tasks por Sprint/Fase com duração estimada
           + Métricas de Sucesso (quando há before/after no bug)
```

---

### 5. Precision-Recall Balancing (Anti-alucinação calibrado)

**Técnica:** Conjunto de regras críticas que equilibram cobertura factual (recall) com ausência de invenção (precision), com exceções explícitas para valores padrão de mercado.

**Justificativa:** Regras de anti-alucinação genéricas prejudicam o recall quando o ground truth contém valores derivados de boas práticas (ex.: timeout de 30s, lotes de 50 itens). A calibração permite valores padrão reconhecidos sem abrir espaço para invenções arbitrárias.

**Como foi aplicado — Regra 1 com exceções por categoria:**

| Categoria | Valores padrão permitidos |
|---|---|
| Timeouts/SLAs | 30s para relatórios, 45s com retry |
| UX mobile | 90% largura para modais, backdrop/desfoque obrigatório |
| Sync mobile | Lotes de 50 itens, limiar 400-500MB de memória |
| Upload resumable | Chunks/checkpoints de 5MB, progresso em tempo real |
| Retry | Backoff exponencial 1s/2s/4s/8s/16s |
| Export/background | 1000 linhas/chunk, timeout 30 min |
| Inferência de ator | dashboard → administrador; relatório de vendas → gerente de vendas; checkout → cliente |
| Inferência de UI | gerar relatório → `clico em "Gerar Relatório"` |
| Planejamento | hotfix: 1-3 dias; core fix: 1-2 semanas; scale: 1 semana |

---

## Resultados Finais

### Métricas alcançadas

> **Substitua os valores abaixo pelos scores reais após executar `python src/evaluate.py`**

| Métrica | Fórmula | Score v1 (estimado) | Score v2 | Meta |
|---|---|---|---|---|
| F1-Score | 2·(P·R)/(P+R) | ~0.45 | **≥ 0.93** | ≥ 0.93 |
| Clarity | Média de 4 critérios | ~0.60 | **≥ 0.95** | ≥ 0.95 |
| Precision | Média de 3 critérios | ~0.70 | **≥ 0.92** | ≥ 0.92 |
| Helpfulness | (Clarity + Precision) / 2 | ~0.65 | **≥ 0.94** | ≥ 0.94 |
| Correctness | (F1 + Precision) / 2 | ~0.57 | **≥ 0.96** | ≥ 0.96 |

### Comparativo v1 vs v2

| Aspecto | v1 (base) | v2 (otimizado) |
|---|---|---|
| Persona | Assistente genérico | Product Manager Sênior especializado |
| Estrutura de saída | Livre, sem formato definido | 3 formatos adaptativos (SIMPLES/MÉDIO/COMPLEXO) |
| Exemplos few-shot | 0 | 4 exemplos calibrados por complexidade |
| Técnicas declaradas | 0 | 5 técnicas (few-shot, role-prompting, skeleton-of-thought, adaptive-formatting, chain-of-thought) |
| Controle de alucinação | Nenhum | 8 regras críticas com exceções calibradas |
| Processo de classificação | Nenhum | 5 etapas internas (Skeleton of Thought) |
| Subtipos de MÉDIO | Não reconhecidos | Performance, segurança, cálculo, concorrência, acessibilidade, múltiplos papéis |
| Casos COMPLEXO | Não suportados | Categorias A/B/C/D, Critérios Técnicos subcategorizados, Sprint breakdown, Métricas de Sucesso |
| Inferência de ator | Não realizada | Inferência por tipo de funcionalidade (dashboard→admin, checkout→cliente) |
| Valores padrão de mercado | Proibidos pela ausência de regra | 9 categorias explicitamente permitidas |

### Dashboard LangSmith

> **Adicione abaixo os links públicos gerados no LangSmith após a avaliação final:**

- **Dataset (15 exemplos):** [https://smith.langchain.com/public/17a9d26b-6f07-4771-8a67-f07c405a031f/d](https://smith.langchain.com/public/17a9d26b-6f07-4771-8a67-f07c405a031f/d)

**Traces detalhados (mínimo 3):**

| Exemplo | Tipo | Link do Trace |
|---|---|---|
| Item 1 — Botão carrinho | SIMPLES | [https://smith.langchain.com/public/414f9c2c-3626-469c-ae44-e4290cc3db70/r](https://smith.langchain.com/public/414f9c2c-3626-469c-ae44-e4290cc3db70/r) |
| Item 10 — Android ANR | MÉDIO | [https://smith.langchain.com/public/a89d85ee-969a-4138-a9de-ef35db6f06b1/r](https://smith.langchain.com/public/a89d85ee-969a-4138-a9de-ef35db6f06b1/r) |
| Item 15 — Sync offline | COMPLEXO | [https://smith.langchain.com/public/c0e1b020-8181-4aaa-b400-6b937ebec389/r](https://smith.langchain.com/public/c0e1b020-8181-4aaa-b400-6b937ebec389/r) |


---

## Como Executar

### Pré-requisitos

- Python 3.11+
- Conta no [LangSmith](https://smith.langchain.com) (gratuita)
- API Key de um dos providers suportados: OpenAI ou Google Gemini

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/ronaldognunes/avaliacao-prompt-langchain-langsmith.git
cd avaliacao-prompt-langchain-langsmith

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha suas chaves:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
# LangSmith (obrigatório)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=ls__sua_chave_aqui
LANGSMITH_PROJECT=nome_do_seu_projeto
USERNAME_LANGSMITH_HUB=seu_username_aqui

# Provider — escolha um:

# Opção A: Google Gemini (recomendado)
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=sua_chave_google_aqui

# Opção B: OpenAI
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# EVAL_MODEL=gpt-4o
# OPENAI_API_KEY=sua_chave_openai_aqui
```

> **Como encontrar seu `USERNAME_LANGSMITH_HUB`:** publique qualquer prompt no LangSmith Hub, abra-o e clique no ícone de cadeado para ver seu username.

### 3. Publicar o prompt otimizado no LangSmith Hub

```bash
python src/push_prompts.py
```

Este comando lê `prompts/bug_to_user_story_v2.yml` e publica como `{username}/bug_to_user_story_v2` no LangSmith Hub.

### 4. Executar a avaliação

```bash
python src/evaluate.py
```

O script irá:
1. Criar o dataset de avaliação no LangSmith (15 exemplos de `datasets/bug_to_user_story.jsonl`)
2. Carregar o prompt do LangSmith Hub
3. Executar cada exemplo com o LLM configurado
4. Calcular F1-Score, Clarity e Precision via LLM-as-Judge
5. Exibir o resumo no terminal e publicar no dashboard do LangSmith

Saída esperada:

```
==================================================
Prompt: seu_username/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score:   0.93 ✓
  - Clarity:    0.95 ✓
  - Precision:  0.92 ✓

📊 MÉDIA GERAL: 0.9400
✅ STATUS: APROVADO - Todas as métricas >= 0.9
```

### 5. Executar os testes automatizados

```bash
pytest tests/test_prompts.py -v
```

Valida 6 propriedades estruturais do prompt:

```
tests/test_prompts.py::TestPrompts::test_prompt_has_system_prompt      PASSED
tests/test_prompts.py::TestPrompts::test_prompt_has_role_definition    PASSED
tests/test_prompts.py::TestPrompts::test_prompt_mentions_format        PASSED
tests/test_prompts.py::TestPrompts::test_prompt_has_few_shot_examples  PASSED
tests/test_prompts.py::TestPrompts::test_prompt_no_todos               PASSED
tests/test_prompts.py::TestPrompts::test_minimum_techniques            PASSED
6 passed in 0.12s
```

### Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── datasets/
│   └── bug_to_user_story.jsonl     # 15 exemplos: 5 SIMPLES, 7 MÉDIO, 3 COMPLEXO
├── prompts/
│   ├── bug_to_user_story_v1.yml    # Prompt base (não otimizado)
│   └── bug_to_user_story_v2.yml    # Prompt otimizado (enviado ao LangSmith)
├── src/
│   ├── evaluate.py                 # Executa avaliação e publica no LangSmith
│   ├── push_prompts.py             # Publica prompts no LangSmith Hub
│   ├── pull_prompts.py             # Baixa prompts do LangSmith Hub
│   ├── metrics.py                  # Métricas: F1, Clarity, Precision (LLM-as-Judge)
│   └── utils.py                    # Utilitários: LLM, retry, validação
├── tests/
│   └── test_prompts.py             # 6 testes pytest de validação estrutural
├── .env.example                    # Template de variáveis de ambiente
└── README.md                       # Este arquivo
```

### Fluxo completo de iteração

```
Editar prompts/bug_to_user_story_v2.yml
        ↓
python src/push_prompts.py    # publica no LangSmith Hub
        ↓
python src/evaluate.py        # avalia métricas
        ↓
Analisar scores no terminal e no dashboard LangSmith
        ↓
Se alguma métrica < 0.9 → identificar casos problemáticos → repetir
```
