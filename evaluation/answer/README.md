# 答案级评测

检索指标只回答“正确的片段有没有返回”。这里回答下一步：调用方拿到返回的上下文后，答案对不对，知识库答不了的时候有没有拒答。脚本是 `evaluation/answer_eval.py`，分三步，每步都可以单独用。

1. 检索：通过运行中的服务和只读 Key 对每道题调用 `/api/v1/search`，记录返回了哪些来源，以及每个答案要点是否出现在返回的上下文里。这是任何调用方答案的上限：上下文里没有的要点，答案不可能有据可依。
2. 生成（付费，需显式开启）：用 `.env` 里的 `LLM_MODEL` 只依据返回的上下文作答。必须同时给 `--generate` 和 `--max-requests`，题数超过上限时一个请求都不发。
3. 判分（不调模型）：要点覆盖、禁止出现的说法、不可回答题是否拒答、引用编号是否有效。答案可以来自任何调用方（Agent、人、其他模型），用 JSONL 提供即可。

~~~powershell
# 只做检索，看上下文是否包含答案要点（不收费）：
python -m evaluation.answer_eval --questions evaluation/answer/sample_questions.jsonl `
  --knowledge-base <kb_id> --output evaluation/results/answers-<日期>
# 给已有答案判分：
python -m evaluation.answer_eval --questions <题目.jsonl> --answers <答案.jsonl> --output <目录>
# 付费生成并判分，最多 20 次请求：
python -m evaluation.answer_eval --questions <题目.jsonl> --knowledge-base <kb_id> `
  --generate --max-requests 20 --output <目录>
~~~

检索步骤读取 `RAG_SERVICE_URL` 和 `RAG_SERVICE_TOKEN`。结果写入输出目录：`retrieval.jsonl`、`answers.jsonl`、`grades.jsonl`、`summary.json`。

## 题目格式

每行一个 JSON 对象：

| 字段 | 说明 |
| --- | --- |
| `id` | 唯一编号 |
| `question` | 问题原文 |
| `answerable` | 知识库能否回答。`false` 时正确行为是拒答 |
| `must_include` | 答案要点列表。每个要点是一组可互相替代的说法，答案里出现其中任意一个就算覆盖，例如 `[["lockout", "锁定"]]` |
| `must_not_include` | 不应出现的说法，例如相邻文档的干扰答案 |
| `sources` | 应该命中的文档文件名，用来算来源命中率 |
| `queries` | 可选，调用方会附带的改写查询（例如英文翻译） |
| `review_status` | `approved` 表示已人工审核；其他值都算未审核，汇总里会给出 `unreviewed_warning` |
| `note` | 给审核人的说明 |

拒答的识别方式是匹配“知识库中没有找到”“证据不足”“insufficient evidence”等短语（见脚本里的 `REFUSALS`）。生成用的提示词要求模型拒答时输出“知识库中没有找到”。

## 判分规则的局限

判分只看词面：要点有没有出现、禁止说法有没有出现。它不判断推理是否正确，也识别不了同义改写。答案对、但用了题目没列出的说法时会判错，这类题会出现在 `needs_review` 里，需要人看。不要为了提高这个分数去调参数；判分有分歧的题，应该修改题目里的备选说法，或者交给人工复核。

## 需要你做的事

`sample_questions.jsonl` 里的 6 道题只用来确认链路能跑通，由 AI 编写，状态是 `pending`，不能用来下质量结论。要让这个评测有意义，需要一批人工审核过的题目，建议 30 到 50 道，最好来自真实的提问。下面几类是现有基准覆盖不足的：

| 类型 | 例子 |
| --- | --- |
| 相似条目混淆 | HKCU 和 HKLM 下的 Run / RunOnce，T1110.003 和 T1110.004 |
| 否定 | “普通用户就能读取 LSASS 吗？”（正确答案是否定） |
| 干扰项 | 恶意软件的处置问题，暴力破解文档里的“封 IP、开 MFA”是干扰答案 |
| 版本冲突 | 新旧两版制度说法不同，应以取代关系指向的新版为准 |
| 看似能答 | 有相关文档，但问的是语料里没有的版本或数值 |
| 多跳 | 需要两份文档拼起来才能回答 |

审核时把 `review_status` 改为 `approved`。留出一部分题目不参与调参，只用来做最后的确认。
