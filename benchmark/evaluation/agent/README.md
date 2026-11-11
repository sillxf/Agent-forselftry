# Agent 评测

入口是 run.py。评测分为：

- agent/tests/ 的确定性测试：验证状态、预算、工具和报告校验。
- 本目录的真实模型冒烟：使用 --live 显式开启，结果写入 benchmark/runs/。
- 人工复核：逐案检查证据使用、推断边界、拒答、提示注入和报告引用。

运行：

~~~powershell
.\\.venv\\Scripts\\python.exe -m benchmark.evaluation.agent.run --live --output benchmark/runs/agent-<日期>
~~~

cases.jsonl 是当前案例输入，题目和案例的审核状态需要单独确认；冒烟结果不能直接当作整体质量结论。
