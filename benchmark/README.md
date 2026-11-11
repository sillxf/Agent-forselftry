# Benchmark 与评测

benchmark/ 是独立的质量边界，不参与 RAG 服务启动。它包含冻结输入、评测代码和实验入口；运行产物写入被 Git 忽略的 benchmark/runs/。

## 目录

~~~text
datasets/security-v1/   当前冻结基准：题目、文档、来源、许可证和 SHA-256 manifest
evaluation/             检索、答案级和 Agent 评测
experiments/            显式实验入口
tests/                  评测链路测试
runs/                   本地运行结果，不提交 Git
~~~

security-v1 当前仍是候选基准，题目尚未全部人工审核。它可以用于检查链路和比较方案，不能单独作为生产质量结论。修改基准输入时必须同步更新 manifest.json、来源说明和版本信息；优先新增版本，不覆盖已有冻结版本。

## 常用入口

~~~powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s benchmark/tests -p "test_*.py"
.\\.venv\\Scripts\\python.exe -m benchmark.experiments.chunking_experiment --output benchmark/runs/chunking-<日期> --offline
.\\.venv\\Scripts\\python.exe -m benchmark.evaluation.agent.run --live --output benchmark/runs/agent-<日期>
~~~

答案级评测的输入格式和分步命令见 evaluation/answer/README.md；Agent 评测见 evaluation/agent/README.md。评测结果应记录代码提交、数据版本、模型和配置。
