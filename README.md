# 祈飞财务结算 · 原型与 PRD

商业结算平台「祈飞财务结算」的单文件可交互原型 + 配套 PRD。

- 对外版本：**v1.0**（2026-10-23 定版）
- 对应原型内部迭代 v1.28.4，逐版本迭代过程见 `qifei-settlement-prd.md` 文末「变更记录」

## 在线预览

| 入口 | 链接 |
| --- | --- |
| 原型入口页 | https://yechangmian.github.io/qifei-finance-settlement/ |
| 直接打开原型 | https://yechangmian.github.io/qifei-finance-settlement/qifei-settlement-demo.html |
| 需求文档 PRD（在线阅读） | https://yechangmian.github.io/qifei-finance-settlement/qifei-settlement-prd.html |
| 源码仓库 | https://github.com/YeChangMian/qifei-finance-settlement |

在线预览由 GitHub Pages 提供（源：`main` 分支根目录）。原型为单文件、无外部依赖，打开即用。

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `qifei-settlement-demo.html` | 单文件可交互原型（内联 CSS / JS / 图片，双击即可在浏览器打开，无需构建、无外部依赖） |
| `qifei-settlement-prd.md` | 产品需求文档源文件（Markdown），与原型严格同步维护 |
| `qifei-settlement-prd.html` | PRD 的渲染版（由 `.md` 自动生成，带排版，可在 GitHub Pages 直接阅读，避免 `.md` 以原文展示） |
| `build_prd_html.py` | 把 `qifei-settlement-prd.md` 转成 `qifei-settlement-prd.html` 的脚本 |
| `qifei-qa.py` | 自动 QA 脚本：headless Chrome 跑 31 个场景（结构检查 + 运行时异常检查 + 截图） |

## 菜单结构

| 菜单 | 内容 |
| --- | --- |
| 祈飞结算商品维护 | 商品维度佣金规则，含 5 个渠道费率（直播/短视频/商品卡/推荐卡/其他）、通用佣金率、批量导入、结算规则编辑与结束结算 |
| 祈飞达播结算维护 | 达人维度结算：达人结算范围三模式、达人通用佣金率、达人带货新增/编辑、带货范围（指定商品 / 全店商品）与特别佣金商品、结算时间段筛选、双页签（指定佣金结算 / 不结算达人） |
| 特殊品牌结算 | 占位页，功能建设中 |
| 店铺档案 | 店铺信息（只读）+ 达人结算范围设置，切换即时联动达播页 |

## 本地使用

```bash
# 直接打开原型（或用浏览器打开该文件）
open qifei-settlement-demo.html

# 跑自动 QA（需要本机安装 Chrome，脚本默认路径 /Applications/Google Chrome.app/...）
python3 qifei-qa.py
```

## 版本约定

- 对外版本号：`v1.0`，之后在此基线上的小修订用 `v1.0.1 / v1.0.2…`
- 内部迭代号（v1.28.x 等）仅用于过程追溯，记录在 PRD「变更记录」中
