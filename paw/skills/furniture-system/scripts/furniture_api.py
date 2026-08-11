#!/usr/bin/env python3
"""Dependency-free CLI for QwenPaw furniture platform Skills."""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4


class FurnitureClientError(RuntimeError):
    def __init__(self, detail: str, *, status: int | None = None, request_id: str = ''):
        super().__init__(detail)
        self.detail = detail
        self.status = status
        self.request_id = request_id


def parse_json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FurnitureClientError(f'{label} 不是有效 JSON：{exc.msg}') from exc
    if not isinstance(value, dict):
        raise FurnitureClientError(f'{label} 必须是 JSON 对象')
    return value


def _multipart_body(fields: dict[str, Any], file_path: Path) -> tuple[bytes, str]:
    boundary = f'----furniture-agent-{uuid4().hex}'
    parts: list[bytes] = []
    for key, value in fields.items():
        if value is None:
            continue
        parts.extend([
            f'--{boundary}\r\n'.encode(),
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode(),
            str(value).encode('utf-8'),
            b'\r\n',
        ])
    content_type = mimetypes.guess_type(file_path.name)[0] or 'application/octet-stream'
    parts.extend([
        f'--{boundary}\r\n'.encode(),
        (
            'Content-Disposition: form-data; name="file"; '
            f'filename="{file_path.name}"\r\n'
        ).encode('utf-8'),
        f'Content-Type: {content_type}\r\n\r\n'.encode(),
        file_path.read_bytes(),
        b'\r\n',
        f'--{boundary}--\r\n'.encode(),
    ])
    return b''.join(parts), f'multipart/form-data; boundary={boundary}'


class FurnitureAPIClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        token: str | None = None,
        skill: str = 'furniture-system',
        timeout: float | None = None,
        opener=None,
    ):
        self.base_url = (base_url or os.getenv('FURNITURE_API_URL', '')).strip().rstrip('/')
        self.token = (token or os.getenv('FURNITURE_API_TOKEN', '')).strip()
        self.skill = skill.strip() or 'furniture-system'
        try:
            self.timeout = float(timeout or os.getenv('FURNITURE_API_TIMEOUT', '30'))
        except ValueError as exc:
            raise FurnitureClientError('FURNITURE_API_TIMEOUT 必须是数字') from exc
        self.opener = opener or urlopen
        self._validate_config()

    def _validate_config(self):
        if not self.base_url:
            raise FurnitureClientError('缺少 FURNITURE_API_URL')
        parsed = urlparse(self.base_url)
        local_hosts = {'localhost', '127.0.0.1', '::1'}
        if parsed.scheme != 'https' and not (
            parsed.scheme == 'http' and parsed.hostname in local_hosts
        ):
            raise FurnitureClientError('公网 FURNITURE_API_URL 必须使用 HTTPS')
        if not self.token:
            raise FurnitureClientError('缺少 FURNITURE_API_TOKEN')

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        fields: dict[str, Any] | None = None,
        file_path: str | Path | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if not path.startswith('/'):
            raise FurnitureClientError('API path 必须以 / 开头')
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        if query:
            cleaned = {key: value for key, value in query.items() if value not in (None, '')}
            if cleaned:
                url += '?' + urlencode(cleaned, doseq=True)
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Token {self.token}',
            'User-Agent': 'QwenPaw-Furniture-Skills/1.0',
            'X-Agent-Skill': self.skill,
            'X-Request-ID': str(uuid4()),
        }
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            headers['Content-Type'] = 'application/json; charset=utf-8'
        elif file_path is not None:
            path_obj = Path(file_path).expanduser().resolve()
            if not path_obj.is_file():
                raise FurnitureClientError(f'文件不存在：{path_obj}')
            body, content_type = _multipart_body(fields or {}, path_obj)
            headers['Content-Type'] = content_type
        if extra_headers:
            headers.update(extra_headers)
        request = Request(url, data=body, headers=headers, method=method.upper())
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read()
                response_request_id = response.headers.get('X-Request-ID', '')
        except HTTPError as exc:
            raw = exc.read()
            response_request_id = exc.headers.get('X-Request-ID', '') if exc.headers else ''
            detail = self._error_detail(raw, exc.reason)
            raise FurnitureClientError(
                detail,
                status=exc.code,
                request_id=response_request_id,
            ) from exc
        except URLError as exc:
            detail = str(exc.reason).replace(self.token, '[REDACTED]')
            raise FurnitureClientError(f'无法连接家具平台：{detail}') from exc
        if not raw:
            return {'request_id': response_request_id}
        try:
            data = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FurnitureClientError(
                '平台返回了非 JSON 响应',
                request_id=response_request_id,
            ) from exc
        if isinstance(data, dict) and response_request_id and not data.get('request_id'):
            data['request_id'] = response_request_id
        return data

    def _error_detail(self, raw: bytes, fallback: Any) -> str:
        try:
            data = json.loads(raw.decode('utf-8'))
            detail = data.get('detail') or data.get('errors') or data
            text = json.dumps(detail, ensure_ascii=False) if not isinstance(detail, str) else detail
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            text = str(fallback or '请求失败')
        return text.replace(self.token, '[REDACTED]')[:2000]

    def capabilities(self):
        return self.request('GET', '/api/agent/capabilities/')

    def search_products(self, **query):
        return self.request('GET', '/api/agent/products/search/', query=query)

    def product_detail(self, product_id: int):
        return self.request('GET', f'/api/agent/products/{product_id}/')

    def calculate_price(self, product_id: int, selections: dict[str, Any]):
        return self.request(
            'POST',
            f'/api/agent/products/{product_id}/price/',
            payload={'selections': selections},
        )

    def search_documents(self, **query):
        return self.request('GET', '/api/agent/documents/search/', query=query)

    def search_cases(self, **query):
        return self.request('GET', '/api/agent/cases/search/', query=query)

    def create_quote(self, payload: dict[str, Any], idempotency_key: str):
        return self.request(
            'POST',
            '/api/agent/quotes/drafts/',
            payload=payload,
            extra_headers={'Idempotency-Key': idempotency_key},
        )

    def preview_import(self, product_id: int, file_path: str, **fields):
        return self.request(
            'POST',
            f'/api/agent/products/{product_id}/config-import/preview/',
            fields=fields,
            file_path=file_path,
        )

    def confirm_import(self, product_id: int, file_path: str, **fields):
        return self.request(
            'POST',
            f'/api/agent/products/{product_id}/config-import/confirm/',
            fields=fields,
            file_path=file_path,
        )


def _payload_from_args(args) -> dict[str, Any]:
    if bool(args.payload) == bool(args.payload_file):
        raise FurnitureClientError('必须且只能提供 --payload 或 --payload-file')
    if args.payload_file:
        try:
            raw = Path(args.payload_file).expanduser().read_text(encoding='utf-8')
        except OSError as exc:
            raise FurnitureClientError(f'无法读取报价 JSON：{exc}') from exc
    else:
        raw = args.payload
    return parse_json_object(raw, '报价 payload')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='QwenPaw 家具平台确定性 API 客户端')
    parser.add_argument('--skill', default='furniture-system', help='发送到审计日志的 Skill 名称')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('capabilities')

    search = commands.add_parser('search-products')
    search.add_argument('--query', default='')
    search.add_argument('--category-l1')
    search.add_argument('--category-l2')
    search.add_argument('--brand', type=int)
    search.add_argument('--origin')
    search.add_argument('--lead-time')
    search.add_argument('--min-price')
    search.add_argument('--max-price')
    search.add_argument('--page', type=int, default=1)
    search.add_argument('--page-size', type=int, default=10)

    detail = commands.add_parser('product-detail')
    detail.add_argument('product_id', type=int)
    price = commands.add_parser('calculate-price')
    price.add_argument('product_id', type=int)
    price.add_argument('--selections', required=True)

    documents = commands.add_parser('search-documents')
    documents.add_argument('--query', default='')
    documents.add_argument('--doc-type')
    documents.add_argument('--limit', type=int, default=10)
    cases = commands.add_parser('search-cases')
    cases.add_argument('--query', default='')
    cases.add_argument('--industry')
    cases.add_argument('--limit', type=int, default=10)

    quote = commands.add_parser('create-quote')
    quote.add_argument('--idempotency-key', required=True)
    quote.add_argument('--payload')
    quote.add_argument('--payload-file')

    for name in ('preview-import', 'confirm-import'):
        command = commands.add_parser(name)
        command.add_argument('product_id', type=int)
        command.add_argument('file')
        command.add_argument('--mapping', default='{}')
        command.add_argument('--replace-dimensions', action='store_true')
        command.add_argument('--keep-existing-prices', action='store_true')
        if name == 'confirm-import':
            command.add_argument('--confirmation-token', required=True)
    return parser


def execute(args, client: FurnitureAPIClient):
    if args.command == 'capabilities':
        return client.capabilities()
    if args.command == 'search-products':
        return client.search_products(
            q=args.query,
            category_l1=args.category_l1,
            category_l2=args.category_l2,
            brand=args.brand,
            origin=args.origin,
            lead_time=args.lead_time,
            min_price=args.min_price,
            max_price=args.max_price,
            page=args.page,
            page_size=args.page_size,
        )
    if args.command == 'product-detail':
        return client.product_detail(args.product_id)
    if args.command == 'calculate-price':
        return client.calculate_price(
            args.product_id,
            parse_json_object(args.selections, 'selections'),
        )
    if args.command == 'search-documents':
        return client.search_documents(q=args.query, doc_type=args.doc_type, limit=args.limit)
    if args.command == 'search-cases':
        return client.search_cases(q=args.query, industry=args.industry, limit=args.limit)
    if args.command == 'create-quote':
        return client.create_quote(_payload_from_args(args), args.idempotency_key)
    fields = {
        'mapping': json.dumps(parse_json_object(args.mapping, 'mapping'), ensure_ascii=False),
        'replace_dimensions': str(args.replace_dimensions).lower(),
        'replace_prices': str(not args.keep_existing_prices).lower(),
    }
    if args.command == 'preview-import':
        return client.preview_import(args.product_id, args.file, **fields)
    fields['confirmation_token'] = args.confirmation_token
    return client.confirm_import(args.product_id, args.file, **fields)


def main(argv=None) -> int:
    try:
        args = build_parser().parse_args(argv)
        result = execute(args, FurnitureAPIClient(skill=args.skill))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except FurnitureClientError as exc:
        error = {
            'ok': False,
            'status': exc.status,
            'detail': exc.detail,
            'request_id': exc.request_id,
        }
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
