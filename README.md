# edu-material-harvest · 高校公开资料采集

给定「学校名 + 官方域名」，从**官方免登录 `*.edu.cn` 公开源**自动发现并采集高校的
**培养方案 / 专业介绍 / 课程大纲 / 年度报告**，逐份落盘并登记**可溯源台账**（下载直链 + 承载页）。
适用于**任意中国高校，不限地域**。

## 安装（Claude Code 插件）

```
/plugin marketplace add <本仓库 URL 或本地路径>
/plugin install edu-material-harvest@edu-material-harvest
```

## 用法

在 Claude Code 里**直接说需求**即可——它会先联网核实每所学校的**官方域名**（绝不猜域名），再自动发现、逐份下载并出台账。例如：

- 单校 · 某类材料：`帮我采集华中科技大学的年度报告`
- 单校 · 四类全采：`把北京大学的培养方案、专业介绍、课程大纲、年度报告都采下来`
- 承载页直采（站点栏目乱、全站爬容易采到假货时）：`只采这几个页面：<承载页 URL1> <承载页 URL2>`
- 地区批量：`把湖南的 985 高校（中南大学、湖南大学、国防科技大学）的培养方案都采了，各校分开存`
- 地区批量（211 / 双一流同理）：把名单换成你要的学校即可，不限省份

⚠️ 三点如实说：① 能采到什么取决于该校是否有**官方免登录公开源**（站点被拦截或不可达时可能无果）；
② 批量是**按你给的名单逐校做**，每校都会先核实域名——请先给出具体名单，别写"某地区所有高校"；
③ 只采官方免登录源，不碰需要登录/付费的内容。

也可直接跑脚本：

```
# 单校
python skills/edu-material-harvest/scripts/discover.py --school <校名> --domain <域名>          # 只侦察
python skills/edu-material-harvest/scripts/discover.py --school <校名> --domain <域名> --auto   # 采集 + 出台账

# 批量（自己给名单）：照 skills/edu-material-harvest/references/schools_seed.example.json 写 schools_seed.json
python skills/edu-material-harvest/scripts/discover.py --seeds schools_seed.json --auto         # 逐校采集，各出到子目录

# 地区批量（内置教育部高校名单，按 省/城市/层次/985·211 生成名单；域名由你上传或由 Agent 现搜）
python skills/edu-material-harvest/scripts/region_seeds.py --province 湖北 --preset 985 --out seeds.json
python skills/edu-material-harvest/scripts/discover.py --seeds seeds.json --auto
```

## 跨 Agent 可用（MCP）

采集内核带一个**零依赖** stdio MCP 服务端（纯 Python，**不用 `pip install` 任何东西**），
除 Claude Code 外，Codex / WorkBuddy / 千问办公 / Claude Desktop / Cursor / Cline 等任何支持
MCP 的客户端都能挂上**同一套采集能力**（工具、Resources、Prompts 齐全；长任务自动转后台，不会憋超时）。

### 安装：把这段 JSON 贴进客户端的 MCP 配置

```json
{
  "mcpServers": {
    "edu-material-harvest": {
      "command": "python",
      "args": [
        "<本仓库克隆到本地的绝对路径>/skills/edu-material-harvest/scripts/mcp_server.py"
      ]
    }
  }
}
```

按你的机器改两处：

- `command`：填 `python` 即可；**若客户端找不到 python**（客户端通常不继承你终端的 PATH），
  换成解释器的**绝对路径**，例如 `C:/Python312/python.exe`。
- `args[0]`：换成你 clone 后 `mcp_server.py` 的**绝对路径**（正斜杠 `/` 或反斜杠 `\\` 都行）。

> **最省事的做法**：clone 后跑一次自带命令，它会**自动打印填好你本机绝对路径的同一段 JSON**，
> 直接复制粘贴：
>
> ```
> python skills/edu-material-harvest/scripts/mcp_server.py --print-config
> ```
>
> 其中 Claude Code / Codex 还能一键写配置：
> `--install claude`（或 `--install codex`），Codex 用 `codex mcp get edu-material-harvest` 验证。

挂上后客户端里会出现 `env_check`、`region_seeds`（地区名单）、`harvest_school`（一键）、
`harvest_many`（批量多校）、`harvest_pages`（承载页直采）、`build_ledger`、`read_artifacts`、
`job_wait` 等工具。原理与四客户端接入法见：
`skills/edu-material-harvest/references/09-Agent接入与MCP.md`

## 详细文档

- 安装接入与故障对照：`skills/edu-material-harvest/README-安装与接入.md`
- 自动发现逻辑（设计思路 / 判据 / 边界）：`skills/edu-material-harvest/references/08-自动发现逻辑.md`
- 跨 Agent 接入与 MCP（架构 / 协议 / 工具 / 排障）：`skills/edu-material-harvest/references/09-Agent接入与MCP.md`
- 地区批量（省份/985·211 → 逐校，两路域名 + 溯源）：`skills/edu-material-harvest/references/10-地区批量.md`
- 使用教程：`skills/edu-material-harvest/使用教程_高校公开资料采集.docx`

## 红线

只采官方 `*.edu.cn` 免登录公开源；绝不猜域名、绝不编造 URL；每条链接都实测过。
