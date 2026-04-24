# 组件方法签名

> 注：详细业务规则将在 CONSTRUCTION 阶段的功能设计中定义。此处仅列出方法签名和高层用途。

## 后端 Service 方法

### AuthService (auth_app/services.py)
```python
class AuthService:
    def login(username: str, password: str) -> dict          # 验证凭据，返回 {token, user}
    def logout(token: Token) -> None                         # 删除 Token
    def get_current_user(request) -> User                    # 获取当前用户信息
    def create_user(data: dict) -> User                      # 创建用户
    def update_user(user_id: int, data: dict) -> User        # 更新用户信息
    def toggle_user_status(user_id: int) -> User             # 切换启用/禁用
    def reset_password(user_id: int, new_password: str) -> None  # 管理员重置密码
```

### CategoryService (products/services.py)
```python
class CategoryService:
    def get_tree(dimension: str) -> list                     # 获取指定维度的分类树
    def create(data: dict) -> Category                       # 创建分类
    def update(category_id: int, data: dict) -> Category     # 更新分类
    def delete(category_id: int) -> None                     # 删除分类（检查子分类和产品）
    def reorder(items: list[dict]) -> None                   # 批量更新排序
```

### ProductImageService (products/services.py)
```python
class ProductImageService:
    def upload_images(product_id: int, files: list) -> list  # 批量上传图片+生成缩略图
    def delete_image(image_id: int) -> None                  # 删除图片及缩略图
    def set_cover(image_id: int) -> None                     # 设为封面
    def update_order(product_id: int, order: list) -> None   # 更新图片排序
```

### ProductImportService (products/services.py)
```python
class ProductImportService:
    def parse_excel(file) -> dict                            # 解析 Excel，返回 {success, failed, preview}
    def execute_import(parsed_data: list) -> dict            # 执行批量导入
    def generate_template() -> bytes                         # 生成导入模板文件
```

### QuoteService (quotes/services.py)
```python
class QuoteService:
    def duplicate(quote_id: int, user: User) -> Quote        # 复制报价单含明细
    def export_pdf(quote_id: int) -> bytes                   # WeasyPrint 生成 PDF
    def recalculate_total(quote_id: int) -> Decimal          # 重新计算总金额
```

### ShareService (sharing/services.py)
```python
class ShareService:
    def create_link(data: dict, user: User) -> ShareLink     # 创建分享链接
    def verify_password(token: str, password: str) -> bool   # 验证分享密码
    def get_shared_content(token: str) -> dict               # 获取分享内容
    def log_access(share_link: ShareLink, request) -> None   # 记录访问日志
    def track_click(share_link: ShareLink, data: dict) -> None  # 记录点击追踪
```

### DashboardService (dashboard/services.py) — 新增
```python
class DashboardService:
    def get_stats() -> dict                                  # 聚合统计数据
    def get_recent_activities(limit: int) -> list            # 最近活动列表
    def get_monthly_stats() -> dict                          # 本月统计
```

### FileStorageService (common/file_storage.py)
```python
class FileStorageService:
    def upload(file, subdirectory: str) -> str               # 上传文件，返回相对路径
    def delete(file_path: str) -> None                       # 删除文件
    def generate_thumbnail(image_path: str, size: tuple) -> str  # 生成缩略图
```

---

## 前端 Service 方法

### authService.ts
```typescript
login(username: string, password: string): Promise<{token: string, user: User}>
logout(): Promise<void>
getMe(): Promise<User>
getUsers(): Promise<PaginatedResponse<User>>
createUser(data: CreateUserDTO): Promise<User>
updateUser(id: number, data: UpdateUserDTO): Promise<User>
toggleUserStatus(id: number): Promise<User>
resetPassword(id: number, newPassword: string): Promise<void>
```

### productService.ts
```typescript
getProducts(params: ProductQueryParams): Promise<PaginatedResponse<Product>>
getProduct(id: number): Promise<ProductDetail>
createProduct(data: CreateProductDTO): Promise<Product>
updateProduct(id: number, data: UpdateProductDTO): Promise<Product>
deleteProduct(id: number): Promise<void>
uploadImages(id: number, files: File[]): Promise<ProductImage[]>
deleteImage(imageId: number): Promise<void>
setCoverImage(imageId: number): Promise<void>
updateImageOrder(id: number, order: number[]): Promise<void>
importProducts(file: File): Promise<ImportResult>
downloadTemplate(): Promise<Blob>
getConfigs(productId: number): Promise<ProductConfig[]>
createConfig(productId: number, data: CreateConfigDTO): Promise<ProductConfig>
updateConfig(configId: number, data: UpdateConfigDTO): Promise<ProductConfig>
deleteConfig(configId: number): Promise<void>
getCategories(params?: CategoryQueryParams): Promise<Category[]>
getCategoryTree(dimension: string): Promise<CategoryTree[]>
createCategory(data: CreateCategoryDTO): Promise<Category>
updateCategory(id: number, data: UpdateCategoryDTO): Promise<Category>
deleteCategory(id: number): Promise<void>
reorderCategories(items: ReorderItem[]): Promise<void>
```

### dashboardService.ts — 新增
```typescript
getStats(): Promise<DashboardStats>
getRecentActivities(limit?: number): Promise<Activity[]>
getMonthlyStats(): Promise<MonthlyStats>
```

### shareService.ts
```typescript
getShares(): Promise<PaginatedResponse<ShareLink>>
createShare(data: CreateShareDTO): Promise<ShareLink>
deleteShare(id: number): Promise<void>
getSharedContent(token: string): Promise<SharedContent>
verifySharePassword(token: string, password: string): Promise<boolean>
trackClick(token: string, data: ClickTrackData): Promise<void>  // 新增
```

---

## Store 定义

### authStore.ts
```typescript
interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}
```

### productStore.ts
```typescript
interface ProductState {
  products: Product[]
  total: number
  loading: boolean
  filters: { search?: string; origin?: string; category?: number; is_active?: boolean }
  pagination: { page: number; pageSize: number }
  fetchProducts: () => Promise<void>
  setFilters: (filters: Partial<ProductState['filters']>) => void
  setPage: (page: number) => void
}
```
