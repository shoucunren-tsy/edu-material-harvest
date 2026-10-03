# 安装与接入 · 高校公开资料采集

把本 skill 装进**你自己的 Claude Code**，然后用它采集**任何一所** `*.edu.cn` 高校的
培养方案 / 专业介绍 / 课程大纲 / 年度报告，逐份落盘并登记可溯源台账。

> 不需要编程。你只需要会：把文件夹放进指定位置、照着命令敲、看输出。

---

## 一、它做什么

给定 `{学校名, 官方域名}`，一条命令：

1. **自动发现**：摸清该校材料挂在哪些栏目页、附件直链是什么（每条都实探过 HTTP / 内容类型 / 文件头）；
2. **下载 + 校验 + 去重**：只下真文件，重复的剔除，按「学校 / 材料类型」分目录存好；
3. **出台账**：Excel（逐文件明细 + 页面级链接台账）+ CSV，每行含**下载直链**与**承载页**。

你后续做分析时，能一键跳回学校官网核对原文。

---

## 二、前置条件

| 需要 | 说明 | 没有会怎样 |
|---|---|---|
| **Claude Code** | 本 skill 跑在它里面 | —— |
| **Python 3.9+** | 建议 3.10+；本 skill 在 3.12 上跑通 | 脚本跑不了 |
| **curl** | Windows 10 1803+ **自带** | 无法下载/探测（会报 `缺少依赖：curl`） |
| **解压器**（可选） | 7-Zip 或 Bandizip（命令行）；采 RAR/ZIP 打包件时才需要 | 打包件那几项记「缺解压器」并跳过，其余照常 |
| **PowerShell**（可选） | Windows 自带；用于"删到回收站" | 删除降级为"隔离到临时目录"（文件不丢） |

**外部工具全部自动探测**（PATH → 常见安装位置），也可用环境变量覆盖：
`EDU_7Z` / `EDU_CURL` / `EDU_POWERSHELL`。

**Python 库**（建议装进你的项目 venv）：

```bash
python -m pip install -r scripts/requirements.txt
```

| 库 | 用途 | 缺失行为 |
|---|---|---|
| `pymupdf` | PDF 取词（课程名/专业名命名） | 文件名退化为通用名（打 WARN，不崩） |
| `openpyxl` | 生成 Excel 台账（**核心产物**） | **报错退出**；或 `report.py --csv-only` 降级只出 CSV |
| `python-docx` | 生成使用教程 docx | 报错退出（仅在跑 `generate_tutorial.py` 时） |

> 缺依赖本 skill **要吵不要哑**：不会静默降级到"看起来成功"。

---

## 三、安装（drop-in，零配置）

**主形态 = 扁平文件夹**。整目录丢进 Claude Code 的 skills 目录即可：

```bash
# 把整个 edu-material-harvest-高校公开资料采集（自己创作） 文件夹复制到：
<你的 CLAUDE_CONFIG_DIR>/skills/
```

- 默认 skills 目录一般是 `~/.claude/skills/`。
- 若你设过环境变量 `CLAUDE_CONFIG_DIR`（本机就是），skills 目录在
  **`<CLAUDE_CONFIG_DIR>/skills/`**——照着放即可。
- 放好后**新开一个 Claude Code 会话**，说「帮我采集 XX 大学的培养方案」即触发。

> 为什么是"扁平文件夹"而不是"插件"？因为 Claude Code **不支持嵌套 SKILL.md**——
> `SKILL.md` 必须在本文件夹根目录。整文件夹既可直接 drop-in，也可作为 npm/plugin 的一部分
> （见第六节），**同一份文件两种用法**。

---

## 四、接入新学校：三步

以"湖南大学"为例（换成你的学校，域名换成实测的）：

### 第 1 步 · 解析域名（关键，别猜）

用 WebSearch 搜 `"<校名> 教务处"` 或 `"<校名> 信息公开"`，**确认官方 `*.edu.cn` 域名**。
- 认准 `edu.cn` 后缀；别把独立学院 / 分校 / 培训机构当主校。
- 教务子域不一定是 `jwc.`（有的校是 `jw.`）。

### 第 2 步 · 只侦察（默认，不下载）

```bash
python scripts/discover.py --school 湖南大学 --domain hnu.edu.cn
```

产出在 `discover_out/`：

| 文件 | 看什么 |
|---|---|
| `candidates.md` | **人眼确认表**：命中的栏目页、确认的附件（带 HTTP/ctype/字节）、被拦的页 |
| `jobs.json` | 确认可下载的清单（喂给 download.py） |
| `html_links.json` | 纯 HTML 材料页（只登记，不下载） |
| `unverified.json` | 没通过探测的候选（不自动下载） |
| `discover_report.json` | 过程统计（可达主机、扫描页数、拦截数、耗时） |

### 第 3 步 · 拍板 + 采集

看完 `candidates.md` 没问题后，一键下载 + 出台账：

```bash
python scripts/discover.py --school 湖南大学 --domain hnu.edu.cn --kinds 年度报告 --auto
```

得到 `<out>/新增数据/湖南大学/年度报告/*.pdf` 与 `<out>/采集台账.xlsx`。
**再跑一遍是幂等的**（已存在即跳过，不重复下载、不丢记录）。

> 批量：把学校写进 `references/schools_seed.example.json`（复制成 `schools_seed.json`），
> 然后 `python scripts/discover.py --seeds schools_seed.json`。

---

## 五、故障对照表

| 现象 | 原因 | 解决 |
|---|---|---|
| `缺少依赖：curl` | 无 curl | Windows 装 curl 或设 `EDU_CURL` 指向可执行文件 |
| `缺少依赖：解压器…` | 无 7z/Bandizip | 采打包件才需要；装 7-Zip 或设 `EDU_7Z`。不影响其余项 |
| 报错 `未安装 openpyxl…` | 缺 Excel 库 | `pip install openpyxl`，或加 `--csv-only` 只出 CSV |
| 域名被拒 `不是 *.edu.cn` | 传了非 edu 域名 | 核对域名，必须是官方教育域名 |
| `apex、www 及已知子域均不可达` | 域名错 / 网络到不了 | 核对官方域名；`--no-subdomains` 试试；换网络 |
| 结果里很多 `blocked` | 站点有 WAF / JS 挑战 | **真实边界**，不是 bug；换子域或手动补 |
| `candidates.md` 里某些行没确认 | 返回 HTML 或状态异常 | 正常——它们只登记不下载；确认真文件才下 |
| 下载中途卡死 | 高校附件服务器中途停传 | curl 已带 `--speed-time 30 --speed-limit 20480` 自动中止 |
| 中文输出乱码 | Windows GBK 终端 | `common.py` 已自动 utf-8；自建脚本用 `sys.stdout.reconfigure` |
| 重复跑没新增 | 幂等生效 | 正常；已存在即跳过 |

---

## 六、分发形态（可选）

**主形态（推荐）**：整文件夹丢进 `skills/`，如上。

**附形态（插件 marketplace）**：本文件夹自带 `.claude-plugin/plugin.json` 与
`.claude-plugin/marketplace.json`（**可直接抄用**）。但插件对目录层级有硬要求：
`SKILL.md` 必须在 `<插件仓库根>/skills/<名>/SKILL.md`，而 `.claude-plugin/` 必须在**仓库根**。

所以发布成插件的正确布局是：

```
<插件仓库根>/                     ← 一个 git 仓库
├── .claude-plugin/
│   ├── plugin.json              ← 本文件夹 .claude-plugin/ 里的两个文件
│   └── marketplace.json         ← 复制到仓库根
└── skills/
    └── edu-material-harvest/    ← 把本 skill 文件夹整个放这里（可改名，但 plugin.json 的 name 要对上）
        ├── SKILL.md
        └── ...
```

然后他人：

```
/plugin marketplace add <git-url 或本地路径>
/plugin install edu-material-harvest@edu-material-harvest
```

> ⚠️ 两点：
> 1. 插件**必须经 marketplace 分发**，不能凭空下载——需要你把仓库托管到 Git（GitHub 等）或给出本地路径。
> 2. 本文件夹的 `.claude-plugin/` 是**给仓库根用的模板**；放在 skill 文件夹里只是"随包携带"，不影响
>    drop-in 使用（drop-in 形态不读它）。
> 3. 插件形态与 drop-in 形态**父目录不同、子目录相同**（都是 `skills/<名>/SKILL.md`），
>    同一份 `SKILL.md` 与 `scripts/` 直接复用，无需改动。

---

## 七、红线（本 skill 的底线，别改坏）

1. **只采官方 `*.edu.cn` 免登录公开源**；登录墙后的一律放弃。
2. **绝不猜域名、绝不编 URL**——每条链接都实测过。
3. **原始数据目录只读**：不删、不改、不移、不改名；产物一律另存新文件。
4. **删除一律走回收站**（无 PowerShell 时隔离到临时目录，**绝不永久删除**）。
5. **全自动只授权"怎么跑"，不授权"跑什么"**——扩大采集范围（换校 / 换材料类型）须用户点名。
