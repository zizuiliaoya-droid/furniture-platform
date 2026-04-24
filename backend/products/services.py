"""Product management services."""
import openpyxl
from django.conf import settings
from django.db import transaction

from common.file_storage import FileStorageService
from .models import Category, Product, ProductImage


class CategoryService:
    @staticmethod
    def get_tree(dimension: str):
        return Category.objects.filter(
            dimension=dimension, parent__isnull=True
        ).order_by('sort_order', 'id')

    @staticmethod
    def reorder(items: list):
        for item in items:
            Category.objects.filter(pk=item['id']).update(sort_order=item['sort_order'])


class ProductImageService:
    @staticmethod
    def upload_images(product: Product, files: list) -> list:
        created = []
        for f in files:
            if f.size > settings.MAX_IMAGE_SIZE:
                continue
            path = FileStorageService.upload(f, 'products')
            thumbs = FileStorageService.generate_thumbnails(path)
            img = ProductImage.objects.create(
                product=product,
                image_path=path,
                thumbnail_path=thumbs,
                sort_order=product.images.count(),
            )
            created.append(img)
        return created

    @staticmethod
    def delete_image(image: ProductImage):
        FileStorageService.delete_with_thumbnails(image.image_path)
        image.delete()

    @staticmethod
    def set_cover(image: ProductImage):
        ProductImage.objects.filter(product=image.product, is_cover=True).update(is_cover=False)
        image.is_cover = True
        image.save(update_fields=['is_cover'])


class ProductImportService:
    REQUIRED_HEADERS = ['名称', '产地']
    ORIGIN_MAP = {'进口': 'IMPORT', '国产': 'DOMESTIC', '定制': 'CUSTOM'}

    @staticmethod
    def parse_excel(file) -> dict:
        wb = openpyxl.load_workbook(file, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=1, values_only=True))
        if not rows:
            return {'success_count': 0, 'failed_count': 0, 'preview': []}
        headers = [str(h).strip() if h else '' for h in rows[0]]
        results = []
        seen_codes = set()
        for i, row in enumerate(rows[1:], start=2):
            data = dict(zip(headers, row))
            errors = []
            name = str(data.get('名称', '') or '').strip()
            if not name:
                errors.append('名称为必填项')
            origin_raw = str(data.get('产地', '') or '').strip()
            origin = ProductImportService.ORIGIN_MAP.get(origin_raw)
            if not origin:
                errors.append(f'产地无效: {origin_raw}')
            code = str(data.get('编号', '') or '').strip() or None
            if code:
                if code in seen_codes or Product.objects.filter(code=code).exists():
                    errors.append(f'编号重复: {code}')
                seen_codes.add(code)
            category_name = str(data.get('分类', '') or '').strip()
            category = None
            if category_name:
                category = Category.objects.filter(name=category_name).first()
                if not category:
                    errors.append(f'分类不存在: {category_name}')
            results.append({
                'row': i, 'name': name, 'code': code, 'origin': origin,
                'description': str(data.get('描述', '') or ''),
                'min_price': data.get('最低售价'),
                'category': category, 'errors': errors,
            })
        success = [r for r in results if not r['errors']]
        failed = [r for r in results if r['errors']]
        return {'success_count': len(success), 'failed_count': len(failed), 'preview': results, 'parsed_data': success}

    @staticmethod
    @transaction.atomic
    def execute_import(parsed_data: list, user) -> int:
        count = 0
        for item in parsed_data:
            Product.objects.create(
                name=item['name'], code=item['code'], origin=item['origin'],
                description=item['description'],
                min_price=item['min_price'] if item['min_price'] else None,
                category=item['category'] or Category.objects.first(),
                created_by=user,
            )
            count += 1
        return count

    @staticmethod
    def generate_template():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '产品导入模板'
        ws.append(['名称', '编号', '产地', '描述', '最低售价', '分类'])
        ws.append(['示例产品', 'P001', '进口', '产品描述', 1000, '办公椅'])
        from io import BytesIO
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()
