# Multi-View 退步归因：固定路线消融

不改模型、语料、View、Ground Truth、候选预算或 RRF 常数；不调权重。
全部方案共用逐题编码一次的原始 Query 向量；本轮不比较查询延迟。所有标签仍保留原审核状态。

原始两组排名指纹复现：{'hybrid': True, 'multi_view': True}。

| 路线 | 全部 Parent R@5 | 全部 Parent R@10 | 全部 MRR@5 | 中文→英文 R@5 |
| --- | ---: | ---: | ---: | ---: |
| original_dense | 0.9667 | 0.9889 | 0.8331 | 0.9487 |
| view_dense | 0.7509 | 0.8833 | 0.6302 | 0.6603 |
| bm25 | 0.5333 | 0.5444 | 0.4519 | 0.0000 |
| hybrid | 0.9444 | 0.9778 | 0.7448 | 0.9231 |
| inner_dense | 0.8500 | 0.9556 | 0.7304 | 0.7692 |
| view_bm25 | 0.7583 | 0.8889 | 0.6126 | 0.5705 |
| flat_rrf | 0.8667 | 0.9778 | 0.7456 | 0.7692 |
| multi_view | 0.8444 | 0.9778 | 0.6807 | 0.7436 |

original_dense=原文 Dense；view_dense=辅助问题 Dense 映射并去重；inner_dense=RRF(原文 Dense, View Dense)。
hybrid=RRF(原文 Dense,BM25)；view_bm25=RRF(View Dense,BM25)。
flat_rrf=RRF(原文 Dense,View Dense,BM25)；multi_view=RRF(inner_dense,BM25)。

## 原先 Recall@5 退步的题目

| ID | 原文 Dense 正Parent排名 | View 正Parent排名 | Hybrid | 内层融合 | 三路直接融合 | 两层融合 | 正证据Child有View |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rag_004 | 1 | 1 | 5 | 1 | 3 | 6 | 1/1 |
| rag_007 | 3 | 候选池无 | 2 | 16 | 8 | 8 | 1/1 |
| rag_038 | 1 | 14 | 2 | 6 | 6 | 7 | 1/1 |
| rag_043 | 3 | 19 | 4 | 8 | 8 | 9 | 1/1 |
| rag_045 | 1 | 19 | 1 | 6 | 6 | 6 | 1/1 |
| rag_049 | 4 | 12 | 4 | 9 | 9 | 9 | 1/1 |
| rag_050 | 1 | 5 | 2 | 6 | 7 | 7 | 3/3 |
| rag_053 | 1 | 候选池无 | 2 | 14 | 15 | 15 | 1/1 |
| rag_072 | 1 | 10 | 2 | 5 | 5 | 6 | 1/1 |
| rag_081 | 2 | 候选池无 | 2 | 9 | 9 | 9 | 1/1 |

退步题中，没有直接覆盖正证据 Child 的 View：[]。
注意：无正证据 Child View 不等于整个 Parent 无 View；可能存在兄弟 Chunk 的视图。
首个正Parent排名按去重Parent计算，与最终 ParentContextBuilder 一致。
原始 raw View 问题、命中来源、正证据覆盖、各路候选池和排名见 route_diagnostics.json。
消融是开发集机制诊断，不是对 LLM 生成内容做了人工事实审核，也不建立泛化结论。

## 可由消融支持的结论

1. 原文 Dense R@5 为 96.67%，问题 View Dense 为 75.09%；新增通道明显弱于原通道。
2. 不加 BM25，单独融合原文和问题 View 后 R@5 已降到 85.00%；退步在内层就发生，并非最后一层才导致。
3. 三路直接 RRF 为 86.67%，比两层融合恢复 2.22 个百分点，仍低于原 Hybrid 94.44%；嵌套结构不是唯一原因。
4. 10 道原先退步题中，有 10 道的正证据 Child 至少有一条 View；不能简单归咎于没有生成 View。
5. RRF 按名次投票，不判断原始相似度可信度。弱问题通道也参与等权投票，会使仅在原文排名很高的证据被其他两路都命中的候选超越。
以上是当前固定数据上的路线干预，不是每种因素互相独立的百分比贡献分解。

## 问题视图焦点的具体例子

这些只是对已冻结文本的对照，不是新增人工审核通过状态。

### rag_007
原问题：Can password guessing be performed without contacting a live authentication service?
对应正证据 Child 的中文 View：攻击者如何使用 T1110: Brute Force 获取账户访问权限？

### rag_045
原问题：不打开浏览器窗口也能运行网页应用格式的独立程序，资料指的是哪个系统工具？
对应正证据 Child 的中文 View：攻击者如何滥用 mshta.exe 执行恶意 HTA 文件或 JavaScript、VBScript？

### rag_053
原问题：为什么一本固定出版物不再适合维护所有事件处置的操作细节？
对应正证据 Child 的中文 View：NIST SP 800-61 Revision 3 的目的和范围是什么？
