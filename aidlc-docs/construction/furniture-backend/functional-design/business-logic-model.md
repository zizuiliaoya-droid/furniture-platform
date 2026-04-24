# 业务逻辑模型 — Unit 1 后端

## 1. AuthService 业务流程

### login(username, password)
```
1. 查询 User(username=username)
2. IF 用户不存在 → 返回 400 "用户名或密码错误"
3. IF user.is_active == False → 返回 400 "账号已被禁用"
4. IF check_password 失败 → 返回 400 "用户名或密码错误"
5. 删除该用户已有的 Token（确保单 Token）
6. 创建新 Token
7. 返回 {token: token.key, user: UserSerializer(user)}
```

### reset_password(user_id, new_password)
```
1. 查询 User(id=user_id)
2. IF 用户不存在 → 返回 404
3. user.set_password(new_password)
4. user.save()
5. 删除该用户已有的 Token（强制重新登录）
```

---

## 2. ProductImportService 业务流程

### parse_excel(file)
```
1. 验证文件格式为 .xlsx
2. 使用 openpyxl 读取工作表
3. 遍历每行：
   a. 验证必填字段（名称、产地）
   b. 验证产地值在 IMPORT/DOMESTIC/CUSTOM 中
   c. 检查编号唯一性（数据库 + 当前批次内）
   d. 查找分类名称对应的 Category
   e. 分类不存在 → 标记失败
4. 返回 {
     success_count: N,
     failed_count: M,
     preview: [{row, data, status, error}],
     parsed_data: [valid_rows]
   }
```

### execute_import(parsed_data)
```
1. 批量创建 Product 对象
2. 设置 created_by 为当前用户
3. 返回 {imported_count: N}
```

---

## 3. QuoteService 业务流程

### duplicate(quote_id, user)
```
1. 查询 Quote(id=quote_id) 含所有 QuoteItem
2. IF 不存在 → 返回 404
3. 创建新 Quote:
   - title = 原标题 + "(副本)"
   - customer_name, notes, terms 复制
   - status = DRAFT
   - created_by = user
4. 遍历原 QuoteItem，创建副本:
   - 复制所有字段（product, product_name, config_name, unit_price, quantity, discount, subtotal, sort_order）
   - quote = 新报价单
5. 计算 total_amount
6. 返回新报价单
```

### export_pdf(quote_id)
```
1. 查询 Quote(id=quote_id) 含所有 QuoteItem
2. IF 不存在 → 返回 404
3. 渲染 HTML 模板（报价单布局）
4. WeasyPrint 将 HTML 转为 PDF
5. 返回 PDF bytes，Content-Type: application/pdf
```

### 状态流转验证
```
VALID_TRANSITIONS = {
    'DRAFT': ['SENT', 'CANCELLED'],
    'SENT': ['CONFIRMED', 'CANCELLED'],
    'CONFIRMED': ['CANCELLED'],
    'CANCELLED': [],  # 终态
}

def change_status(quote, new_status):
    IF new_status not in VALID_TRANSITIONS[quote.status]:
        → 返回 400 "不允许的状态变更"
    quote.status = new_status
    quote.save()
```

---

## 4. ShareService 业务流程

### get_shared_content(token)
```
1. 查询 ShareLink(token=token)
2. IF 不存在 → 返回 404
3. IF is_active == False → 返回 403 "链接已失效"
4. IF expires_at 不为空且已过期 → 返回 403 "链接已过期"
5. IF max_access_count 不为空且 access_count >= max_access_count → 返回 403 "链接已失效"
6. IF password_hash 不为空 → 返回 {requires_password: True, title: ...}
7. access_count += 1
8. 记录 ShareAccessLog
9. 根据 content_type 查询对应内容:
   - PRODUCT → Product + Images + Configs
   - CASE → Case + Images + Products
   - QUOTE → Quote + QuoteItems
   - CATALOG → 所有上架产品（分页）
10. 返回内容
```

### track_click(share_link, data)
```
1. 创建 ClickTrackingLog:
   - share_link = share_link
   - event_type = data.event_type
   - object_id = data.object_id
   - object_name = data.object_name
   - ip_address = request.META
```

---

## 5. DashboardService 业务流程

### get_stats()
```
1. 全量统计:
   - product_count = Product.filter(is_active=True).count()
   - case_count = Case.count()
   - quote_count = Quote.count()
   - document_count = Document.count()
2. 本月新增:
   - month_start = 本月第一天
   - new_products = Product.filter(created_at__gte=month_start, is_active=True).count()
   - new_cases = Case.filter(created_at__gte=month_start).count()
   - new_quotes = Quote.filter(created_at__gte=month_start).count()
3. 最近 30 天每日统计:
   - 按 created_at__date 分组，统计每天的新增数
   - 返回 [{date, products, cases, quotes}] × 30
4. 最近活动:
   - Quote.order_by('-updated_at')[:10]
5. 返回聚合结果
```

---

## 6. FileStorageService 业务流程

### upload(file, subdirectory)
```
1. 生成路径: {subdirectory}/{YYYYMMDD}/{uuid4}_{filename}
2. 确保目录存在
3. 写入文件到 MEDIA_ROOT/{path}
4. 返回相对路径
```

### generate_thumbnail(image_path, size)
```
1. 使用 Pillow 打开图片
2. 计算等比缩放尺寸
3. 居中裁剪到目标尺寸
4. 保存缩略图，路径为原路径加 _{size_name} 后缀
5. 返回缩略图相对路径
```

---

## 7. 错误处理

### 全局异常处理器 (common/exceptions.py)
```
- ValidationError → 400 {field: [errors]}
- NotFound → 404 {detail: "Not found"}
- PermissionDenied → 403 {detail: "Permission denied"}
- ParseError → 400 {detail: "Parse error"}
- 未捕获异常 → 500 {detail: "Internal server error"}
```

### 文件操作错误
```
- 文件过大 → 400 "文件大小超过限制"
- 格式不支持 → 400 "不支持的文件格式"
- 存储失败 → 500 "文件保存失败"
```
