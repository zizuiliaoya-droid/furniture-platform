"""Product management models."""
import hashlib
import json

from django.conf import settings
from django.db import models


class Brand(models.Model):
    """品牌字典"""
    name = models.CharField(max_length=100)
    is_self_owned = models.BooleanField(default=False, help_text='是否自有品牌')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Category(models.Model):
    """产品分类（过渡保留，作为筛选项字典使用）"""
    DIMENSION_CHOICES = [
        ('TYPE', '按类型'),
        ('SPACE', '按空间'),
        ('ORIGIN', '按产地'),
    ]
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    dimension = models.CharField(max_length=10, choices=DIMENSION_CHOICES, blank=True, default='TYPE')
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('parent', 'name', 'dimension')
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Product(models.Model):
    """产品"""
    ORIGIN_CHOICES = [
        ('IMPORT', '进口'),
        ('DOMESTIC', '国产'),
    ]
    CATEGORY_L1_CHOICES = [
        ('SEATING', 'Seating'),
        ('DESKS_WORKSTATIONS', 'Desks & Workstations'),
        ('TABLE', 'Table'),
        ('STORAGE', 'Storage'),
        ('ACCESSORIES', 'Accessories'),
        ('EDUCATION', 'Education'),
    ]
    CATEGORY_L2_CHOICES = [
        # Seating
        ('TASK_CHAIR', 'Task Chair'),
        ('EXECUTIVE_CHAIR', 'Executive Chair'),
        ('CONFERENCE_CHAIR', 'Conference Chair'),
        ('STOOL', 'Stool'),
        ('LOUNGE_CHAIR', 'Lounge Chair'),
        ('STACKING_CHAIR', 'Stacking Chair'),
        ('BENCH', 'Bench'),
        # Desks & Workstations
        ('HEIGHT_ADJUSTABLE_DESK', 'Height Adjustable Desk'),
        ('FIXED_DESK', 'Fixed Desk'),
        ('WORKSTATION_CLUSTER', 'Workstation Cluster'),
        ('EXECUTIVE_DESK', 'Executive Desk'),
        # Table
        ('CONFERENCE_TABLE', 'Conference Table'),
        ('COFFEE_TABLE', 'Coffee Table'),
        ('TRAINING_TABLE', 'Training Table'),
        ('DINING_TABLE', 'Dining Table'),
        # Storage
        ('FILING_CABINET', 'Filing Cabinet'),
        ('BOOKSHELF', 'Bookshelf'),
        ('LOCKER', 'Locker'),
        ('CREDENZA', 'Credenza'),
        # Accessories
        ('MONITOR_ARM', 'Monitor Arm'),
        ('CABLE_MANAGEMENT', 'Cable Management'),
        ('DESK_LAMP', 'Desk Lamp'),
        ('WHITEBOARD', 'Whiteboard'),
        ('ACOUSTIC_PANEL', 'Acoustic Panel'),
        # Education
        ('STUDENT_DESK', 'Student Desk'),
        ('LECTURE_CHAIR', 'Lecture Chair'),
        ('COLLABORATIVE_TABLE', 'Collaborative Table'),
    ]
    LEAD_TIME_CHOICES = [
        ('WITHIN_45D', '45天内'),
        ('2_4M_VIETNAM', '2-4月【越南】'),
        ('2_4M_MALAYSIA', '2-4月【马来西亚】'),
        ('4_6M_EU', '4-6月【荷兰/意大利/德国】'),
    ]
    PRICING_MODE_CHOICES = [
        ('MATRIX', '配置-价格映射表'),
        ('RULE', '基准价+加价规则'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, default='')

    # 新分类体系
    category_l1 = models.CharField(max_length=20, choices=CATEGORY_L1_CHOICES, default='SEATING')
    category_l2 = models.CharField(max_length=40, choices=CATEGORY_L2_CHOICES, blank=True, default='')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True, blank=True, related_name='products')
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default='IMPORT')
    lead_time = models.CharField(max_length=40, choices=LEAD_TIME_CHOICES, blank=True, default='')

    # 价格
    pricing_mode = models.CharField(max_length=10, choices=PRICING_MODE_CHOICES, default='MATRIX')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     help_text='仅 RULE 模式使用')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='最低售价（列表展示）')

    # 尺寸
    length_mm = models.IntegerField(null=True, blank=True, help_text='长度(mm)')
    width_mm = models.IntegerField(null=True, blank=True, help_text='宽度(mm)')
    height_mm = models.IntegerField(null=True, blank=True, help_text='高度(mm)')

    # 扩展信息
    official_url = models.URLField(max_length=500, blank=True, default='')
    material_album = models.JSONField(default=list, blank=True, help_text='可选材质图册（图片路径数组）')
    model_3d_url = models.URLField(max_length=500, blank=True, default='')

    # 状态
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    # 过渡保留（旧分类体系）
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='primary_products')
    categories = models.ManyToManyField(Category, through='ProductCategory', related_name='products', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['origin']),
            models.Index(fields=['category_l1']),
            models.Index(fields=['category_l1', 'category_l2']),
            models.Index(fields=['lead_time']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """产品-分类多对多（过渡保留）"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'category')


class ProductImage(models.Model):
    """产品图片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_path = models.CharField(max_length=500)
    thumbnail_path = models.JSONField(default=dict, blank=True)
    sort_order = models.IntegerField(default=0)
    is_cover = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']


class ProductConfig(models.Model):
    """产品配置（旧组合配置，兼容保留）"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='configs')
    config_name = models.CharField(max_length=200)
    attributes = models.JSONField(default=dict, blank=True)
    guide_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.config_name}"


class ProductConfigDimension(models.Model):
    """配置维度（动态选择器数据源）"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='config_dimensions')
    dimension_key = models.CharField(max_length=100, help_text='维度键，如 frame_color_back')
    dimension_label = models.CharField(max_length=100, help_text='展示名，如 框架颜色（背框）')
    options = models.JSONField(default=list, help_text='[{"key":"P1","label":"P1"}, ...]')
    parent_dimension = models.CharField(max_length=100, blank=True, default='',
                                        help_text='级联父维度 key（可空）')
    is_required = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'dimension_key')
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} - {self.dimension_label}"


class ProductPriceMatrix(models.Model):
    """模式 A：配置-价格映射表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_matrix')
    config_signature = models.CharField(max_length=255, help_text='配置组合稳定哈希（按 key 排序后 hash）')
    config_attributes = models.JSONField(default=dict, help_text='{"frame_color_back":"P1", ...}')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'config_signature')
        indexes = [
            models.Index(fields=['product', 'config_signature']),
        ]

    @staticmethod
    def build_signature(selections: dict) -> str:
        """按 key 排序后生成稳定哈希"""
        sorted_items = sorted(selections.items())
        raw = json.dumps(sorted_items, ensure_ascii=False, separators=(',', ':'))
        return hashlib.md5(raw.encode()).hexdigest()

    def __str__(self):
        return f"{self.product.name} - {self.config_signature[:16]}"


class ProductPriceRule(models.Model):
    """模式 B：基准价 + 加价规则"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_rules')
    dimension_key = models.CharField(max_length=100)
    option_key = models.CharField(max_length=100)
    price_delta = models.DecimalField(max_digits=10, decimal_places=2, help_text='正负皆可')
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'dimension_key', 'option_key')
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} - {self.dimension_key}:{self.option_key} ({self.price_delta:+})"


class ProductDocument(models.Model):
    """产品-文档关联"""
    RELATION_TYPE_CHOICES = [
        ('DESIGN', '设计资源'),
        ('TRAINING', '培训资料'),
        ('CERTIFICATE', '资质文件'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_documents')
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, related_name='product_links')
    relation_type = models.CharField(max_length=15, choices=RELATION_TYPE_CHOICES)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'document')
        ordering = ['relation_type', 'sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} - {self.document.name} ({self.relation_type})"
