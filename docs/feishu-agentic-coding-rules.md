# <text color="red">文档是保密文档禁止外传</text>
## **引言**
User-Agentic-coding 是一个用于评估和训练 AI 编程代理（Coding Agent）的数据集，收集真实的"人-AI 结对编程"交互轨迹。数据来源于开发者使用 AI 编程工具（Claude Code、Cline 等）在 Docker 容器中修复 Bug 或开发新功能的完整过程，包含用户指令、Agent 推理链、工具调用、代码变更等全链路信息。它收集了真实用户在使用coding agent解决实际问题时的交互数据,每个任务包含:
- 一个用户提交的Issue(问题描述,bug描述或者功能请求)
- 一个Pull Request（PR）,是用户对Issue的解决或功能实现的提交,包含了对代码的修改和测试
- 项目的代码仓库克隆脚本（setup_repo.sh）,环境搭建脚本（setup_env.sh）和验证脚本（run_verification.py或者verification.py）
- Dockerfile,docker构建时的配置,确保项目的环境可以完整复现
你需要将issue描述和提示词发送给agent，让agent解决issue,然后生成一个修复补丁，验证修复补丁有效.
所有制作完成的数据都符合:可以在标准化的容器中复现bug,并可以使用agent提供的修复补丁（final.diff）修复bug
---

## <text color="red" bgcolor="light-yellow">做之前必看</text>
- <text bgcolor="light-yellow">公司提供的账号或API key严禁外泄！</text>
- <text bgcolor="light-yellow">除项目需求外，公司提供的API key或账号严禁用于其他用途！</text>
## **轨迹采集****制作要求**
- 使用的模型为：claude opus 4.6，不要使用其他任何模型进行数据采集
- 使用的编程agent插件可以为CLINE，但是尽量不要使用swe-agent、openhands等特定领域的agent
- 采集的Agent交互轨迹不允许内部重复，且严禁与开源SFT数据集（如SWE-bench官方数据集, Aider-bench等）及平台存量数据重复
- 即使针对同一个Bug（指令相同），如果Agent采用了完全不同的推理路径和修复策略（Thought不同），则视为不同数据；若推理逻辑高度相似，则视为重复
- 交付批次内数据重复率必须为 0。
- 与平台已有数据（及公开数据集）的重复率 < 0.05%。
## **Docker 环境要求**
- 根据 Dockerfile 或公开 Docker Image 版本说明，构建环境** 必须成功**
- 交付数据必须保证在提供的 Docker 环境中 **100% 可复现**
- 容器内需包含项目代码、依赖环境、必要的构建工具
## **文本结构与数据质量**
- 格式规范： 所有的推理（Thought）和对话内容必须为UTF-8编码的纯文本。
- Markdown要求： 代码块、文件路径、终端日志必须使用 Markdown 格式（````code````）包裹。
- LaTeX要求： 涉及算法公式的描述优先使用 LaTeX 格式。
## **重复率控制**
**判重单位：**以"仓库上下文 (Repo Context) + 用户指令 (User Instruction) + Agent 核心推理链 (Thought)"三者的组合作为去重最小单位。
<quote-container>
即使针对同一个 Bug（指令相同），如果 Agent 采用了完全不同的推理路径和修复策略（Thought 不同），视为不同数据；若推理逻辑高度相似，则视为重复。
</quote-container>


## **任务类型与分布**

<lark-table rows="5" cols="2" header-row="true" column-widths="305,394">

  <lark-tr>
    <lark-td>
      维度
    </lark-td>
    <lark-td>
      要求
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      Bug 修复 (bug_fix)
    </lark-td>
    <lark-td>
      占比 40%–60%
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      需求开发 (feature)
    </lark-td>
    <lark-td>
      占比 40%–60%
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      多步/跨文件任务（交互 > 5 轮）
    </lark-td>
    <lark-td>
      ≥ 60%
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      自我纠错任务（报错→分析→重修）
    </lark-td>
    <lark-td>
      ≥ 20%（高价值数据）
    </lark-td>
  </lark-tr>
</lark-table>

## **编程语言分布**

<lark-table rows="4" cols="3" header-row="true" column-widths="245,245,200">

  <lark-tr>
    <lark-td>
      梯队
    </lark-td>
    <lark-td>
      语言
    </lark-td>
    <lark-td>
      占比要求
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      第一梯队（Web/Script）
    </lark-td>
    <lark-td>
      Python, JavaScript/TypeScript
    </lark-td>
    <lark-td>
      ≥ 55%
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      第二梯队（System/Backend）
    </lark-td>
    <lark-td>
      Java, C++, Go, C
    </lark-td>
    <lark-td>
      ≥ 35%
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      其他
    </lark-td>
    <lark-td>
      SQL, Rust, Shell 等
    </lark-td>
    <lark-td>
      ≤ 10%
    </lark-td>
  </lark-tr>
</lark-table>

## **数据格式规范**
- **存储格式：JSON**：完整规范的JSON文件，文件编码为 UTF-8。
- **验证标准**：`initial_state` + `git apply final_diff` 必须严格等于任务结束时的最终文件状态（一致性 ≥ 95%）。
## **字段完备性要求：**
- 两个必需标注文件，一个是instance.json，一个是trajectory.json.
- instance.json 文件包含以下字段：  

<lark-table rows="13" cols="4" header-row="true" column-widths="265,162,200,258">

  <lark-tr>
    <lark-td>
      字段名
    </lark-td>
    <lark-td>
      类型
    </lark-td>
    <lark-td>
      是否必须
    </lark-td>
    <lark-td>
      说明
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance_id`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      任务实例的唯一标识符 (示例： "sphinx-doc__sphinx-8721")
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `repo`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      格式为"所有者/名称"的GitHub仓库
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `base_commit`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      表示修复前状态的Git提交哈希
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `language`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      项目的编程语言 (示例： "Python")
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `task_category`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      任务类别 (枚举： "bug_fix", "feature")
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `problem_statement`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      要修复的bug或问题的详细描述
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `FAIL_TO_PASS`
    </lark-td>
    <lark-td>
      array
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      初始失败但修复后应该通过的测试名称列表
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `PASS_TO_PASS`
    </lark-td>
    <lark-td>
      array
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      修复前和修复后都应该通过的测试名称列表
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `patch`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      包含代码修复的Git补丁
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `test_patch`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      包含修复代码测试的Git补丁
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `created_at`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      最好有 (Better have)
    </lark-td>
    <lark-td>
      问题创建时的ISO 8601时间戳
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `environment_setup_commit`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      最好有 (Better have)
    </lark-td>
    <lark-td>
      环境搭建配置的Commit哈希值
    </lark-td>
  </lark-tr>
</lark-table>

- trajectory.json 需要包含以下字段：  

<lark-table rows="28" cols="4" header-row="true" column-widths="357,200,200,453">

  <lark-tr>
    <lark-td>
      字段名
    </lark-td>
    <lark-td>
      类型
    </lark-td>
    <lark-td>
      是否必须
    </lark-td>
    <lark-td>
      说明
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance_id`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      链接到相应实例的唯一标识符
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instruction`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      用户指令/初始提示，用于agent
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance`
    </lark-td>
    <lark-td>
      object
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      嵌入的实例配置（与instance.json结构相同）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.repo`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      仓库路径
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.base_commit`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      基础提交哈希
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.git_context`
    </lark-td>
    <lark-td>
      object
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      Git仓库上下文，包含初始状态和最终差异
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.git_context.initial_state`
    </lark-td>
    <lark-td>
      object
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      修复前工作区文件的初始状态
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.git_context.final_diff`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      显示所有变更的最终差异
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.problem_statement`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      问题描述
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.FAIL_TO_PASS`
    </lark-td>
    <lark-td>
      array
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      修复后应该通过的测试名称列表（同swe要求）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.PASS_TO_PASS`
    </lark-td>
    <lark-td>
      array
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      修复前和修复后都应该通过的测试名称列表（同swe要求）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.patch`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      修复补丁代码
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.test_patch`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      测试修复补丁代码
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `instance.created_at`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      最好有 (Better have)
    </lark-td>
    <lark-td>
      问题创建时的ISO 8601时间戳
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata`
    </lark-td>
    <lark-td>
      object
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      会话元数据和配置
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.agent`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      代理名称/版本（例如，"Claude Code"，"OpenHands"）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.model`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      模型标识符（例如，"claude-sonnet-4-20250514"）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.thinking_mode`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      推理模式设置（"slow"或"fast"）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.max_iterations`
    </lark-td>
    <lark-td>
      number
    </lark-td>
    <lark-td>
      最好有 (Better have)
    </lark-td>
    <lark-td>
      允许的最大迭代次数
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.eval_output_dir`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      评估输出目录
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.start_time`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      最好有 (Better have)
    </lark-td>
    <lark-td>
      会话开始时间戳（ISO 8601）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.data_source`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      数据来源，如：Github开源仓库
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      metada.source
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      数据来源人群：如前端工程师，后端工程师等等
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.model_system_prompt`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      最好有 (Better have)
    </lark-td>
    <lark-td>
      来自模型本身的提示词，和agent或者环境完全无关的
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.coding_agent_system_prompt`
    </lark-td>
    <lark-td>
      string
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      编码agent的系统提示，是轨迹的起点
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `metadata.tools`
    </lark-td>
    <lark-td>
      array
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      代理可用的工具列表
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      `trajectory`
    </lark-td>
    <lark-td>
      array
    </lark-td>
    <lark-td>
      必须 (Required)
    </lark-td>
    <lark-td>
      对话轮次和采取的操作数组
    </lark-td>
  </lark-tr>
</lark-table>

**git_context 字段定义**
此字段用于标准化记录代码变更，供应商需通过此字段交付文件状态，而非简单的文件覆盖记录。
1. git_context.initial_state
  类型：Object
  说明：任务开始前，工作区内所有相关文件的原始内容快照。
  格式：Key 为文件相对路径（相对于 cwd），Value 为文件完整内容字符串。
  约束：对于新建文件，该文件不出现在 initial_state 中。对于"从零创建"任务，可为空对象 {}。
2. git_context.final_diff
     类型：String
     说明：任务完成后，相对于初始状态的 Unified Diff（标准 git diff 输出）。
     约束：必须包含完整的 Diff Header（如 diff --git a/... b/...），支持 new file mode（新增文件）和代码行增删（+ /-）。

**trajectory 字段定义**
`trajectory` 是一个有序数组，每个元素为一条消息对象，遵循 Anthropic Messages API 风格结构。
消息基本结构
```json
{
  "role": "user" | "assistant",
  "content": <String | Array>
}
```


**agent工具调用名称规范（tool_use）**
不强制统一工具名称，但同一条记录内工具名称需保持自洽（`tool_use` 的 `id` 与对应 `tool_result` 的 `tool_use_id` 能正确关联）。常见工具名称参考：

<lark-table rows="8" cols="2" header-row="true" column-widths="143,607">

  <lark-tr>
    <lark-td>
      功能类别
    </lark-td>
    <lark-td>
      常见名称
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      执行终端命令
    </lark-td>
    <lark-td>
      `RunCommand`, `execute_command`, `execute_bash`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      读取文件
    </lark-td>
    <lark-td>
      `ReadFile`, `read_file`, `str_replace_editor(view)`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      写入/创建文件
    </lark-td>
    <lark-td>
      `WriteFile`, `write_to_file`, `str_replace_editor(create)`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      编辑文件
    </lark-td>
    <lark-td>
      `EditFile`, `replace_in_file`, `str_replace_editor(str_replace)`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      搜索文件
    </lark-td>
    <lark-td>
      `SearchFiles`, `search_files`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      列出目录
    </lark-td>
    <lark-td>
      `ListFiles`, `list_files`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      标记完成
    </lark-td>
    <lark-td>
      `AttemptCompletion`, `attempt_completion`
    </lark-td>
  </lark-tr>
</lark-table>

## 数据跳过规则
- 单个代码文件内容过长，ai在阅读代码时超过了ai上下文
- 此条pr对代码的更改过于复杂，ai的修改无法通过回归测试
- 在该条pr的提交版本下应用test.patch后运行测试没有报错，即不会出现FAIL_TO_PASS
## Dockerfile编写
- Dockerfile是构建docker环境的模板，需要针对不同的项目不同的pr进行针对性修改，使得项目可以在该dockerfile构建的docker环境中运行。
- 要求使用miniconda，工作目录为/testbed，基础镜像建议为ubuntu:22.04
## 最终需要交付的文件

#### 文件说明
<image token="BnqjbaMOqoImn7xZ074cBg7enUf" width="312" height="224" align="center"/>

- code.patch：该条pr对代码的修改，解决了该条pr对应的issue
- Dockerfile：docker环境的模板，通过该dockerfile构建的docker环境应使该条pr对应的代码版本正常运行
- final.diff：agent修复后的补丁文件，用于回归测试验证
- instance.json：命名为 仓库所有者_仓库名-pr编号.jaon，其中包含大部分该文件所需字段，我们需要在其中补充其他必须字段
- setup_env.sh：环境配置脚本，在构建docker的过程中会运行该脚本在docker中构建仓库运行所需环境，需要在这个文件中写该仓库的环境配置脚本，如依赖安装，项目构建，环境变量的设置等
- setup_repo.sh：仓库克隆脚本，在构建docker环境时，该脚本负责将仓库克隆到镜像中并切换到该条pr对应的分支，内容一般比较固定。如果仓库过大可以修改以使用浅克隆。
- test.patch：验证代码修改的测试用例更改补丁，一般包含测试用例的更改，用于测试该条pr对代码的修改是否有效。
- <text bgcolor="light-yellow">trajectory.json</text>：最终的必需轨迹文件，记录agent的工具调用，思考链
- run_verification.py：回归验证脚本，进入docker后挂载该脚本，运行脚本可以进行回归验证（注：有些数据不提供该文件，需要根据其他题目提供的进行修改）
---

# 总流程
1. 配置项目环境，构建镜像（在当前目录运行命令：docker build . -t [镜像名]）
1. 运行镜像并挂载相关文件
```bash
docker run -it --rm ^
-v "%CD%\run_verification.py:/testbed/run_verification.py" ^
-v "%CD%\code.patch:/testbed/code.patch" ^
-v "%CD%\test.patch:/testbed/test.patch" ^ 
[镜像名]
```

1. 配置环境，运行test.patch涉及的测试文件，不断更改环境配置直到测试全部通过，将过程中的更改写到配置环境的脚本中，使得镜像构建后便可直接实现test.patch中测试文件全部PASS（以python项目为例，假设test.patch中涉及的测试文件为：tests/test_text.py，则运行pytest -vs tests/test_text.py 命令进行测试，根据报错信息更改或添加依赖，将执行这些更改的命令写入到setup_env.sh中，直到运行测试时没有failed为止）
1. 针对code.patch的回归验证：应用test.patch，运行test.patch涉及的测试文件，预期会出现报错，再应用code.patch，再次运行测试，预期报错被修复，测试用例全部PASS（先进行测试：pytest -vs tests/test_text.py ，此时测试全部通过，应用test补丁：git apply -v ../test.patch，再次运行测试，此时测试会有报错，应用code补丁：git apply -v ../code.patch，再次运行测试，此时测试无报错，验证成功）
1. 运行run_verification.py验证文件，该文件会生成一个结果文件，其中包含解析出的FAIL_TO_PASS和PASS_TO_PASS，将这两个字段标注在instance.json中（python run_verification.py，cat result.json，复制所需的FAIL_TO_PASS和PASS_TO_PASS字段标注到instance.json中）
1. 退出镜像重新构建，构建出该仓库的直接可运行环境，启动镜像（注：如果拿到的数据是已经标注好的，即instance.json中已经有FAIL_TO_PASS和PASS_TO_PASS且这两个字段不为空，则可以直接从这一步开始）
1. 启动镜像时只挂载两个文件：用于回归验证的test.patch和agent插件
```bash
docker run -it --rm ^
-v "./test.patch:/testbed/test.patch" ^
-v "[插件在你电脑上的路径]:/testbed/claude-dev-3.76.0.vsix" ^ 
[镜像名]
```

1. 通过<text bgcolor="light-yellow">Container Tools</text>  和<text bgcolor="light-yellow">Dev Containers</text> 插件，将vscode链接到容器内
<image token="CKV9bfEP8oNQj4x0rpKcS7Nrnxe" width="1225" height="407" align="center"/>

<image token="PeiLbHOjOoAw6PxJkIVcDjcFnog" width="729" height="606" align="center"/>

1. 在链接到容器内的vscode中安装插件：在插件商店页面点击右上角的三个点，选择从vsix安装，然后选择/testbed目录下的claude-dev-3.76.0.vsix即可安装（该插件在后面有提供，一定不要下载插件商店的，并且一定要将插件文件挂载到容器中，在容器中进行安装，不可安装在宿主机中然后进入容器安装）
<image token="YeJFb90Tto4UoAx57v8cwoz5nmg" width="531" height="346" align="center"/>

1. 点击设置配置api key 和 base url，配置好之后点击Done
<image token="FqCDbOV7vouA01xwgqkc3Ihenxc" width="291" height="812" align="center"/>

<image token="SGQ4biZqWo7XE6xNATEcVjrinJ2" width="277" height="540" align="center"/>

1. 将agent切换到plan模式（输入框为黄色边框的即为plan模式），输入提示词和issue描述，让agent根据issue描述和提示词计划修改
1. 确认agent的计划无误后，将其切换到act模式执行plan
1. agent执行完毕后，必须要点击下面的开启新对话的选项
1. 运行`git diff > final.diff`获取更改补丁
1. `git checkout -- .` 放弃所有更改，使仓库回到原来的状态（新增的文件要手动删除）
1. 运行命令：git apply 

<lark-table rows="2" cols="2" column-widths="100,100">

  <lark-tr>
    <lark-td>
    </lark-td>
    <lark-td>
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
    </lark-td>
    <lark-td>
    </lark-td>
  </lark-tr>
</lark-table>

-v ../test.patch ，然后运行测试，确定其可以复现bug（注意测试的时候只测试test.patch涉及到的测试文件，下同）
1. 然后运行命令：git apply -v final.diff，运行测试，测试ai的补丁是否可以修复bug
1. 如果可以修复bug，则继续往下进行，如果不能，则删除对话记录和final.diff（重要），随后从第11步开始执行，优化提示词，直到ai的补丁可以修复bug（注意，不可直接或间接告诉ai任何test.patch和code.patch以及上一次尝试时的final.diff)
1. 将final.diff复制到宿主机，一定要注意这里选择LF
<image token="XcJ9b3G5Sotjl9xR3EWcXAT9nDe" width="1460" height="1033" align="center"/>

1. 使用`docker cp ``[哈希]``:root/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/tasks/``[目录名] ./ `命令导出这次的agent对话记录文件夹，文件夹存放在~/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/tasks/ 目录下 
1. 运行脚本提取所需信息到trajectory.json标注文件中，然后在两个标注文件中补充需要的字段：task_category和source
1. 将run_verification.py中针对code.patch的回归验证改为final.diff
<image token="NzuvbX4sGoEi5gxnX8EcQG37nGb" width="948" height="137" align="center"/>

1. 数据提取脚本如下（参考脚本）：
```python
import json
import os
import re
from pathlib import Path
import uuid

def extract_file_content(text):
    """从文本中提取文件路径和内容"""
    pattern = r'\[read_file for \'([^\']+)\'\]\s*Result:\n(.*)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        filepath = match.group(1).strip()
        content = match.group(2).strip()
        return filepath, content
    return None, None

def get_filename(filepath):
    """从文件路径中提取文件名"""
    return filepath.split('/')[-1] if '/' in filepath else filepath

# ... existing code ...
def convert_json_to_json(input_file, output_file, input_agent_prompt_info_file, input_agent_io_log_file):
     # 从输入文件路径中提取task_id（路径中最后一个反斜杠前的数字）
    task_id = ""
    path_parts = input_file.replace("\\", "/").split("/")
    for part in path_parts:
        if re.match(r'^\d+$', part):  # 检查是否为纯数字
            task_id = part
            break
    # 读取输入JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化字典
    INITIAL_STATE = {}
    seen_filenames = set()
    
    # 提取轨迹数据并构建INITIAL_STATE
    trajectory = data
    system_prompt = []  # 存储system_prompt
    # metrics = {}  # 存储metrics
    turn_count = 0  # 计算轮次
    instruction=""
    for item in data:
        if item["role"] == "user":
            user_content_parts = []
            
            # 处理user的content
            for content_item in item["content"]:
                if content_item["type"] == "text":
                    text = content_item["text"].strip()
                    if text.startswith("[read_file for '"):
                        filepath, content = extract_file_content(text)
                        if filepath and content:
                            filename = get_filename(filepath)
                            if filename not in seen_filenames and content != "(tool did not return anything)":
                                INITIAL_STATE[filepath] = content
                                seen_filenames.add(filename)    
                            continue
                    if text:
                        user_content_parts.append({
                            "type": "text",
                            "text": text
                        })
            # 将所有user的content添加到system_prompt
            if user_content_parts:
                for content_part in user_content_parts:
                    system_prompt.append({
                        "type": content_part["type"],
                        "text": content_part["text"]
                    })
        elif item["role"] == "assistant":
            assistant_content = []
            # 处理assistant的content
            for content_item in item["content"]:
                if content_item["type"] == "thinking":
                    # 保持thinking类型，包含thinking字段
                    thinking_content = {
                        "type": "thinking",
                        "thinking": content_item.get("thinking", "")
                    }
                    if "summary" in content_item:
                        thinking_content["summary"] = content_item["summary"]
                    assistant_content.append(thinking_content)
                
                elif content_item["type"] == "tool_use":
                    # 转换为tool_use类型，包含id、name、input字段
                    assistant_content.append({
                        "type": "tool_use",
                        "id": content_item.get("id", ""),
                        "name": content_item.get("name", ""),
                        "input": content_item.get("input", {})
                    })
                
                elif content_item["type"] == "text":
                    # 保持text类型
                    assistant_content.append({
                        "type": "text",
                        "text": content_item.get("text", "")
                    })
            
            # # 添加assistant消息到轨迹
            # if assistant_content:
            #     trajectory.append({
            #         "role": "assistant",
            #         "content": assistant_content
            #     })
            
            # 计算轮次：每遇到一个assistant就增加一轮
            if item["role"] == "assistant":
                turn_count += 1
            
            # 保存最后一个modelInfo.modelId
            if "modelInfo" in item:
                modelId = item["modelInfo"]["modelId"]
    # 将system_prompt的第一个元素的text添加到instruction
    instruction = data[0]["content"][0]["text"]
    # system_prompt = system_prompt[1:]  # 去掉system_prompt的第一个元素，因为第一个元素是用户提示词
        # 
    # 读取final.diff文件
    final_diff = ""
    diff_file = "final.diff"
    if os.path.exists(diff_file):
        with open(diff_file, 'r', encoding='utf-8') as f:
            final_diff = f.read()
    
    # 读取当前目录下的json文件，取其中的instance_id字段作为instance_id，取其中的repo字段作为repo...
    instance_id = ""
    base_commit = ""
    fail_to_pass = []
    pass_to_pass = []
    repo = ""
    language = ""
    problem_statement = ""
    for file in os.listdir("."):
        if file.endswith(".json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "instance_id" in data:
                    instance_id = data["instance_id"]
                    # break
                if "repo" in data:
                    repo = data["repo"]
                    # break
                if "base_commit" in data:
                    base_commit = data["base_commit"]
                    # break
                if "FAIL_TO_PASS" in data:
                    fail_to_pass = data["FAIL_TO_PASS"]
                    # break
                if "PASS_TO_PASS" in data:
                    pass_to_pass = data["PASS_TO_PASS"]
                    # break
                if "language" in data:
                    language = data["language"]
                    # break
                if "problem_statement" in data:
                    problem_statement = data["problem_statement"]
                    # break
    # 从instruction中提取problem_statement，将“。以下是具体的issue描述：”之后的内容作为problem_statement
    if not problem_statement:
        if "以下是具体的issue描述：" in instruction:
            print(000)
            problem_statement = instruction.split("以下是具体的issue描述：")[1].strip()
            # 如果problem_statement内容为空，则使用“以下是issue：”之后的内容
        else:
            problem_statement = instruction.split("以下是issue：")[1].strip()
                    # 如果problem_statement内容为空，则使用“以下是issue描述：”之后的内容
        if not problem_statement:
            problem_statement = instruction.split("以下是issue描述：")[1].strip()

    # 提取当前文件夹中test.patch文件的内容作为test_patch
    test_patch = ""
    test_file = "test.patch"
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            test_patch = f.read()
    # 提取当前文件夹中code.patch文件的内容作为patch
    patch = ""
    patch_file = "code.patch"
    if os.path.exists(patch_file):
        with open(patch_file, 'r', encoding='utf-8') as f:
            patch = f.read()
    thinking_mode = ""
    # 判断trajectory中的"role": "assistant"数据的content数组中是否有type为thinking的元素，有则思考模式为slow，否则为fast
    for item in trajectory:
        if item["role"] == "assistant":
            for content_item in item["content"]:
                if content_item["type"] == "thinking":
                    thinking_mode = "slow"
                    break
            else:
                thinking_mode = "fast"
                break
    
    
    if thinking_mode == "":
        thinking_mode = "fast"

    # 读取 指定目录下的agent_prompt_info.json文件，获取其中的coding_agent_system_prompt字段作为coding_agent_system_prompt
    coding_agent_system_prompt = ""
    if os.path.exists(input_agent_prompt_info_file):
        with open(input_agent_prompt_info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "coding_agent_system_prompt" in data:
                coding_agent_system_prompt = data["coding_agent_system_prompt"]

    # 读取指定目录下的agent_io_log.json文件，读取其中的requests字段中的tools字段作为tools
    tools = []
    if os.path.exists(input_agent_io_log_file):
        with open(input_agent_io_log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "requests" in data:
                if "tools" in data["requests"][0]:
                    tools = data["requests"][0]["tools"]
                
     # 构建输出JSON对象
    output_data = {
        "instance_id": instance_id,  # 类型: string  从json文件中提取instance_id
        "instruction": instruction,  # 类型: string，用户提示词  从json文件中提取instruction
        "instance": {
            "repo":repo,  # 类型: string，仓库路径  提取repo
            "base_commit":base_commit,  # 类型: string，基础提交哈希  提取base_commit
            "git_context":{
                "initial_state":INITIAL_STATE, # 类型：object，变更前仓库文件的初始状态
                "final_diff":final_diff
            }, # 类型：object，Git仓库上下文，包括initial state和final diff
            "problem_statement":problem_statement, # 类型 string，问题描述 
            "FAIL_TO_PASS":fail_to_pass, 
            "PASS_TO_PASS":pass_to_pass, 
            "patch":patch, # 类型 string，code.patch 
            "test_patch":test_patch, # 类型 string，test.patch 
            # "created_at":created_at # 类型 string，创建时间戳 （可选）TODO
        },  # 类型: object  嵌入instance.json
        "metadata":{
            "agent":"cline", # 类型 string，会话使用的智能体  默认cline
            "model":modelId, # 类型 string，会话使用的模型  
            "thinking_mode":thinking_mode, # 类型 string，思考模式 
            # "max_iterations":max_iterations, # 类型 number，最大迭代次数(可选) TODO
            "eval_output_dir":"/testbed", # 类型 string，评估输出目录 
            # "start_time":start_time, # 类型 string，会话开始时间戳（可选） TODO
            "data_source":"GitHub开源仓库", # 类型 string，数据来源 
            "source":"后端工程师", # 类型 string，采集数据的来源 ，这根据需求更改
            # "model_system_prompt":"You are Claude Opus....", # 类型 string，模型系统提示词 
            "coding_agent_system_prompt":coding_agent_system_prompt, # 类型 string，编码智能体系统提示词 
            "tools":tools # 类型 array，agent可用工具列表 
        }, # 类型：object，会话元数据和配置 
        "trajectory":trajectory, # 类型 array，会话轨迹 
        "task_id": task_id,  # 使用从文件路径中提取的数字
        "task_category": "",  # 这里可以根据需要填写
        "metrics": {  # 添加metrics字段
            "turn_count": turn_count
        },
        "language":language
    }
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output_data, ensure_ascii=False, indent=2))
    # 写入JSON文件 - 每行一个JSON对象，无缩进
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(output_data, ensure_ascii=False) + '\n')
    
    print(f"转换完成！已保存到 {output_file}")
    print(f"提取了 {len(INITIAL_STATE)} 个文件到 initial_state")
    print(f"系统提示词包含 {len(system_prompt)} 个项目")
    print(f"总共有 {turn_count} 轮对话")

if __name__ == "__main__":
    # 输入和输出文件路径
    metadata_dir = "1774842200684" # 修改为你的输入文件路径
    input_json_file = os.path.join(metadata_dir, "api_conversation_history.json") 
    input_agent_prompt_info_file = os.path.join(metadata_dir, "agent_prompt_info.json")
    input_agent_io_log_file = os.path.join(metadata_dir, "agent_io_log.json")
    output_json_file = "trajectory.json"  # 输出文件路径
    
    convert_json_to_json(input_json_file, output_json_file, input_agent_prompt_info_file, input_agent_io_log_file)

```

1. 插件(注意：确保cline插件的版本和来源；安装完成后需要重载窗口；在agent修复完成后需要开启新对话“strat new task”触发coding_agent_system_prompt字段的捕获)：
<image token="FFdgb1DMfobtHFxO66acnagRn2d" width="444" height="96" align="center"/>

<image token="OFWFb5D74oEQVAxTvEUc6DCPnMN" width="302" height="124" align="center"/>

<view type="1">

  <file token="VC2Ybm9mioEr1dx8OmYcvHe3n9e" name="cline-claude.vsix"/>

</view>

---

## 验收标准
###### **格式验收**

<lark-table rows="10" cols="3" header-row="true" column-widths="111,231,509">

  <lark-tr>
    <lark-td>
      #
    </lark-td>
    <lark-td>
      检查项
    </lark-td>
    <lark-td>
      通过标准
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-1
    </lark-td>
    <lark-td>
      JSON格式合法性
    </lark-td>
    <lark-td>
      为有效 JSON文件，可被 `json.loads()` 解析
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-2
    </lark-td>
    <lark-td>
      必填字段完备性
    </lark-td>
    <lark-td>
      上述所有必需的字段均存在且非空
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-3
    </lark-td>
    <lark-td>
      字段类型正确性
    </lark-td>
    <lark-td>
      各字段数据类型与上述必需字段中的定义一致
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-4
    </lark-td>
    <lark-td>
      `id` 唯一性
    </lark-td>
    <lark-td>
      全量数据中 `id` 无重复
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-5
    </lark-td>
    <lark-td>
      `task_category` 枚举合法
    </lark-td>
    <lark-td>
      仅取值 `"bug_fix"` 或 `"feature"`
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-6
    </lark-td>
    <lark-td>
      `trajectory` 非空
    </lark-td>
    <lark-td>
      至少包含 1 条 user 消息和 1 条 assistant 消息
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-7
    </lark-td>
    <lark-td>
      编码规范
    </lark-td>
    <lark-td>
      全部为 UTF-8 编码
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-8
    </lark-td>
    <lark-td>
      `final_diff` 格式
    </lark-td>
    <lark-td>
      包含完整 Diff Header（`diff --git a/... b/...`）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      F-9
    </lark-td>
    <lark-td>
      工具调用一致性
    </lark-td>
    <lark-td>
      assistant 消息中每个 `tool_use.id` 都有对应的 `tool_result.tool_use_id`
    </lark-td>
  </lark-tr>
</lark-table>

###### **内容逻辑验收**

<lark-table rows="6" cols="3" header-row="true" column-widths="81,261,521">

  <lark-tr>
    <lark-td>
      #
    </lark-td>
    <lark-td>
      检查项
    </lark-td>
    <lark-td>
      通过标准
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      C-1
    </lark-td>
    <lark-td>
      git 状态一致性
    </lark-td>
    <lark-td>
      `initial_state` + `git apply final_diff` 与最终文件状态一致性 ≥ 95%
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      C-2
    </lark-td>
    <lark-td>
      数据闭环
    </lark-td>
    <lark-td>
      Agent 已执行完成 planning中的所有任务
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      C-3
    </lark-td>
    <lark-td>
      Bug 修复闭环（`bug_fix` 任务）
    </lark-td>
    <lark-td>
      git initial_state 时测试样例可复现 Bug；git final_state 时回归测试通过
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      C-4
    </lark-td>
    <lark-td>
      功能开发验证（`feature` 任务）
    </lark-td>
    <lark-td>
      final_state 提供的测试样例可执行通过
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      C-5
    </lark-td>
    <lark-td>
      代码可执行性
    </lark-td>
    <lark-td>
      运行脚本中的 Bug 可修复，需求开发的样例脚本可执行
    </lark-td>
  </lark-tr>
</lark-table>

###### **完整 JSON 记录示例****（以下为精简示例，实际内容要多很多）**
```json
{
  "instance_id": "python-attrs__attrs-1410",
  "instruction": "<task>\n我当前的目录是有个python库attrs，我需要你帮我解决一个issue，注意，解决issue的时候你可以更改代码，但是一定不要修改测试文件，不要运行其他测试，此外也不需要验证你的修改。以下是issue：Getting this message because I both have the type annotation and type defined on a custom attribute class which is reasonable considering the ambiguity.\\n\\nHowever I think the message itself could be more helpful by displaying the name of the attribute to eliminate the variable hunt.\\n\\nMy suggested change is:\\n\\nattrs/src/attr/_make.py\\n\\nLine 2354 in 2afd663\\n\\n def from_counting_attr(cls, name, ca, type=None): \\n    @classmethod\\n    def from_counting_attr(cls, name, ca, type=None):\\n        # type holds the annotated \n</task>",
  "instance": {
    "repo": "python-attrs/attrs",
    "base_commit": "6bde3618237cdae312e4e7fb006690be2a3ee0f6",
    "git_context": {
      "initial_state": {
        "src/attr/_make.py": "# SPDX-License-Identifier: MIT\n\nfrom __future__ import annotations\n\nimport abc\nimport contextlib\nimport copy\nimport enum\nimport inspect\nimport itertools\nimport linecache\nimport sys\nimport types\nimport unicodedata\n\nfrom collections.abc import..."
        },
      "final_diff": "diff --git a/src/attr/_make.py b/src/attr/_make.py\nindex 0c5aa0b..3aedcb0 100644\n--- a/src/attr/_make.py\n+++ b/src/attr/_make.py\n@@ -2491,7 +2491,7 @@ class Attribute:\n         if type is None:\n             type = ca.type\n         elif ca.type is not None:\n-            msg = \"Type annotation and type argument cannot both be present\"\n+            msg = f\"Type annotation and type argument cannot both be present for {name}.\"\n             raise ValueError(msg)\n         return cls(\n             name,\n"
    },
    "problem_statement": "unhelpful message \"ValueError: Type annotation and type argument cannot both be present\"\nGetting this message because I both have the type...",
    "FAIL_TO_PASS": [
      "tests/test_annotations.py::TestAnnotations::test_catches_basic_type_conflict"
    ],
    "PASS_TO_PASS": [
      "tests/test_annotations.py::test_is_class_var['typing.ClassVar[dict]']",
      "tests/test_annotations.py::test_is_class_var[ClassVar]",
      "tests/test_annotations.py::test_is_class_var[t.ClassVar[int]]",
      "tests/test_annotations.py::test_is_class_var[typing.ClassVar]",
      "tests/test_annotations.py::TestAnnotations::test_annotations_strings[False]",
      "tests/test_annotations.py::TestAnnotations::test_annotations_strings[True]"
    ],
    "patch": "diff --git a/changelog.d/1410.change.md b/changelog.d/1410.change.md\nnew file mode 100644\nindex 000000000..0536da8f5\n--- /dev/null\n+++ b/changelog.d/1410.change.md\n@@ -0,0 +1,1 @@\n+The error message if an attribute has both an annotation and a type argument will now disclose _what_ attribute seems to be the problem.\ndiff --git a/src/attr/_make.py b/src/attr/_make.py\nindex 0c5aa0bd6..7439dc2ad 100644\n--...",
    "test_patch": "diff --git a/tests/test_annotations.py b/tests/test_annotations.py\nindex f37a1c0b0..5c6296634 100644\n--- a/tests/test_annotations.py\n+++ b/tests/test_annotations.py\n@@ -62,7 +62,7 @@ class C:\n                 x: int = attr.ib(type=int)\n \n         assert (\n-            \"Type annotation and type argument cannot both be present\",\n+            \"Type annotation and type argument cannot both be present for 'x'.\",\n         ) == e.value.args\n \n     def test_typing_annotations(self):\n"
  },
  "metadata": {
    "agent": "cline",
    "model": "claude-opus-4-6",
    "thinking_mode": "slow",
    "eval_output_dir": "/testbed",
    "data_source": "GitHub开源仓库",
    "source": "后端工程师",
    "coding_agent_system_prompt": "You are Cline, a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices.\n\nTOOL USE\n\nYou have access to a set of tools that are executed upon the user's approval. You may use multiple tools in a single response when the operations are independent (e.g., reading several files, searching in parallel). For dependent operations where one result informs the next, use tools sequentially. You will receive the results of all tool uses in the user's response....",
    "tools": [
      {
        "name": "ask_followup_question",
        "description": "Ask user a question for clarifying or gathering information needed to complete the task. For example, ask the user clarifying questions about a key implementation decision. You should only ask one question.",
        "input_schema": {
          "type": "object",
          "properties": {
            "question": {
              "type": "string",
              "description": "The single question to ask the user. E.g. \"How can I help you?\""
            },
            "options": {
              "type": "string",
              "description": "An array of 2-5 options (e.x: \"[\"Option 1\", \"Option 2\", \"Option 3\"]\") for the user to choose from. Each option should be a string describing a possible answer to the single question. You may not always need to provide options, but it may be helpful in many cases where it can save the user from having to type out a response manually. IMPORTANT: NEVER include an option to toggle to Act mode, as this would be something you need to direct the user to do manually themselves if needed."
            },
            "task_progress": {
              "type": "string",
              "description": "A checklist showing task progress after this tool use is completed. The task_progress parameter must be included as a separate parameter inside of the parent tool call, it must be separate from other parameters such as content, arguments, etc. (See 'UPDATING TASK PROGRESS' section for more details)"
            }
          },
          "required": [
            "question",
            "options"
          ]
        }
      },
      {
        "name": "execute_command",
        "description": "Request to execute a CLI command on the system. Use this when you need to perform system operations or run specific commands to accomplish any step in the user's task.",
        "input_schema": {
          "type": "object",
          "properties": {
            "command": {
              "type": "string",
              "description": "The CLI command to execute. This should be valid for the current operating system. Do not use the ~ character or $HOME to refer to the home directory. Always use absolute paths. The command will be executed from the current workspace, you do not need to cd to the workspace."
            },
            "requires_approval": {
              "type": "boolean",
              "description": "To indicate whether this command requires explicit user approval or interaction before it should be executed. For system/file altering operations like installing/uninstalling packages, removing/overwriting files, system configuration changes, network operations, or any commands that are considered potentially dangerous must be set to true. False for safe operations like running development servers, building projects, and other non-destructive operations."
            }
          },
          "required": [
            "command",
            "requires_approval"
          ]
        }
      },
      {
        "name": "read_file",
        "description": "Request to read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file you do not know the contents of, for example to analyze code, review text files, or extract information from configuration files. Automatically extracts raw text from PDF and DOCX files. May not be suitable for other types of binary files, as it returns the raw content as a string. Do NOT use this tool to list the contents of a directory. Only use this tool on files.",
        "input_schema": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "The path of the file to read (relative to the current working directory /testbed/attrs) Use @workspace:path syntax (e.g., @frontend:src/index.ts) to specify a workspace."
            },
            "task_progress": {
              "type": "string",
              "description": "A checklist showing task progress after this tool use is completed. The task_progress parameter must be included as a separate parameter inside of the parent tool call, it must be separate from other parameters such as content, arguments, etc. (See 'UPDATING TASK PROGRESS' section for more details)"
            }
          },
          "required": [
            "path"
          ]
        }
      },
      {
        "name": "write_to_file",
        "description": "[IMPORTANT: Always output the absolutePath first] Request to write content to a file at the specified path. If the file exists, it will be overwritten with the provided content. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file.",
        "input_schema": {
          "type": "object",
          "properties": {
            "absolutePath": {
              "type": "string",
              "description": "The absolute path to the file to write to."
            },
            "content": {
              "type": "string",
              "description": "After providing the path so a file can be created, then use this to provide the content to write to the file."
            },
            "task_progress": {
              "type": "string",
              "description": "A checklist showing task progress after this tool use is completed. The task_progress parameter must be included as a separate parameter inside of the parent tool call, it must be separate from other parameters such as content, arguments, etc. (See 'UPDATING TASK PROGRESS' section for more details)"
            }
          },
          "required": [
            "absolutePath",
            "content"
          ]
        }
      },
      {
        "...":"..."
      }
    ]
  },
  "trajectory": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "<task>\n我当前的目录是有个python库attrs，我需要你帮我解决一个issue，注意，解决issue的时候你可以更改代码，但是一定不要修改测试文件，不要运行其他测试，此外也不需要验证你的修改。以下是issue：Getting this message because I both have the type annotation and type defined on a custom attribute class which is reasonable considering the ambiguity.\\n\\nHowever I think the message itself could be more helpful by displaying the name of the attribute..."
        },
        {
          "type": "text",
          "text": "\n# task_progress List (Optional - Plan Mode)\n\nWhile in PLAN MODE, if you've outlined concrete steps or requirements for the user, you may include ..."
        },
        {
          "type": "text",
          "text": "<environment_details>\n# Visual Studio Code Visible Files\nsrc/attr/_make.py\n\n# Visual Studio Code Open Tabs\nsrc/attr/_make.py\n\n# Current Time\n3/30/2026, 6:35:35 AM (UTC, UTC+0:00)\n\n# Current Working Directory (/testbed/attrs) Files\n.git_archival.txt\n.gitattributes\n.gitignore\n.pre-commit-config.yaml\n.python-version-default\n.readthedocs.yaml\nCHANGELOG.md\nCITATION.cff\nconftest.py\nLICENSE\npyproject.toml\nREADME.md\ntox.ini\nbench/\nbench/test_benchmarks.py\nchangelog.d/..."
        }
      ],
      "ts": 1774852535847
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "thinking",
          "thinking": "Let me look at the current error message in the code to understand what needs to be changed.",
          "signature": "EpcCClkIDBgCKkC3S22fZdxqbnzMLLvZ/jPd8aUmFAeRBGdrZefgydvs/ixeuhJEHZDKPlwgd/41ZU0jt0zjKSAnIq9SUnsa70+MMg9jbGF1ZGUtb3B1cy00LTY4ABIMy/U/wqFFGili4w68GgwYfRYpjOp4CFkB+FsiMBvHbRP3551eKk/8rAkg1tfa9BiDSl8ITvZegXvXjQKeummWuZaBYxH+PzqKCr2K1ipsPDf8sCluXDdbwPgihUJDDtYmgNH9uU31S0eNm1fnl0ki1/QK6AGJnRkNRmakt63PGEn5ccCR9SMMv7uXfpAmyY12IlFPnjJDBny+hRypUk7KQcn7JW94HviXLN+YzxBU+6W/s4UldJgzoOVOGAE=",
          "summary": []
        },
        {
          "type": "tool_use",
          "id": "toolu_01VNJvy2cV85as3mSLNUMLXx",
          "name": "search_files",
          "input": {
            "path": "src/attr/_make.py",
            "regex": "Type annotation and type argument"
          },
          "call_id": "toolu_01VNJvy2cV85as3mSLNUMLXx",
          "reasoning_details": []
        }
      ],
      "modelInfo": {
        "modelId": "claude-opus-4-6",
        "providerId": "anthropic",
        "mode": "plan"
      },
      "metrics": {
        "tokens": {
          "prompt": 10,
          "completion": 108,
          "cached": 8791
        }
      },
      "ts": 1774852540038
    },
    {
      "...":"..."
    }
  ],
  "task_id": "1774852534913",
  "task_category": "feature",
  "metrics": {
    "turn_count": 5
  },
  "language": "Python"
}
```

###### **自我纠错轨迹示例（高价值）** {folded="true"}
以下为精简示例，展示 Agent 遇到报错后自主分析并修复的行为链(客户所需的高价值数据)：
```json
{
  "trajectory": [
    {"role": "user", "content": "修复 login 函数中密码校验失败的 bug"},
    {"role": "assistant", "content": [
      {"type": "thinking", "thinking": "先读取代码理解现有逻辑..."},
      {"type": "tool_use", "id": "t1", "name": "ReadFile", "input": {"file_path": "auth.py"}}
    ]},
    {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "t1", "content": "def login(user, pwd): ..."}
    ]},
    {"role": "assistant", "content": [
      {"type": "thinking", "thinking": "发现问题：hash 比较用了 == 而非 hmac.compare_digest，但先尝试修复..."},
      {"type": "tool_use", "id": "t2", "name": "EditFile", "input": {"file_path": "auth.py", "old_str": "...", "new_str": "..."}}
    ]},
    {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "t2", "content": "File edited successfully."}
    ]},
    {"role": "assistant", "content": [
      {"type": "tool_use", "id": "t3", "name": "RunCommand", "input": {"command": "pytest test_auth.py -v"}}
    ]},
    {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "t3", "content": "FAILED test_login_with_special_chars - AssertionError", "is_error": true}
    ]},
    {"role": "assistant", "content": [
      {"type": "thinking", "thinking": "测试失败了，特殊字符场景没处理。需要在 hash 之前对密码做 encoding 处理..."},
      {"type": "text", "text": "测试未通过，特殊字符场景有问题，我来修正。"},
      {"type": "tool_use", "id": "t4", "name": "EditFile", "input": {"file_path": "auth.py", "old_str": "...", "new_str": "..."}}
    ]}
  ]
}
```

<quote-container>
以上为精简结构示意，省略了部分字段。实际数据需包含完整的顶层字段。
</quote-container>

---

# ** 常见问题**
##### **新建文件（feature 任务）时 initial_state 怎么填？**
新建文件不需要出现在 `initial_state` 中。`initial_state` 可以是空对象 `{}`（从零创建任务），`final_diff` 中使用 `new file mode` 标记新增文件。注意：final.diff中修改的所有文件的初始内容（也就是未修改前的内容）一定要在`initial_state`中，要保证`initial_state` + `final_diff` 严格等于仓库任务结束后的状态
##### **如何判定"自我纠错"任务？**
轨迹中包含以下模式即认定为自我纠错：Agent 执行操作 → 收到错误结果（`is_error: true` 或输出含报错信息）→ Agent 分析错误原因 → 重新修改代码/命令 → 最终成功。
##### **"简单问答"和"结对编程"怎么区分？**
结对编程轨迹的核心特征：Agent 需要实际操作文件系统（读写文件、执行命令），且 `git_context.final_diff` 非空。如果交互仅停留在文本对话层面，没有实际的代码变更，则属于简单问答，**不满足**采集要求。
##### 如果agent修改代码后无法通过回归验证怎么办？
重置仓库到该提交的原始状态，删除所有新增文件，包括final.diff，开启新对话，调整提示词，让agent重新修改。
##### agent总是修改不通过，我可以告诉它code的相关内容吗？
不可以，因为我们要采集的数据要尽可能贴近真实用户的交互轨迹，所以test.patch和code.patch仅用来验证ai修改是否有效，绝对不可以透露这两个补丁文件的相关内容，不过可以分析agent修改不通过的原因，在agent plan之后输入提示词让其向着期望的方向更改。
##### 我可以先应用test.patch复现bug之后再让agent修改吗？
不可以，ai修改之前的代码仓库必须严格保持该commit的基础状态，不能有任何新增和修改。
##### agent修改逻辑代码的同时修改了测试代码，导致test.patch应用失败无法进行回归验证怎么办？
在提示词中加入让agent不能修改测试代码的限制，让agent使用临时测试文件进行修改。
##### 在仓库该issue的页面上tag没有说明是feature和bug_fix怎么办？
需要人工阅读issue描述，以判断这个issue是feature还是bug_fix。
##### 如果题目过于简单，agent很快修改好并且通过回归验证的数据算作有效吗？
<text bgcolor="light-yellow">如果api调用轮次小于5轮，即运行标注脚本后，标注文件的turn_count字段的值小于5，应算作无效数据。</text>
##### 如果initial_state字段中的文件存在为完全覆盖final.diff的情况怎么办？
使用这个脚本将缺失的文件补上（使用方法：python export_final_diff_files_from_image.py [数据文件夹，即final.diff所在文件夹的路径]  [镜像名]），脚本会从容器中抓取所有final.diff涉及到的文件的初始状态，然后选择缺失的文件，粘贴到initial_state字段中：
```python
#!/usr/bin/env python3
"""
Export non-added files referenced by final.diff from a running Docker image.

Output format:
{
  "path/to/file.py": "full file content",
  "path/to/another.py": "full file content"
}
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path

def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def normalize_repo_relative_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    if normalized.startswith("a/") or normalized.startswith("b/"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    parts = normalized.split("/")
    if len(parts) >= 3 and parts[0] == "testbed":
        normalized = "/".join(parts[2:])
    return normalized

def parse_non_added_files(final_diff: str) -> list[str]:
    required_files: list[str] = []
    current_old_path: str | None = None
    current_is_new_file = False

    for raw_line in final_diff.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("diff --git a/") and " b/" in line:
            if current_old_path and not current_is_new_file:
                required_files.append(current_old_path)
            current_old_path = normalize_repo_relative_path(
                line[len("diff --git a/") :].split(" b/", 1)[0]
            )
            current_is_new_file = False
            continue

        if current_old_path is None:
            continue

        if line.startswith("new file mode") or line.startswith("--- /dev/null"):
            current_is_new_file = True

    if current_old_path and not current_is_new_file:
        required_files.append(current_old_path)

    return sorted(dict.fromkeys(required_files))

def load_trajectory_record(project_dir: Path) -> dict:
    trajectory_path = project_dir / "trajectory.json"
    if not trajectory_path.is_file():
        return {}

    content = read_text(trajectory_path).strip()
    if not content:
        return {}

    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        return {}

    if isinstance(obj, dict):
        return obj
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return obj[0]
    return {}

def get_repo_path(project_dir: Path) -> str:
    setup_repo_path = project_dir / "setup_repo.sh"
    if setup_repo_path.is_file():
        for raw_line in read_text(setup_repo_path).splitlines():
            line = raw_line.strip()
            if not line.startswith("git clone"):
                continue
            target = line.split()[-1].strip()
            if target.startswith("/testbed/"):
                return target.rstrip("/")
            break

    record = load_trajectory_record(project_dir)
    instance = record.get("instance", {})
    if isinstance(instance, dict):
        repo = instance.get("repo", "")
        if isinstance(repo, str) and repo.strip():
            repo_name = repo.rstrip("/").split("/")[-1]
            if repo_name:
                return f"/testbed/{repo_name}"

    return "/testbed"

def run_command(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )

def start_container(image_name: str) -> str:
    result = run_command(["docker", "run", "-d", "--rm", image_name, "sleep", "3600"])
    if result.returncode != 0:
        raise RuntimeError(f"failed to start container: {result.stderr.strip()}")
    return result.stdout.strip()

def stop_container(container_id: str) -> None:
    run_command(["docker", "stop", container_id], timeout=30)

def read_file_from_container(container_id: str, file_path: str) -> str:
    result = run_command(
        ["docker", "exec", container_id, "bash", "-lc", f"cat -- {shlex.quote(file_path)}"],
        timeout=60,
    )
    if result.returncode != 0:
        raise FileNotFoundError(
            f"failed to read {file_path} from container: {result.stderr.strip()}"
        )
    return result.stdout

def export_files(project_dir: Path, image_name: str) -> dict[str, str]:
    final_diff = read_text(project_dir / "final.diff")
    if not final_diff.strip():
        raise FileNotFoundError(f"final.diff not found or empty: {project_dir / 'final.diff'}")

    target_files = parse_non_added_files(final_diff)
    repo_path = get_repo_path(project_dir)

    container_id = start_container(image_name)
    try:
        result: dict[str, str] = {}
        for relative_path in target_files:
            container_path = f"{repo_path.rstrip('/')}/{relative_path}"
            result[relative_path] = read_file_from_container(container_id, container_path)
        return result
    finally:
        stop_container(container_id)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export non-added files from final.diff out of a Docker image."
    )
    parser.add_argument("project_dir", help="task directory containing final.diff")
    parser.add_argument("image_name", help="Docker image name")
    parser.add_argument(
        "--output",
        default="",
        help="output JSON path (default: <project_dir>/final_diff_files.json)",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        raise SystemExit(f"project_dir does not exist: {project_dir}")

    output_path = (
        Path(args.output).resolve()
        if args.output
        else project_dir / "final_diff_files.json"
    )

    exported = export_files(project_dir, args.image_name)
    output_path.write_text(
        json.dumps(exported, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"exported {len(exported)} files to {output_path}")

if __name__ == "__main__":
    main()

```


