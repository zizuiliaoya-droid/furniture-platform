"""
测试数据初始化命令（幂等，可重复执行）。

用法:
    python manage.py seed_demo

参考 产品库字段描述.xlsx（椅子类 11 个配置维度 + 双模式价格 + 级联）
与 产品管理系统调整问题.xlsx（8 大办公空间案例行业）构造真实感数据。
"""
from decimal import Decimal
from itertools import product as iproduct

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import (
    Brand, Product, ProductConfigDimension,
    ProductPriceMatrix, ProductPriceRule,
)
from cases.models import Case
from documents.models import Document, DocumentFolder
from quotes.models import Quote, QuoteItem
from quotes.services import QuoteService

User = get_user_model()


class Command(BaseCommand):
    help = '初始化测试演示数据（幂等）'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='先清空演示数据（产品/品牌/案例/文档/报价）再重灌')

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get('flush'):
            self._flush()
        admin = self._ensure_admin()
        brands = self._seed_brands()
        self._seed_branding()
        self._seed_matrix_chair(admin, brands)
        self._seed_rule_chair(admin, brands)
        self._seed_simple_products(admin, brands)
        self._seed_cases(admin)
        self._seed_documents(admin)
        self._seed_quotes(admin)
        self.stdout.write(self.style.SUCCESS('[OK] 测试数据初始化完成'))

    def _flush(self):
        """清库重灌：删除演示相关数据（保留用户账号）"""
        from products.models import ProductImage
        QuoteItem.objects.all().delete()
        Quote.objects.all().delete()
        ProductPriceMatrix.objects.all().delete()
        ProductPriceRule.objects.all().delete()
        ProductConfigDimension.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Case.objects.all().delete()
        Document.objects.all().delete()
        Brand.objects.all().delete()
        self.stdout.write('  已清空演示数据（产品/配置/价格/案例/文档/报价/品牌）')

    # ── 用户 ──────────────────────────────────────────────────────────────
    def _ensure_admin(self):
        admin = User.objects.filter(role='ADMIN').order_by('id').first()
        if not admin:
            admin = User.objects.create_superuser(
                username='admin', password='admin123456',
                role='ADMIN', display_name='系统管理员',
            )
            self.stdout.write('  创建管理员 admin')
        # 一个普通员工，方便测试权限
        if not User.objects.filter(username='staff').exists():
            User.objects.create_user(
                username='staff', password='staff123456',
                role='STAFF', display_name='测试员工',
            )
            self.stdout.write('  创建员工 staff')
        return admin

    # ── 品牌 ──────────────────────────────────────────────────────────────
    def _seed_brands(self):
        data = [
            ('ZIKOO', True, 1),
            ('Steelcase', False, 2),
            ('Vitra', False, 3),
            ('Herman Miller', False, 4),
            ('Haworth', False, 5),
        ]
        brands = {}
        for name, self_owned, order in data:
            b, _ = Brand.objects.get_or_create(
                name=name, defaults={'is_self_owned': self_owned, 'sort_order': order})
            brands[name] = b
        self.stdout.write(f'  品牌 {len(brands)} 个')
        return brands

    def _seed_branding(self):
        from sharing.models import BrandingConfig
        if not BrandingConfig.objects.exists():
            BrandingConfig.objects.create(
                company_name='智凯家具软装',
                contact_info='电话：021-8888-8888\n邮箱：sales@zikoo.example\n地址：上海市 · 家具产业园',
            )
            self.stdout.write('  品牌展示配置 1 条')

    # ── MATRIX 模式椅子（配置-价格映射表，枚举全组合） ──────────────────────
    def _seed_matrix_chair(self, admin, brands):
        p, created = Product.objects.get_or_create(
            code='ZK-CHAIR-M01',
            defaults=dict(
                name='ZIKOO 人体工学办公椅 (Matrix)',
                description='款式：高背人体工学；映射表定价模式。可选框架色 / 坐垫材质 / 扶手。',
                category_l1='SEATING', category_l2='OFFICE_CHAIR',
                brand=brands['ZIKOO'], origin='DOMESTIC', lead_time='WITHIN_45D',
                pricing_mode='MATRIX',
                length_mm=680, width_mm=680, height_mm=1180,
                official_url='https://example.com/zk-chair-m01',
                created_by=admin, is_active=True,
            ),
        )
        if not created:
            return
        dims = [
            ('frame_color_back', '框架颜色（背框）', ['P1', 'P2', 'P3'], '', True, 1),
            ('cushion_material', '坐垫材质', ['网', '布', '皮'], '', True, 2),
            ('armrest', '扶手', ['2D', '3D', '4D'], '', True, 3),
        ]
        for key, label, opts, parent, req, order in dims:
            ProductConfigDimension.objects.create(
                product=p, dimension_key=key, dimension_label=label,
                options=[{'key': o, 'label': o} for o in opts],
                parent_dimension=parent, is_required=req, sort_order=order,
            )
        # 枚举全部 3×3×3=27 组合，按规则生成价格
        frame_add = {'P1': 0, 'P2': 100, 'P3': 200}
        cushion_add = {'网': 0, '布': 150, '皮': 600}
        armrest_add = {'2D': 0, '3D': 180, '4D': 360}
        base = Decimal('1680')
        prices = []
        for fc, cm, ar in iproduct(['P1', 'P2', 'P3'], ['网', '布', '皮'], ['2D', '3D', '4D']):
            config = {'frame_color_back': fc, 'cushion_material': cm, 'armrest': ar}
            price = base + frame_add[fc] + cushion_add[cm] + armrest_add[ar]
            ProductPriceMatrix.objects.create(
                product=p,
                config_signature=ProductPriceMatrix.build_signature(config),
                config_attributes=config, price=price,
            )
            prices.append(price)
        p.min_price = min(prices)
        p.save(update_fields=['min_price'])
        self.stdout.write('  MATRIX 椅子 + 27 条价格映射')

    # ── RULE 模式椅子（基准价 + 加价规则 + 级联维度） ───────────────────────
    def _seed_rule_chair(self, admin, brands):
        p, created = Product.objects.get_or_create(
            code='ZK-CHAIR-R01',
            defaults=dict(
                name='Steelcase 高管椅 (Rule)',
                description='款式：高管大班椅；基准价 + 加价规则定价。靠背材质支持级联系列。',
                category_l1='SEATING', category_l2='OFFICE_CHAIR',
                brand=brands['Steelcase'], origin='IMPORT', lead_time='4_6M_EU',
                pricing_mode='RULE', base_price=Decimal('2800'),
                length_mm=720, width_mm=720, height_mm=1250,
                official_url='https://example.com/sc-chair-r01',
                created_by=admin, is_active=True,
            ),
        )
        if not created:
            return
        # 靠背材质 + 级联系列 + 扶手 + 底座
        ProductConfigDimension.objects.create(
            product=p, dimension_key='backrest_material', dimension_label='靠背材质',
            options=[{'key': '网', 'label': '网'}, {'key': '布', 'label': '布'}, {'key': '皮', 'label': '皮'}],
            is_required=True, sort_order=1,
        )
        ProductConfigDimension.objects.create(
            product=p, dimension_key='backrest_series', dimension_label='靠背材质系列',
            options=[{'key': 'AIR', 'label': 'AIR'}, {'key': '3D knit', 'label': '3D knit'},
                     {'key': 'intermix', 'label': 'intermix'}],
            parent_dimension='backrest_material=网', is_required=False, sort_order=2,
        )
        ProductConfigDimension.objects.create(
            product=p, dimension_key='armrest', dimension_label='扶手',
            options=[{'key': '2D', 'label': '2D'}, {'key': '3D', 'label': '3D'}, {'key': '4D', 'label': '4D'}],
            is_required=True, sort_order=3,
        )
        ProductConfigDimension.objects.create(
            product=p, dimension_key='base', dimension_label='底座',
            options=[{'key': '标准', 'label': '标准'}, {'key': '高配', 'label': '高配'}, {'key': '低配', 'label': '低配'}],
            is_required=True, sort_order=4,
        )
        rules = [
            ('backrest_material', '网', 0), ('backrest_material', '布', 300), ('backrest_material', '皮', 900),
            ('backrest_series', 'AIR', 0), ('backrest_series', '3D knit', 200), ('backrest_series', 'intermix', 400),
            ('armrest', '2D', 0), ('armrest', '3D', 150), ('armrest', '4D', 300),
            ('base', '标准', 0), ('base', '高配', 500), ('base', '低配', -200),
        ]
        for i, (dk, ok, delta) in enumerate(rules):
            ProductPriceRule.objects.create(
                product=p, dimension_key=dk, option_key=ok,
                price_delta=Decimal(str(delta)), sort_order=i,
            )
        p.min_price = Decimal('2600')  # 基准 2800 + 最低 base 低配 -200
        p.save(update_fields=['min_price'])
        self.stdout.write('  RULE 椅子 + 12 条加价规则（含级联）')

    # ── 其它品类简单产品（无配置维度，用 min_price 展示） ──────────────────
    def _seed_simple_products(self, admin, brands):
        items = [
            ('ZK-DESK-01', '升降办公桌', 'DESKS_WORKSTATIONS', 'HEIGHT_ADJUSTABLE_DESK',
             'Vitra', 'IMPORT', '2_4M_VIETNAM', 3200, 1400, 700, 1200),
            ('ZK-DESK-02', '屏风工位 4 人位', 'DESKS_WORKSTATIONS', 'BENCHING',
             'ZIKOO', 'DOMESTIC', 'WITHIN_45D', 5800, 2800, 2800, 1100),
            ('ZK-TABLE-01', '会议桌 3.6m', 'TABLE', 'CONFERENCE_TABLE',
             'Haworth', 'IMPORT', '2_4M_MALAYSIA', 8800, 3600, 1200, 750),
            ('ZK-STORAGE-01', '钢制文件柜', 'STORAGE', 'CABINET_CREDENZA',
             'ZIKOO', 'DOMESTIC', 'WITHIN_45D', 1200, 900, 450, 1800),
            ('ZK-ACC-01', '显示器支架', 'ACCESSORIES', 'MONITOR_ARM',
             'Herman Miller', 'IMPORT', '4_6M_EU', 980, 0, 0, 0),
            ('ZK-EDU-01', '教室课桌椅', 'EDUCATION', 'EDU_DESK',
             'ZIKOO', 'DOMESTIC', 'WITHIN_45D', 680, 600, 450, 760),
        ]
        n = 0
        for code, name, l1, l2, brand, origin, lead, price, L, W, H in items:
            _, created = Product.objects.get_or_create(
                code=code,
                defaults=dict(
                    name=name, description=f'{name} — 测试数据',
                    category_l1=l1, category_l2=l2, brand=brands[brand],
                    origin=origin, lead_time=lead, pricing_mode='MATRIX',
                    min_price=Decimal(str(price)),
                    length_mm=L or None, width_mm=W or None, height_mm=H or None,
                    created_by=admin, is_active=True,
                ),
            )
            n += 1 if created else 0
        self.stdout.write(f'  其它品类产品 {n} 个')

    # ── 客户案例（8 大办公空间行业） ────────────────────────────────────────
    def _seed_cases(self, admin):
        cases = [
            ('某科技公司总部开放办公区改造', 'TECH_OFFICE'),
            ('某券商交易大厅工位升级', 'FINANCE_OFFICE'),
            ('某建筑设计院协作空间', 'REALESTATE_OFFICE'),
            ('某高校智慧教室项目', 'EDUCATION_OFFICE'),
            ('某三甲医院行政办公区', 'MEDICAL_OFFICE'),
            ('某 4A 广告公司创意办公室', 'MEDIA_OFFICE'),
        ]
        n = 0
        for title, industry in cases:
            _, created = Case.objects.get_or_create(
                title=title,
                defaults=dict(industry=industry,
                              description=f'{title}（演示案例）', created_by=admin),
            )
            n += 1 if created else 0
        self.stdout.write(f'  客户案例 {n} 个')

    # ── 内部文档 ────────────────────────────────────────────────────────────
    def _seed_documents(self, admin):
        folder, _ = DocumentFolder.objects.get_or_create(
            name='产品手册', doc_type='DESIGN', defaults={'sort_order': 1})
        if not Document.objects.filter(name='ZIKOO 培训资料 - 入门指南').exists():
            Document.objects.create(
                name='ZIKOO 培训资料 - 入门指南', doc_type='TRAINING',
                resource_type='RICH_TEXT', mime_type='text/html',
                content='<h2>ZIKOO 产品入门</h2><p>这是一段<strong>富文本</strong>培训资料示例。</p>'
                        '<ul><li>人体工学椅调节</li><li>升降桌使用</li></ul>',
                tags=['入门', '培训'], created_by=admin,
            )
            self.stdout.write('  富文本培训资料 1 条')

    # ── 报价单（演示一键加入链路结果） ──────────────────────────────────────
    def _seed_quotes(self, admin):
        if Quote.objects.filter(title='演示报价单 - 科技公司').exists():
            return
        q = Quote.objects.create(
            title='演示报价单 - 科技公司', customer_name='某科技公司',
            status='DRAFT', notes='测试演示用', created_by=admin,
        )
        matrix_chair = Product.objects.filter(code='ZK-CHAIR-M01').first()
        if matrix_chair:
            try:
                QuoteService.add_item_from_product(
                    quote=q, product=matrix_chair,
                    selections={'frame_color_back': 'P2', 'cushion_material': '皮', 'armrest': '4D'},
                    quantity=10, discount=Decimal('5'),
                )
            except Exception as e:
                self.stdout.write(f'  (报价明细跳过: {e})')
        desk = Product.objects.filter(code='ZK-DESK-01').first()
        if desk:
            QuoteItem.objects.create(
                quote=q, product=desk, product_name=desk.name,
                config_name='标准', unit_price=desk.min_price or Decimal('3200'),
                quantity=10, discount=Decimal('0'), sort_order=1,
            )
            q.recalculate_total()
        self.stdout.write('  演示报价单 1 个')
