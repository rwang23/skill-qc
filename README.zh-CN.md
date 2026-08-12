# SkillRigor

[English](README.md)

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-0b5b4b)
![自审 100/100](https://img.shields.io/badge/自审-100%2F100-0b5b4b)
![安全门 PASS](https://img.shields.io/badge/安全门-PASS-0b5b4b)
![证据 E2](https://img.shields.io/badge/证据-E2-d7ad53)
![MIT License](https://img.shields.io/badge/license-MIT-d7684e)

SkillRigor 一次只审计一个 Agent Skill。它会给出可解释的 100 分质量评分、独立安全门、证据等级，以及英文或中文 HTML 网页报告。

它默认只读，不会修复、安装、发布或执行被审计的 Skill。

## 为什么做这个工具

论文 [《What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files》](https://arxiv.org/abs/2608.08453) 发现，公开 Skill 最常见的问题并不是复杂攻击，而是路由元数据薄弱、正文不可执行或过度膨胀，以及资源组织不当。论文的路由实验还显示，元数据合格的 Skill 更容易被正确检索。

SkillRigor 把这些研究结论、Agent Skills 公开规范和实际发布控制整理成一套可重复运行的单 Skill 评判流程。它把 Skill 当作一个需要被发现、加载、执行和维护的软件依赖，而不是一份很长的 Prompt 文档。

## 一份报告会回答什么

- 当前 Skill 的总分是多少？
- 八个维度分别为什么得分或扣分？
- 安全门是 `PASS`、`REVIEW` 还是 `BLOCKED`？
- 当前结论由 E1、E2、E3 还是 E4 证据支持？
- 每个维度下一步最值得改什么？
- 和上一轮相比，解决了哪些问题，又新增了哪些问题？

可以直接打开仓库中的示例：

- [英文自审报告](examples/self-audit.en.html)
- [中文自审报告](examples/self-audit.zh-CN.html)
- [机器可读 JSON](examples/self-audit.json)

## 评分模型

| 维度 | 权重 | 主要评判内容 |
|---|---:|---|
| 路由能力 | 18 | 名称、Description、Trigger 与发现契约 |
| 可执行性 | 16 | 可执行工作流、明确输出与停止条件 |
| 上下文效率 | 10 | 激活正文是否聚焦，是否做到渐进披露 |
| 资源组织 | 9 | 脚本、参考资料、资产与链接完整性 |
| 安全性 | 20 | 凭据、政策绕过、破坏性操作与权限边界 |
| 可移植性 | 8 | 用户路径、固定模型与环境假设 |
| 有效性准备度 | 12 | 当前成熟度要求的路由与回归材料 |
| 可维护性 | 7 | 未完成指令、元数据一致性与生命周期契约 |

总分、安全门和证据等级必须分开看。`100 / PASS / E2` 表示 Skill 包满足全部计分契约，并且具备均衡的路由测试；它不表示真实场景中的效果已经得到证明。E3 需要同一版本的目标客户端记录，E4 还需要真实运行记录和责任人复核。

完整规则见[评分标准](references/rubric.md)、[证据契约](references/evidence-schema.md)和[报告契约](references/report-contract.md)。

## 快速开始

SkillRigor 只依赖 Python 标准库，建议使用 Python 3.11 或更高版本。

```bash
git clone https://github.com/rwang23/skill-rigor.git
cd skill-rigor
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity library \
  --locale zh-CN \
  --json-out audit.json \
  --html-out audit.html
```

目标目录的根部必须直接包含一个 `SKILL.md`。工具会拒绝 Skill 集合目录，保证总分和所有解释始终只对应一个 Skill。

### 与上一轮比较

```bash
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity library \
  --baseline round-1.json \
  --locale zh-CN \
  --json-out round-2.json \
  --html-out round-2.html
```

第二轮报告会列出分数变化、已解决问题和新增问题。只有评分规则版本相同时，分数变化才可直接比较。

### 加入 E3 或 E4 证据

```bash
python scripts/skill_audit.py audit /path/to/one-skill \
  --profile portable \
  --maturity governed \
  --evidence evidence.json \
  --locale zh-CN \
  --json-out audit.json \
  --html-out audit.html
```

只有当证据中的 `target_revision` 与当前 `SKILL.md` 的 SHA-256 完全一致时，E3/E4 才会生效。

### 把现有 JSON 渲染成中文报告

```bash
python scripts/skill_audit.py render audit.json audit.zh-CN.html --locale zh-CN
```

### 退出码

| 代码 | 含义 |
|---:|---|
| 0 | `PASS` |
| 1 | `REVIEW` |
| 2 | `BLOCKED` |
| 3 | 输入无效或执行错误 |

## 默认保护本地路径

CLI 在保存 JSON 和 HTML 前，会自动把目标绝对路径替换成 `<SKILL:name>`。如果报告中还可能出现其他私有路径，可以重复传入：

```bash
--redact-root "/private/workspace=<WORKSPACE>"
```

疑似凭据的具体值不会进入报告，只记录模式类别、文件和行号。

## 作为 Agent Skill 使用

仓库根目录本身就是一个有效的 Skill 包。把它放入所使用 Agent 的 Skill 发现目录，并保持目录名为 `skill-rigor` 即可。它的路由范围刻意保持狭窄：只负责单个 Agent Skill 的只读审计，不接管普通代码审查、Skill 创建或批量盘点。

主工作流在 [SKILL.md](SKILL.md)，详细规则在 `references/`，确定性实现放在 `scripts/`，中英文报告模板放在 `assets/`。这样启动阶段只需要加载简短的路由信息。

## 开发与自审

运行完整测试：

```bash
python -m unittest discover -s tests -v
```

生成项目自审：

```bash
python scripts/skill_audit.py audit . \
  --profile portable \
  --maturity governed \
  --locale en \
  --observed-at 2026-08-11T23:21:19-04:00 \
  --json-out examples/self-audit.json \
  --html-out examples/self-audit.en.html

python scripts/skill_audit.py render \
  examples/self-audit.json \
  examples/self-audit.zh-CN.html \
  --locale zh-CN
```

任何检测规则或计分变化，都需要一个先失败的聚焦用例、通过后的回归测试，以及评分规则版本复核。具体见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 已知边界

- 静态规则可能误报或漏报，尤其是安全示例、否定句、Persona 表达和特殊本地契约。
- E1/E2 不能证明目标客户端一定会正确路由，也不能证明真实任务效果。
- 工具不会执行目标 Skill 包中的脚本。
- 论文研究的是公开 Skill，企业内部 Skill 的分布可能不同。
- 报告干净不等于已经获得安装、发布或执行权限。

## 安全问题

请通过 [GitHub Security Advisories](https://github.com/rwang23/skill-rigor/security/advisories/new) 报告疑似漏洞。不要在公开 Issue 中提交真实凭据或私有审计报告。详见 [SECURITY.md](SECURITY.md)。

## 许可证

[MIT](LICENSE)
