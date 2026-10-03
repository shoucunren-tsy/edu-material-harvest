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

安装后，在 Claude Code 里说「帮我采集 XX 大学的培养方案」即可触发。也可直接跑脚本：

```
python skills/edu-material-harvest/scripts/discover.py --school <校名> --domain <域名>          # 只侦察
python skills/edu-material-harvest/scripts/discover.py --school <校名> --domain <域名> --auto   # 采集 + 出台账
```

## 详细文档

- 安装接入与故障对照：`skills/edu-material-harvest/README-安装与接入.md`
- 自动发现逻辑（设计思路 / 判据 / 边界）：`skills/edu-material-harvest/references/08-自动发现逻辑.md`
- 使用教程：`skills/edu-material-harvest/使用教程_高校公开资料采集.docx`

## 红线

只采官方 `*.edu.cn` 免登录公开源；绝不猜域名、绝不编造 URL；每条链接都实测过。
