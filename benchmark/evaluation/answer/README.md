# 答案级评测

入口是 benchmark/evaluation/answer_eval.py。它把评测拆成三步：

1. 检索：调用 RAG，记录来源和答案要点是否进入上下文。
2. 生成：可选，必须显式传 --generate --max-requests。
3. 判分：不调用模型，检查要点、禁止说法、拒答和引用编号。

示例：

~~~powershell
python -m benchmark.evaluation.answer_eval --questions benchmark/evaluation/answer/sample_questions.jsonl --knowledge-base <kb_id> --output benchmark/runs/answers-<日期>
python -m benchmark.evaluation.answer_eval --questions <题目.jsonl> --answers <答案.jsonl> --output <目录>
~~~

结果文件包括 retrieval.jsonl、answers.jsonl、grades.jsonl 和 summary.json。题目中的 review_status 为 approved 才表示经过人工审核；当前样例主要用于确认链路，词面判分不能替代人工语义复核。
