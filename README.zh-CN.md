# Smart Tutor 中文说明

`smart_tutor` 是一个模块化的多轮家庭作业辅导助手，内置护栏机制。
它只支持数学和历史作业问题，并会拒绝无关请求。

## 系统架构

系统运行流程如下：

1. 用户界面
2. NeMo Guardrails 层
3. 输入护栏过滤
4. 意图与主题分类
5. 任务路由
6. 学科 Tutor Agent
7. LLM 生成引擎
8. 输出护栏
9. 对话记忆
10. 返回响应给用户

## 项目结构

```text
smart_tutor/
  main.py
  gradio_app.py
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

## 功能特性

- 基于 LangChain 的多轮对话记忆
- 输入护栏，过滤非作业类问题
- 意图分类：
  - `homework_question`
  - `summary_request`
  - `unrelated_query`
- 主题路由：
  - `math`
  - `history`
  - 其他主题直接拒绝
- 根据学生水平自动调整讲解难度，例如 `year 1`、`high school`
- 支持生成练习题
- 支持总结当前对话
- 支持可配置的 LLM 提供方：OpenAI 兼容接口或 Ollama

## 环境要求

- Python 3.10 及以上

## 安装步骤

1. 创建并激活 Python 虚拟环境。
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 将 `.env.example` 复制为 `.env`。
4. 根据你使用的模型服务填写配置。

## 配置说明

### OpenAI 兼容模式

如果你使用 OpenAI 或兼容 OpenAI API 的平台，可这样配置：

```env
TUTOR_LLM_PROVIDER=openai
TUTOR_MODEL=gpt-4o-mini
TUTOR_TEMPERATURE=0.2
OPENAI_API_KEY=your_key_here
```

如果你使用兼容 OpenAI 的第三方服务，也可以额外配置：

```env
OPENAI_BASE_URL=https://your-api-base-url/v1
```

## 运行方式

### 命令行模式


```bash
python main.py
```

### Gradio Web 界面

如果你想使用网页交互界面，在 `smart_tutor` 目录下运行：

```bash
python gradio_app.py
```

启动后会显示本地访问地址，通常为：

```text
http://127.0.0.1:7860
```
让老师和同学启动需要生成分享链接

## 示例问题

- `I am a year 1 student. What is 7 + 5?`
- `Explain the causes of World War I.`
- `Give me 3 practice questions on fractions.`
- `Quiz me on the French Revolution.`
- `Summarize our conversation so far`
- `Plan my vacation in Japan`

最后一个示例应当被拒绝，因为它不属于数学或历史作业问题。

## 护栏与行为说明

- 系统只允许回答数学和历史作业问题。
- 明显无关的问题会被拒绝。
- 危险、不安全或违规请求会被阻止。
- 输出结果在返回前还会经过一次输出护栏检查。

## 主要模块说明

- `main.py`：主入口，负责串联输入护栏、分类、路由、Tutor、输出护栏和记忆。
- `gradio_app.py`：Gradio 网页前端。
- `config.py`：统一读取 `.env` 配置。
- `guardrails/`：输入输出护栏与护栏配置文件。
- `classification/`：意图分类器和主题分类器。
- `router/`：按主题路由到对应 Tutor。
- `agents/`：数学与历史 Tutor Agent。
- `llm/`：统一封装模型调用。
- `memory/`：管理多轮对话记忆与学生水平信息。
- `utils/summarizer.py`：生成会话摘要。

## 常见问题

### 1. 提示 `OPENAI_API_KEY is required`

说明当前配置被识别为 `openai` 模式，但没有成功读取到 `OPENAI_API_KEY`。
请检查：

- 是否存在真正的 `.env` 文件，而不只是 `.env.example`
- `.env` 是否位于正确目录
- `OPENAI_API_KEY` 是否填写正确

### 2. 提示模型不存在

说明 `TUTOR_MODEL` 配置的模型名不正确，或当前服务不支持该模型。
请检查模型名称是否与服务提供方支持的名称一致。


## 备注

- 本项目当前采用 NeMo Guardrails 风格的护栏配置组织方式。
- 对话记忆会同时保存用户消息和助手回答。
- 对于简短追问，系统会结合最近话题继续路由到正确学科。
