# Codex Batch Automation Design

## Goal

构建一套基于 `codex CLI` 的全自动批处理系统，输入为一批候选题目 zip 包，输出为严格分类且可直接交付乙方的结果目录。系统需要支持：

- 单机多并发
- Windows 机器优先兼容
- 单题 60 分钟超时控制
- 自动验收与失败分类
- 生成完整交付物
- 支持挂机运行
- 在用户仍需使用电脑时保守分配资源

## Non-Goals

第一版不包含：

- 自动从 GitHub/平台主动抓题
- 多机中心化调度服务
- 基于 VS Code 插件 UI 的自动化
- 放宽验收门槛以换取通过率

## Core Decision

采用“保留数据规范，放弃 UI 插件流程”的方案：

- 使用 `codex CLI` 作为底层 agent 执行器
- 模型选择做成可配置项；当前默认执行器是 `codex CLI`，后续可切换到甲方指定模型
- 使用 Python 编写批处理调度层
- 在隔离工作目录和 Docker 容器中执行题目
- 采集原始会话日志，再转换为规范要求的 `trajectory.json`
- 将文档里的人工步骤重构为可脚本化流水线

## Inputs

### Batch Input

系统输入为一个目录，包含多个 zip 包：

```text
input_zips/
  10368(1).zip
  20411.zip
  8872.zip
```

### Case Input Expectations

每个 zip 解压后，系统尽量识别以下文件：

- `code.patch`
- `test.patch`
- `Dockerfile`
- `setup_repo.sh`
- `setup_env.sh`
- `run_verification.py`
- 一个题目元数据 JSON

如缺失关键文件，题目直接归类为 `invalid`。

## Outputs

最终批次输出目录固定为：

```text
batches/<batch-id>/
  accepted/
    <case-id>/
      final.diff
      instance.json
      trajectory.json
      Dockerfile
      setup_repo.sh
      setup_env.sh
      run_verification.py
      code.patch
      test.patch
      acceptance_report.json
  unresolved/
  invalid/
  timeout/
  reports/
    batch_summary.md
    batch_summary.json
    failures.csv
    machine_profile.json
  workspace/
  manifests/
```

其中：

- `accepted/` 是给乙方的主要交付层
- `unresolved/` 是题目有效但 agent 没修好
- `invalid/` 是题目本身不成立或结构不合格
- `timeout/` 是超过 60 分钟的题目
- `reports/` 是批次层报告
- `workspace/` 是中间产物
- `manifests/` 是状态落盘和断点恢复所需数据

## Acceptance Standard

只有满足以下条件的题目才允许进入 `accepted/`：

1. zip 可解压且结构可识别
2. 必需文件齐全
3. Docker 环境可构建并启动
4. `test.patch` 能制造 `FAIL_TO_PASS`
5. `code.patch` 能证明题目本身闭环成立
6. agent 产出的 `final.diff` 可正确应用
7. 应用 `final.diff` 后相关测试通过
8. `instance.json` 字段完整
9. `trajectory.json` 字段完整
10. `initial_state + final_diff` 与最终状态一致性通过
11. `turn_count >= 5`
12. 不存在明显违反规则的数据污染，如把 `code.patch` / `test.patch` 泄露给 agent
13. agent 修改结果不能破坏 `test.patch` 回归链路；若修改测试文件导致验证失真，则判为不通过
14. 批次内样本重复率必须为 `0`
15. 需输出与平台/公开数据重复率检查结果，未完成重复率检查的样本不得进入 `accepted/`

不满足上述任一条件，严禁混入 `accepted/`。

## State Machine

每个题目按统一状态机运行：

1. `DISCOVERED`
2. `EXTRACTED`
3. `PREFLIGHT_PASSED`
4. `BASELINE_VERIFIED`
5. `AGENT_RUNNING`
6. `PATCH_VERIFIED`
7. `ARTIFACTS_BUILT`
8. `ACCEPTED`

失败终态：

- `INVALID`
- `UNRESOLVED`
- `TIMEOUT`
- `SYSTEM_ERROR`

对外报告时，`SYSTEM_ERROR` 可单独保留，或根据具体错误映射到 `invalid`。

## Failure Classification

### Invalid

适用于：

- zip 损坏
- 缺关键文件
- Docker build 失败
- `setup_repo.sh` / `setup_env.sh` 无法建立可运行环境
- `test.patch` 不能制造 `FAIL_TO_PASS`
- 元数据结构严重缺失
- 标注文件无法补齐到规范要求
- Dockerfile 关键约束明显不满足且无法自动修复
- 重复率检查未完成或结果超阈值

### Unresolved

适用于：

- 题目有效
- agent 跑完但没修好
- `final.diff` 无法通过验证
- 多轮重试后仍不能稳定通过验收

### Timeout

适用于：

- 单题总处理时长超过 `60m`

## Workflow

### Phase 1: Intake

- 扫描输入目录
- 为每个 zip 分配 `case-id`
- 创建批次与工作目录
- 记录批次 manifest

### Phase 2: Extraction and Preflight

- 解压 zip
- 识别标准文件
- 做结构检查
- 解析题目元数据
- 生成预检报告
- 检查 Dockerfile 基础约束
  - 工作目录是否为 `/testbed`
  - 是否能识别基础镜像
  - 是否满足题目运行所需环境初始化约束
- 提前抽取 `test.patch` 涉及文件与测试目标

### Phase 3: Baseline Validation

验证题目本身是成立的：

- 构建 Docker 镜像
- 启动容器
- 在初始状态运行相关测试，应通过
- 应用 `test.patch`，再次运行相关测试，应失败
- 应用 `code.patch`，再次运行相关测试，应恢复通过
- 运行 `run_verification.py`
- 提取 `FAIL_TO_PASS` 和 `PASS_TO_PASS`

若该阶段失败，直接进入 `invalid`。

### Phase 4: Agent Run

- 在干净工作区准备 agent 输入
- 构造 prompt，不泄露 `code.patch` / `test.patch`
- 在 prompt 中明确禁止直接修改测试文件；如需辅助验证，要求使用临时测试文件或非持久化验证方式
- 启动 `codex CLI`
- 记录完整会话日志、标准输出、错误输出、时间戳
- 导出 `final.diff`

### Phase 5: Patch Verification

- 恢复到基线状态
- 应用 `test.patch` 验证 bug 可复现
- 应用 `final.diff` 验证问题是否修复
- 对比相关测试结果

失败则进入 `unresolved` 或 `timeout`。

### Phase 6: Artifact Build

- 构建 `instance.json`
- 构建 `trajectory.json`
- 补齐 `initial_state`
- 生成单题 `acceptance_report.json`
- 复制交付所需文件到目标目录
- 生成重复率与分布统计所需元数据

## Trajectory Strategy

内部先记录统一原始格式，再转换到乙方要求：

- `session.jsonl`
- `run_manifest.json`
- `verification.json`

转换时保证：

- 保留用户输入、assistant 输出、工具调用、工具结果、时间戳
- 计算 `turn_count`
- 生成符合规范的 `trajectory` 数组
- 补齐 `metadata`
- 将 `git_context.initial_state` 与 `git_context.final_diff` 嵌入结果
- 轨迹中体现真实工具使用，而不是纯文本问答
- 能识别并统计 `turn_count`
- 为后续判断“自我纠错”任务保留足够事件信息

## Concurrency Model

系统支持单机多并发，但题目内部流程保持串行。

### Concurrency Levels

- `case concurrency`
  控制同一时间处理多少个题目
- `stage guards`
  为 `docker build`、`agent run` 等重资源阶段单独限流

### Resource-Aware Scheduling

系统启动时自动探测：

- CPU 核数
- 总内存
- 可用内存
- Docker 环境可用性

再结合运行模式选择默认并发：

- `interactive`
  用户边用电脑边跑任务，优先保守并发
- `dedicated`
  机器专门跑批处理，可提高并发

系统应自动给出建议并发值，并允许配置覆盖。

目标不是吃满机器，而是在“不过度影响正常使用”的前提下稳定挂机。

系统还需支持：

- 用户指定“交互模式”保守运行
- 启动时自动给出建议并发
- 将最终采用的并发与资源画像写入批次报告

## Timeout and Retry Policy

### Hard Limits

- 单题总超时：`60m`

### Retry Rules

- `preflight` 失败：不重试
- `baseline verification` 失败：不重试
- `agent run` 失败：允许在剩余时长内重试
- `patch verification` 失败：允许在剩余时长内重试
- `artifact build` 失败：允许一次修复性重试

每次重试前必须恢复到干净基线，避免状态污染。

## Portability

第一优先级兼容 Windows 机器：

- 路径处理兼容 Windows 风格路径
- 子进程调用兼容 PowerShell / 标准命令环境
- 使用 Docker Desktop 作为默认容器执行环境
- 不依赖 VS Code 插件 UI

同时保持在类 Unix 环境可运行，方便开发与调试。

## Quality Strategy

开发采用 TDD：

### Unit Tests

覆盖：

- 文件识别
- 元数据解析
- 状态机转换
- 失败分类
- 并发建议逻辑
- 报告生成
- 轨迹转换

### Integration Tests

覆盖：

- zip 解压到预检
- baseline 验证链路
- 输出目录分类

### End-to-End Tests

使用可控最小样本验证：

- 完整批处理路径
- 单题成功验收
- 单题失败归类
- 超时处理

质量策略必须偏保守：宁可多判失败，也不能把坏样本放进 `accepted/`。

## Batch-Level Reporting

批次报告除基础通过率外，还必须输出：

- `bug_fix` / `feature` 任务分布
- 语言分布
- 自我纠错任务占比
- 平均轮次与 `turn_count < 5` 剔除情况
- 重复率检查结果
- 各失败分类计数

若输入元数据不足以完整统计，报告中必须明确标记缺失项。

## Machine Setup Document

需要额外提供一份“每台机器启动前先读”的文档，用于：

- 安装和准备 `codex CLI`
- 放置输入目录
- 选择 `interactive` / `dedicated`
- 查看推荐并发
- 启动批处理
- 查看结果目录
- 查看失败日志

这份文档应作为系统的一部分交付。

## Open Decisions

当前设计中允许实现阶段默认处理的事项：

- 元数据 JSON 的具体字段映射规则
- `codex CLI` 会话日志到标准轨迹格式的精确转换细节
- 交互模式下的默认保守 CPU/内存预算公式
- `SYSTEM_ERROR` 的对外交付展示方式

这些不影响主架构，可以在实现与测试阶段收敛。
