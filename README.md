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

# 批量：照 skills/edu-material-harvest/references/schools_seed.example.json 写 schools_seed.json（每校一个先核实过的域名）
python skills/edu-material-harvest/scripts/discover.py --seeds schools_seed.json --auto         # 逐校采集，各出到子目录
```

## 跨 Agent 可用（MCP）

采集内核带一个**零依赖** stdio MCP 服务端，除 Claude Code 外，Codex / WorkBuddy /
千问办公等支持 MCP 的客户端也能用**同一套能力**（工具、Resources、Prompts 齐全；
长任务自动转后台，不会憋超时）：

```
python skills/edu-material-harvest/scripts/mcp_server.py --print-config   # 出连接信息
python skills/edu-material-harvest/scripts/mcp_server.py --install claude # 或 codex
```

原理与四客户端接入法见：`skills/edu-material-harvest/references/09-Agent接入与MCP.md`

## 详细文档

- 安装接入与故障对照：`skills/edu-material-harvest/README-安装与接入.md`
- 自动发现逻辑（设计思路 / 判据 / 边界）：`skills/edu-material-harvest/references/08-自动发现逻辑.md`
- 跨 Agent 接入与 MCP（架构 / 协议 / 工具 / 排障）：`skills/edu-material-harvest/references/09-Agent接入与MCP.md`
- 使用教程：`skills/edu-material-harvest/使用教程_高校公开资料采集.docx`

## 红线

只采官方 `*.edu.cn` 免登录公开源；绝不猜域名、绝不编造 URL；每条链接都实测过。
