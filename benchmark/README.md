# Benchmark 与评测

benchmark/ 是独立的质量边界，不参与 RAG 服务启动。它包含冻结输入、评测代码和实验入口；运行产物应写入系统临时目录或被 Git 忽略的 `benchmark/runs/`。

## 目录

~~~text
datasets/security-v1/      原始冻结候选集 r2（保留原始字节与哈希，不覆盖）
datasets/security-v1-r3/   v1 契约迁移版：题目、文档、来源、许可证与 SHA-256 manifest
evaluation/schemas/       可机器读取的契约 schema
evaluation/               检索、答案、Agent 与可选机器裁决入口
experiments/              显式实验入口
tests/                    Benchmark 边界内确定性测试
runs/                     本机运行结果，不提交 Git
~~~

`security-v1` 仍是原始冻结版 r2；迁移后的 v1 数据以新目录 `security-v1-r3` 保存，避免同路径替换造成旧实验无法复现。两者都只是候选数据，机器完整性校验不等于语义正确或人工审核；当前没有人工审核样本。`final_holdout` 是按 `query_family` 稳定分组的仓库内留出集，不是密码学隐藏集，不能用于调参后再宣称独立测试。

## 离线校验与裁决

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s benchmark/tests -p "test_*.py"
.\.venv\Scripts\python.exe -m benchmark.evaluation.validate_dataset --report "$env:TEMP\benchmark-validation.json"
.\.venv\Scripts\python.exe -m benchmark.evaluation.adjudicate --dataset all --output "$env:TEMP\benchmark-adjudication-dryrun"
~~~

最后一条默认 dry-run，不访问模型。Live AI 裁决须显式指定 `--live`，配置两个评审模型（或显式接受单模型相关性限制），并提供请求上限、成本上限和调用者确认的 token 单价；分歧时才请求第三评审。低置信、缺证据、解析失败或无多数的条目为 `unresolved`，排除于主质量分并单独报告。

## 实验与 Agent dry-run

~~~powershell
.\.venv\Scripts\python.exe -m benchmark.experiments.chunking_experiment --output benchmark/runs/chunking-<run-id> --offline
.\.venv\Scripts\python.exe -m benchmark.evaluation.agent.run --output "$env:TEMP\agent-dryrun"
~~~

Agent dry-run 列出实际选择的全部案例与 split，不调用模型。Agent live 示例及必需预算参数见 `evaluation/agent/README.md`；不要在未确认费用前运行。

答案级评测的输入和分步命令见 `evaluation/answer/README.md`。词面规则仅为确定性子指标，不能单独作为语义正确声明。报告需保留数据与代码哈希、模型/prompt 标识、运行预算、各层指标、样本量提示、未决和排除比例。机器裁决不是人类 ground truth；小样本候选集不能证明生产事故表现或生产质量。
