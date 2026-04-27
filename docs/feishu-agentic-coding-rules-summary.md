# 真实用户 agentic coding 轨迹数据规则文档 - 执行摘要

## 这份文档要你做什么

你的目标不是单纯修一个 bug，而是制作一条**可交付的 agentic coding 数据样本**。每条样本都要满足：

- 基于一个真实仓库、真实 issue / PR 背景
- 在标准 Docker 环境中可以稳定复现
- 让 agent 根据 issue 和提示词自行修改代码
- 导出 agent 的完整交互轨迹
- 生成 `final.diff`
- 证明 `final.diff` 能在干净初始状态上修复问题
- 最终补齐 `instance.json` 和 `trajectory.json`

## 核心约束

- 只能使用 `claude opus 4.6`
- agent 插件可用 `CLINE`，尽量不要用 `swe-agent`、`openhands`
- 数据不能和内部已有数据、公开 SFT 数据重复
- 同一批次内部重复率必须为 `0`
- 与平台已有数据/公开数据重复率必须 `< 0.05%`
- 交付必须在 Docker 中 `100%` 可复现
- 轨迹要体现真实结对编程，不是纯文本问答
- 如果最终标注出的 `turn_count < 5`，这条数据无效

## 你最终要交付的文件

- `code.patch`
- `test.patch`
- `Dockerfile`
- `setup_repo.sh`
- `setup_env.sh`
- `run_verification.py`
- `final.diff`
- `instance.json`
- `trajectory.json`

## 两个核心标注文件

### `instance.json`

至少要有这些核心字段：

- `instance_id`
- `repo`
- `base_commit`
- `language`
- `task_category`，只能是 `bug_fix` 或 `feature`
- `problem_statement`
- `FAIL_TO_PASS`
- `PASS_TO_PASS`
- `patch`
- `test_patch`

建议补充：

- `created_at`
- `environment_setup_commit`

### `trajectory.json`

必须包含：

- `instance_id`
- `instruction`
- `instance`
- `metadata`
- `trajectory`

其中重点是：

- `instance.git_context.initial_state`
- `instance.git_context.final_diff`
- `metadata.agent`
- `metadata.model`
- `metadata.thinking_mode`
- `metadata.coding_agent_system_prompt`
- `metadata.tools`

## 最关键的真实性要求

### `initial_state`

- 必须记录所有被 `final_diff` 修改过的文件的**修改前完整内容**
- 新增文件不要放进 `initial_state`
- 如果是从零创建任务，`initial_state` 可以是 `{}`

### `final_diff`

- 必须是标准 unified diff
- 必须带完整 diff header，例如 `diff --git a/... b/...`
- 新文件要有 `new file mode`

### 一致性要求

文档反复强调：

- `initial_state` + `git apply final_diff` 要严格对应最终状态
- 一致性验收标准是 `>= 95%`

## 实际制作流程

### 1. 先把环境做通

- 写好 `Dockerfile`
- 写好 `setup_repo.sh`
- 写好 `setup_env.sh`
- 构建镜像
- 在容器里先让 `test.patch` 涉及的测试文件能正常运行

### 2. 用 `code.patch` / `test.patch` 先验证题目本身成立

文档要求先做一轮题目有效性验证：

- 初始状态跑相关测试，应当通过
- 应用 `test.patch` 后再跑相关测试，应当失败，复现 bug
- 再应用 `code.patch` 后跑测试，应当恢复通过

这一步本质上是在验证这条题目的测试设计和修复闭环是成立的。

### 3. 跑 `run_verification.py`

- 提取 `FAIL_TO_PASS`
- 提取 `PASS_TO_PASS`
- 回填到 `instance.json`

### 4. 重新进入干净环境，让 agent 真正做题

- 容器里只挂载 `test.patch` 和 agent 插件
- 在容器内安装指定插件
- 配置 API key / base url
- 先用 `plan` 模式让 agent 规划
- 确认计划没问题后切到 `act`

### 5. 导出 agent 结果

- agent 执行后必须开启新对话
- 用 `git diff > final.diff` 导出补丁
- 清理仓库改动，回到原始状态
- 只应用 `test.patch` 复现 bug
- 再应用 `final.diff` 验证修复是否成功

### 6. 如果 agent 失败

- 删除这次对话记录和 `final.diff`
- 回到重新提示 agent 的阶段重做
- 只能调整提示词和引导方向
- **不能**把 `test.patch`、`code.patch`、上一轮 `final.diff` 的内容泄露给 agent

### 7. 导出轨迹并生成 `trajectory.json`

- 从插件任务目录导出对话记录
- 跑提取脚本生成 `trajectory.json`
- 补齐 `task_category` 和 `source`
- 把 `run_verification.py` 中针对 `code.patch` 的验证改成针对 `final.diff`

## 高风险点

- 不能让 agent 直接看到 `code.patch` / `test.patch` 的具体内容
- agent 修改测试代码会导致验证链路失真，文档建议在提示词里明确禁止改测试
- `turn_count < 5` 直接无效
- `final.diff` 涉及到的旧文件如果没完整出现在 `initial_state` 里，数据会不合格
- 如果题目过长、过复杂、或 `test.patch` 无法制造 `FAIL_TO_PASS`，应直接跳过

## 任务分类判断

如果 issue 页面没明确写是 `feature` 还是 `bug_fix`，需要人工阅读 issue 描述自行判断。

## 我对你当前工作的理解

如果你接下来是要真正开始做这个项目，那么你的工作可以拆成四块：

1. 选题并验证题目闭环成立
2. 配置 Docker / repo / env，使题目可复现
3. 驱动 agent 产出可用 `final.diff`
4. 整理轨迹和标注，补齐最终交付文件

这说明你接下来最重要的不是“直接让 agent 改代码”，而是先确保：

- 题目有效
- 环境稳定
- 回归验证路径清晰
- 标注字段和轨迹导出方式可落地
