# 家具软装内部管理平台 — 后端

Django REST Framework 后端 API 服务。

## 技术栈
- Django 6.x + DRF 3.17
- PostgreSQL 16
- WeasyPrint (PDF导出)
- Pillow (缩略图)
- openpyxl (Excel导入)

## 本地开发
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export DB_ENGINE=sqlite  # 本地用 SQLite
python manage.py migrate
python scripts/create_admin.py
python manage.py runserver
```

## 环境变量
参见 `.env.example`

## API 文档
- 认证: `/api/auth/`
- 产品: `/api/products/`, `/api/categories/`
- 图册: `/api/catalog/`
- 案例: `/api/cases/`
- 文档: `/api/documents/`
- 报价: `/api/quotes/`
- 分享: `/api/shares/`, `/api/share/{token}/`
- 搜索: `/api/search/`
- 仪表盘: `/api/dashboard/stats/`
