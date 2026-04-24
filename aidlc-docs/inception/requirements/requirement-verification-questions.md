# 需求验证问题

请回答以下问题，帮助我更好地理解项目需求。请在每个问题的 [Answer]: 标签后填写选项字母。

## Question 1
登录页的台灯交互动画使用了 GSAP 及其插件（Draggable, MorphSVGPlugin）。GSAP 的商业插件（如 MorphSVGPlugin）需要 Club GreenSock 会员许可。你的项目许可情况是？

A) 已有 GSAP 商业许可（Club GreenSock 会员）
B) 使用免费替代方案实现类似效果（如用 CSS 动画 + 开源库替代 MorphSVG）
C) 计划购买 GSAP 商业许可
D) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question 2
"咔哒"音效文件如何提供？

A) 我会提供音效文件（mp3/wav）
B) 使用 Web Audio API 程序化生成简单的咔哒声
C) 从免费音效库中选取一个合适的
D) Other (please describe after [Answer]: tag below)

[Answer]: D，不需要音效

## Question 3
PDF 报价单导出使用 WeasyPrint，它需要系统级依赖（cairo, pango 等）。在 Railway 测试环境中，你希望如何处理？

A) 在 Dockerfile 中安装 WeasyPrint 的系统依赖（增加镜像体积约 200MB+）
B) 测试阶段暂不实现 PDF 导出功能，生产环境再启用
C) 使用纯 Python 的 PDF 库替代（如 reportlab），避免系统依赖
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4
关于 Excel 批量导入产品功能，导入模板的字段结构是否已确定？

A) 已确定，按开发文档中的 Product 模型字段设计（名称、编号、产地、描述、最低售价、分类）
B) 需要自定义模板字段，我会提供具体格式
C) 先按基础字段实现，后续根据使用反馈调整
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5
前端 UI 设计风格要求"包豪斯风格定制主题"和"自定义字体（DM Sans + Inter + Noto Sans SC）"。字体加载方式？

A) 使用 Google Fonts CDN 加载
B) 将字体文件打包到项目中（自托管），避免外网依赖
C) 测试环境用 CDN，生产环境自托管（考虑 NAS 可能无外网）
D) Other (please describe after [Answer]: tag below)

[Answer]: D，前端UI的设计采用UI UI pro max的方案，要考虑到nas可能无外网

## Question 6
分享链接的公开访问页面（/s/:token）是否也需要包豪斯风格的 UI 设计？还是使用简洁的独立样式？

A) 与主系统保持一致的包豪斯风格
B) 使用简洁独立的样式，突出内容展示
C) 基本风格一致，但简化布局（无侧边栏，纯内容展示）
D) Other (please describe after [Answer]: tag below)

[Answer]: D，与主系统保持一致的风格

## Question 7
生产环境部署到 Synology NAS 后，外网访问方式的优先级？

A) 主要局域网使用，外网访问是次要需求
B) 需要稳定的外网访问（通过 DDNS + 端口映射）
C) 使用 Synology QuickConnect 作为外网访问方案
D) 暂不考虑外网访问，后续再配置
E) Other (please describe after [Answer]: tag below)

[Answer]: C，分享可能需要外网，分享给外部客户来访问

## Question 8
关于首页（/ 路由），开发文档中未详细描述首页内容。首页应该展示什么？

A) 仪表盘概览（产品数量、案例数量、最近报价单、最近活动等统计信息）
B) 直接跳转到产品图册页面（以图册作为默认首页）
C) 快捷入口卡片（产品管理、案例管理、报价管理等模块的快捷入口）
D) 简洁的欢迎页 + 常用功能快捷入口
E) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 9
项目的 GitHub 仓库结构偏好？

A) 单仓库（monorepo）：frontend/ 和 backend/ 在同一个仓库
B) 双仓库：前端和后端分开两个独立仓库
C) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 10
开发优先级排序 — 你希望先实现哪些核心模块？（可多选，用逗号分隔）

A) 用户认证 + 登录页（台灯交互）
B) 产品管理 + 产品图册
C) 客户案例
D) 内部文档管理
E) 报价方案
F) 分享功能 + 全局搜索
G) 全部同时开发，不分优先级
H) Other (please describe after [Answer]: tag below)

[Answer]: G
