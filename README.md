# Smart Tutor

`smart_tutor` is a modular multi-turn homework tutoring assistant with guardrails.
It only supports math and history homework questions and rejects unrelated queries.

## Architecture

The runtime pipeline follows this order:

1. User Interface
2. NeMo Guardrails Layer
3. Input Guardrail Filter
4. Intent & Topic Classifier
5. Task Router
6. Subject Tutor Agents
7. LLM Generation Engine
8. Output Guardrail
9. Conversation Memory
10. Response to User

## Project Structure

```text
smart_tutor/
  main.py
  config.py
  guardrails/
    rails_config.yml
    input_guardrail.py
    output_guardrail.py
  classification/
    intent_classifier.py
    topic_classifier.py
  router/
    task_router.py
  agents/
    math_tutor.py
    history_tutor.py
  llm/
    llm_engine.py
  memory/
    conversation_memory.py
  utils/
    summarizer.py
```

## Features

- Multi-turn conversation memory using LangChain
- Homework-only filtering with input guardrails
- Intent classification:
  - `homework_question`
  - `summary_request`
  - `unrelated_query`
- Topic routing:
  - `math`
  - `history`
  - reject everything else
- Difficulty adaptation from learner level such as `year 1` or `high school`
- Exercise generation for practice requests
- Conversation summarization on request
- Configurable LLM provider: OpenAI or Ollama

## Setup

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Configure one of the following:

OpenAI mode:

```env
TUTOR_LLM_PROVIDER=openai
TUTOR_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_key_here
```

Ollama mode:

```env
TUTOR_LLM_PROVIDER=ollama
TUTOR_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```

## Run

Use module mode from the project root:

```bash
python -m smart_tutor.main
```

## Example Prompts

- `I am a year 1 student. What is 7 + 5?`
- `Explain the causes of World War I.`
- `Give me 3 practice questions on fractions.`
- `Quiz me on the French Revolution.`
- `Summarize our conversation so far`
- `Plan my vacation in Japan` -> should be rejected

## Notes

- The app uses a NeMo-style guardrail configuration file in `smart_tutor/guardrails/rails_config.yml`.
- Conversation memory stores both user and assistant turns.
- If a follow-up question is short, topic routing can reuse the last known subject.
