# 协作工作区

## 约定

- `CURRENT.md` 是唯一的当前轮次指针。启动任务前先读它，不从聊天记忆猜测目标或轮次。
- 每轮使用唯一 `cycle_id`，所有计划、执行报告和验收结果写在 `cycles/<cycle_id>/`；旧轮次保留，不覆盖。
- Architect 维护 `CURRENT.md` 和 `decision.md`；协调 AI 维护 `plan.md`、`acceptance.md`；执行 AI 各自只维护自己的报告文件。
- 执行 AI 的产品代码仍必须位于各自授权的模块范围和独立 worktree/分支。报告写入项目主工作区的共享路径，不能只留在对话里或各自 worktree 中。
- 在独立 worktree 中工作时，报告写到 `CURRENT.md` 的 `shared_workspace` 绝对路径下，再按其中相对路径定位文件；不要写到自己 worktree 的同名目录。
- 若某 AI 无法访问主工作区共享路径，必须在对话中说明，不得悄悄把报告写到无法被其他角色读取的位置。
- 报告不得包含密钥、Authorization header、真实敏感业务数据或不必要的个人信息。

## 轮次状态

- `planning`：协调 AI 写计划；不启动实现。
- `implementation`：执行 AI 按已确认计划工作并分别写报告。
- `acceptance`：协调 AI 读取差异和执行报告，写验收报告。
- `complete`：Architect 确认本轮结束。下一轮创建新目录并更新 `CURRENT.md`。

## 文件布局

```text
workspace/
  CURRENT.md
  README.md
  templates/
    decision.md
    plan.md
    execution-report.md
    acceptance-report.md
  cycles/
    <cycle_id>/
      decision.md
      plan.md
      reports/
        benchmark.md
        rag.md
        agent.md
      acceptance.md
```

## 最少启动指令

在项目目录 `D:\AI-SecOps-Agent` 打开独立对话后，只需发送相应任务书路径和报告角色。任务书负责读取本文件与 `CURRENT.md`，不需要用户复制任务内容或其他 AI 的报告。

## 每轮操作

1. Architect 新建 `cycles/<cycle_id>/`，从模板填写 `decision.md`，在 `CURRENT.md` 更新轮次、目标和路径，状态设为 `planning`。
2. 启动协调 AI，让它写 `plan.md`。Architect 确认后把状态设为 `implementation`。
3. 分别启动三个执行 AI。它们读取同一份任务和计划，各自在独立代码工作区处理模块，并把报告写到共享轮次目录。
4. 三个报告完成后，将状态设为 `acceptance`，启动协调 AI 写验收报告。
5. Architect 根据验收结果决定返工或下一方向；本轮结束后设为 `complete`，新工作使用新轮次目录。
