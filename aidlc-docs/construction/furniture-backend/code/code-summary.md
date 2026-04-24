# 代码摘要 — Unit 1 后端

## 生成文件清单

| 文件 | 说明 |
|------|------|
| backend/manage.py | Django 管理命令入口 |
| backend/config/__init__.py | 包初始化 |
| backend/config/settings.py | 全局配置（DB/REST/CORS/Auth/WhiteNoise/Media） |
| backend/config/urls.py | 根路由（10 个 app） |
| backend/config/wsgi.py | WSGI 入口 |
| backend/requirements.txt | Python 依赖（10 个包） |
| backend/.env.example | 环境变量模板 |
| backend/common/file_storage.py | FileStorageService（上传/删除/缩略图） |
| backend/common/pagination.py | StandardPagination（20条/页） |
| backend/common/exceptions.py | 全局异常处理器 |
| backend/auth_app/* | 用户认证（User模型/登录/登出/用户管理/权限/密码重置） |
| backend/products/* | 产品管理（5模型/分类树/图片/配置/搜索/Excel导入） |
| backend/catalog/* | 产品图册（只读浏览/搜索） |
| backend/cases/* | 客户案例（3模型/CRUD/图片/关联产品） |
| backend/documents/* | 内部文档（2模型/文件夹树/上传/下载/标签） |
| backend/quotes/* | 报价方案（2模型/CRUD/明细/状态流转/PDF导出/复制） |
| backend/sharing/* | 分享功能（3模型/链接/验证/点击追踪） |
| backend/search/* | 全局搜索（跨4模块） |
| backend/dashboard/* | 仪表盘（全量+月度+30天每日统计） |
| backend/scripts/create_admin.py | 初始管理员创建 |
| backend/entrypoint.sh | Docker 启动脚本 |
| backend/Dockerfile | Docker 构建（含 WeasyPrint） |
| backend/Procfile | Railway 部署配置 |
| backend/runtime.txt | Python 版本 |
| backend/templates/quotes/pdf_template.html | 报价单 PDF 模板 |

## API 端点统计
- 认证: 7 端点
- 产品: 14 端点
- 分类: 6 端点
- 图册: 2 端点
- 案例: 7 端点
- 文档: 8 端点
- 报价: 9 端点
- 分享: 6 端点
- 搜索: 1 端点
- 仪表盘: 1 端点
- **合计: 61 端点**

## 用户故事覆盖
全部 29 个后端相关故事已实现（US-1.1 为纯前端）。
