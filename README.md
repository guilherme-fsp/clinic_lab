# JSON-to-Google-ADK Agent Transpiler

Projeto desenvolvido como desafio técnico para geração dinâmica e execução de agentes com o Google Agent Development Kit (ADK).

A aplicação recebe uma especificação de agente em JSON, valida o contrato e transpila a definição para um módulo Python executável. Como demonstração, o agente processa solicitações de exames laboratoriais a partir de uma imagem, protege dados pessoais, localiza exames em uma base fictícia e solicita o agendamento por meio de uma API FastAPI.

## Sumário

- [Visão geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Configuração e execução com Docker](#configuração-e-execução-com-docker)
- [Uso pela API](#uso-pela-api)
- [Uso pela CLI](#uso-pela-cli)
- [Serviços da demonstração](#serviços-da-demonstração)
- [Proteção de dados pessoais](#proteção-de-dados-pessoais)
- [Estratégia de orquestração](#estratégia-de-orquestração)
- [Observabilidade e testes](#observabilidade-e-testes)
- [Decisões de arquitetura](#decisões-de-arquitetura)
- [Processo de desenvolvimento e uso de IA](#processo-de-desenvolvimento-e-uso-de-ia)
- [Referências](#referências)
- [Execução rápida](#execução-rápida)

## Visão geral

O fluxo principal da aplicação é:

1. O usuário envia uma especificação JSON ao transpilador.
2. A especificação é validada com modelos Pydantic.
3. O transpilador gera dinamicamente um módulo Python que define um agente Google ADK.
4. O runtime carrega o módulo gerado.
5. Uma imagem com uma solicitação médica é enviada para processamento.
6. O agente usa um servidor MCP de OCR para extrair o texto.
7. O texto passa por um guardrail local de proteção de dados pessoais (PII).
8. Os exames identificados são consultados por meio de um servidor MCP de busca/RAG.
9. Os exames encontrados são enviados à API fictícia de agendamento.
10. O agente retorna os exames cujo agendamento foi solicitado.

O código do agente não precisa existir previamente no repositório: ele é produzido pelo transpilador a partir da especificação recebida.

## Arquitetura

```text
                      ┌─────────────────────────┐
                      │      Swagger / API      │
                      │       Port 18003        │
                      └────────────┬────────────┘
                                   │
                         POST /transpile
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   Transpiler Service    │
                      │                         │
                      │ JSON → AgentSpec        │
                      │     ↓                   │
                      │ AgentCodeGenerator      │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      generated/<agent>.py
                                   │
                                   │ POST /run
                                   ▼
                      ┌─────────────────────────┐
                      │     Agent Runtime       │
                      │                         │
                      │ dynamic module loading  │
                      │       ↓                 │
                      │    ADK Runner           │
                      └────────────┬────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
               OCR MCP                       RAG MCP
                    │                             │
                    ▼                             │
              PII Guardrail                       │
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │    Scheduling API       │
                      │       FastAPI           │
                      │                         │
                      │ POST /appointments      │
                      └─────────────────────────┘
```

### Componentes

- `transpiler/`: validação da especificação e geração do código Python.
- `runtime/`: carregamento dinâmico e execução do agente Google ADK.
- `mcp_servers/ocr/`: servidor MCP responsável pela extração de texto.
- `mcp_servers/rag/`: servidor MCP responsável pela recuperação de exames.
- `guardrails/pii/`: detecção e mascaramento de dados pessoais.
- `scheduling_api/`: API fictícia de agendamento construída com FastAPI.
- `data/exams.json`: base fictícia com mais de 100 exames laboratoriais.
- `tests/`: testes unitários e de integração.
- `examples/`: especificação e imagem usadas na demonstração.

### Especificação e geração do agente

A especificação do agente é fornecida em JSON. Exemplo simplificado:

```json
{
  "name": "lab_exam_scheduler",
  "model": "gemini-3.5-flash-lite",
  "description": "Agent responsible for processing laboratory exam requests.",
  "instruction": "Follow the laboratory scheduling workflow.",
  "tools": [
    {
      "type": "mcp",
      "name": "ocr",
      "transport": "sse",
      "url": "http://ocr-mcp:8001/sse"
    },
    {
      "type": "local",
      "name": "sanitize_medical_text",
      "module": "tools.pii_tool",
      "function": "sanitize_medical_text"
    },
    {
      "type": "mcp",
      "name": "exam_search",
      "transport": "sse",
      "url": "http://rag-mcp:8002/sse"
    },
    {
      "type": "http",
      "name": "schedule_exam",
      "base_url": "http://scheduling-api:8000",
      "method": "POST",
      "path": "/appointments"
    }
  ]
}
```

O transpilador gera um módulo Python com:

- imports necessários;
- conexões com servidores MCP;
- ferramentas HTTP e locais;
- configuração do modelo, instrução e ferramentas;
- definição do `root_agent`.

Antes de persistir o código, o resultado é compilado com `compile()` para detectar código Python inválido.

## Estrutura do projeto

```text
.
├── config/
├── data/
│   └── exams.json
├── examples/
│   ├── agent_spec.json
│   └── imagem_qualquer.png
├── generated/
├── guardrails/
│   └── pii/
├── mcp_servers/
│   ├── ocr/
│   └── rag/
├── runtime/
│   └── agent_runner.py
├── scheduling_api/
├── scripts/
├── tests/
│   ├── integration/
│   └── unit/
├── tools/
├── transpiler/
│   ├── generators/
│   ├── schemas/
│   ├── validators/
│   ├── api.py
│   ├── cli.py
│   └── service.py
├── Dockerfile
├── docker-compose.yml
├── main.py
├── pyproject.toml
└── requirements.txt
```

## Configuração e execução com Docker

### 1. Configure as variáveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Preencha as credenciais necessárias. O arquivo `.env` não deve ser versionado.

### 2. Inicie os serviços

Na raiz do projeto, execute:

```bash
docker compose up --build
```

Os principais serviços iniciados são:

- `transpiler-api`
- `ocr-mcp`
- `rag-mcp`
- `scheduling-api`

## Uso pela API

A interface Swagger do transpilador estará disponível em [http://localhost:18003/docs](http://localhost:18003/docs).

### 1. Gerar o agente

Envie a especificação para `POST /transpile`. O arquivo de exemplo é `examples/agent_spec.json`.

Uma resposta bem-sucedida será semelhante a:

```json
{
  "status": "generated",
  "agent_name": "lab_exam_scheduler",
  "output_file": "generated/lab_exam_scheduler.py"
}
```

O módulo em `generated/` é um artefato de runtime e não precisa ser armazenado no repositório.

### 2. Executar o agente

Use o endpoint `POST /run` disponível no mesmo Swagger. Exemplo de payload:

```json
{
  "agent_name": "lab_exam_scheduler",
  "image_path": "examples/imagem_qualquer.png"
}
```

O runtime usa `agent_name` para carregar `generated/lab_exam_scheduler.py` e localizar nele o `root_agent`. Em seguida, executa o agente com o Runner do Google ADK.

## Uso pela CLI

O projeto também oferece uma interface de linha de comando independente da API.

### Gerar o agente

```bash
python -m transpiler.cli examples/agent_spec.json
```

Resultado esperado:

```text
Agent generated successfully: generated/lab_exam_scheduler.py
```

### Executar o agente

```bash
python main.py \
  lab_exam_scheduler \
  examples/imagem_qualquer.png
```

O nome do agente não é fixado no runtime: o argumento `lab_exam_scheduler` determina qual módulo existente em `generated/` será carregado.

## Serviços da demonstração

### API de agendamento

A API fictícia de agendamento é um serviço FastAPI independente. Sua documentação Swagger está disponível em [http://localhost:18000/docs](http://localhost:18000/docs).

O endpoint principal consumido pelo agente é `POST /appointments`.

Exemplo de requisição:

```json
{
  "exams": [
    {
      "name": "Hemograma Completo",
      "code": "LAB001"
    },
    {
      "name": "Creatinina",
      "code": "LAB008"
    }
  ]
}
```

Exemplo de resposta:

```json
{
  "appointment_id": "APT-example",
  "status": "requested",
  "exams": [
    {
      "name": "Hemograma Completo",
      "code": "LAB001"
    },
    {
      "name": "Creatinina",
      "code": "LAB008"
    }
  ],
  "message": "Appointment request received successfully."
}
```

O contrato apresentado no Swagger corresponde ao contrato consumido pela ferramenta HTTP gerada pelo transpilador.

### Servidores MCP

Foram implementados dois serviços MCP independentes:

| Serviço | Endereço no ambiente Docker | Responsabilidade |
| --- | --- | --- |
| OCR MCP | `ocr-mcp:8001` | Receber a referência da imagem e extrair seu conteúdo textual. |
| RAG MCP | `rag-mcp:8002` | Consultar a base fictícia de exames laboratoriais. |

A base possui mais de 100 registros e é indexada para recuperação textual. O agente acessa esses serviços por meio das ferramentas MCP declaradas dinamicamente no código gerado.

## Proteção de dados pessoais

O workflow inclui uma etapa de sanitização antes que o texto extraído seja usado nas etapas posteriores. O guardrail identifica padrões como:

- nomes de pacientes;
- datas de nascimento;
- documentos;
- telefones e outras informações de contato.

Por exemplo:

```text
Paciente: João da Silva
```

é transformado em algo equivalente a:

```text
Paciente: [PERSON_1]
```

A implementação do guardrail é determinística e permanece separada do agente.

Atualmente, o serviço de OCR usa um modelo multimodal para interpretar a imagem. A sanitização textual ocorre imediatamente após a extração do OCR e antes das etapas posteriores de recuperação e agendamento. Em um ambiente com requisitos de privacidade mais restritivos, o componente OCR poderia ser substituído por um mecanismo executado localmente, permitindo que a anonimização ocorresse antes de qualquer processamento externo.

## Estratégia de orquestração

A orquestração segue predominantemente um fluxo sequencial controlado pelas instruções do agente:

```text
Imagem
  ↓
OCR
  ↓
Sanitização de PII
  ↓
Identificação dos exames
  ↓
Busca RAG
  ↓
Validação dos resultados
  ↓
Agendamento
  ↓
Resposta final
```

Essa ordem garante que o conteúdo produzido pelo OCR passe pelo guardrail antes de ser utilizado nas etapas seguintes.

As consultas de exames são operações independentes. Quando o modelo identifica múltiplos exames, o runtime/ADK pode emitir várias chamadas de busca na mesma etapa, permitindo seu processamento sem criar dependência artificial entre as consultas.

Não foram utilizados subagentes porque o domínio é pequeno e o workflow tem uma sequência clara de responsabilidades. A separação foi feita por ferramentas especializadas e serviços MCP, reduzindo a complexidade de coordenação.

## Observabilidade e testes

### Observabilidade

O runtime usa logging estruturado para registrar eventos importantes da execução, por exemplo:

```text
Starting ADK runner
Loading generated agent
Tool call | name=extract_medical_request
Tool response | name=extract_medical_request
Tool call | name=sanitize_medical_text
Tool call | name=search_exams
Tool call | name=schedule_exam
ADK runner finished
```

Os logs do runtime evitam registrar deliberadamente os argumentos e as respostas completas das ferramentas, reduzindo a exposição acidental de informações sensíveis.

### Testes

Para executar os testes:

```bash
pytest -v
```

Os testes cobrem, entre outros pontos:

- validação da especificação;
- geração de código Python e importação do agente gerado;
- geração de ferramentas HTTP e MCP;
- validação de Base64 e MIME type;
- serviço OCR e proteção de PII;
- recuperação de exames;
- API de agendamento;
- integração com os servidores MCP;
- integração da ferramenta de agendamento.

### Evidências de funcionamento

As evidências de funcionamento estão disponíveis na pasta:
exec_evidences/

## Decisões de arquitetura

### Código gerado não versionado

O agente final é tratado como um artefato produzido pelo transpilador. Por isso, `generated/*.py` não representa código-fonte mantido manualmente. Essa escolha demonstra que o módulo executado pelo Google ADK foi criado a partir do JSON enviado ao transpilador.

### Separação entre transpilação e geração de código

A lógica principal está centralizada no serviço de transpilação, que pode ser usado por diferentes interfaces:

```text
CLI ────────┐
            ├── TranspilerService → AgentCodeGenerator
HTTP API ───┘
```

Isso evita que a API dependa diretamente da CLI e reduz duplicação.

### Serviços externos desacoplados

OCR, recuperação de exames e agendamento têm responsabilidades separadas. Assim, cada componente pode ser substituído sem alterar o núcleo do transpilador.

## Processo de desenvolvimento e uso de IA

Ferramentas de IA foram utilizadas como apoio ao desenvolvimento, principalmente para revisão técnica e aceleração dos ciclos de implementação.

### Usos da IA

- discutir alternativas de organização dos módulos;
- sugerir estruturas iniciais para componentes e testes;
- revisar trechos de código durante refatorações;
- interpretar stack traces e erros durante integrações com ADK, MCP e Docker;
- comparar alternativas para carregamento dinâmico de módulos Python;
- auxiliar na identificação de problemas de configuração entre containers;
- sugerir casos de teste e cenários de falha;
- auxiliar na organização e revisão desta documentação.

### Decisões e validações humanas

As decisões de arquitetura foram desenvolvidas e ajustadas durante a implementação. Entre elas:

- separar os servidores OCR e RAG usando MCP;
- utilizar um guardrail local para PII;
- definir o contrato JSON aceito pelo transpilador;
- implementar ferramentas dos tipos `mcp`, `http` e `local`;
- decidir quais campos fariam parte dos schemas;
- substituir o runtime inicialmente estático por carregamento dinâmico;
- remover o agente previamente gerado do código-fonte e gerar o agente somente após receber o JSON;
- consolidar transpilação e execução sob a mesma API HTTP;
- manter a API de agendamento como serviço independente;
- definir o fluxo de segurança entre OCR, sanitização, busca e agendamento;
- executar e validar manualmente as integrações no Docker;
- analisar resultados de recuperação e ajustar o comportamento esperado;
- revisar os resultados do agente e os contratos entre os serviços.

O desenvolvimento foi iterativo: cada implementação era executada, validada por testes ou logs e ajustada quando o comportamento observado não correspondia ao esperado. Sugestões produzidas por IA foram revisadas, modificadas ou descartadas e verificadas durante a execução do sistema. A IA apoiou o trabalho de engenharia; as decisões sobre arquitetura, integração, comportamento e validação final permaneceram parte do processo manual de desenvolvimento.

## Referências

As principais fontes técnicas consultadas durante a implementação foram:

- documentação oficial do Google Agent Development Kit (ADK), incluindo agentes e ferramentas;
- documentação oficial do Model Context Protocol e do MCP Python SDK, incluindo servidores, clientes e transports como SSE e HTTP;
- documentação oficial do FastAPI, usada como referência para endpoints, modelos e Swagger UI;
- documentação do Google Gen AI SDK;


## Execução rápida

Preencha o .env seguindo o exemplo .env.example

Inicie os serviços:

```bash
docker compose up --build
```

Em seguida:

1. Abra [http://localhost:18003/docs](http://localhost:18003/docs).
2. Execute `POST /transpile` com `examples/agent_spec.json`. (A imagem de exemplo também se encontra dentro do dir examples)
3. Execute `POST /run` com o agente gerado e a imagem de exemplo.
4. Acompanhe os logs do workflow.
5. Consulte [http://localhost:18000/docs](http://localhost:18000/docs) para verificar o contrato da API de agendamento.

O fluxo também pode ser executado pela CLI:

```bash
python -m transpiler.cli examples/agent_spec.json

python main.py \
  lab_exam_scheduler \
  examples/imagem_qualquer.png
```
