"""QwenPaw 家具 API 客户端契约测试。"""
from io import BytesIO
import importlib.util
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest


SCRIPT = Path(__file__).parents[1] / 'skills' / 'furniture-system' / 'scripts' / 'furniture_api.py'
SPEC = importlib.util.spec_from_file_location('furniture_api', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload, headers=None):
        self.payload = payload
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self.payload, ensure_ascii=False).encode('utf-8')


def test_public_base_url_requires_https():
    with pytest.raises(MODULE.FurnitureClientError, match='HTTPS'):
        MODULE.FurnitureAPIClient(base_url='http://example.com', token='secret')


def test_search_encodes_query_and_sends_audit_headers():
    captured = {}

    def opener(request, timeout):
        captured['request'] = request
        captured['timeout'] = timeout
        return FakeResponse({'count': 0, 'items': []}, {'X-Request-ID': 'server-request'})

    client = MODULE.FurnitureAPIClient(
        base_url='https://furniture.example.com',
        token='api-secret',
        skill='furniture-catalog',
        timeout=12,
        opener=opener,
    )

    result = client.search_products(q='人体工学 椅', page_size=5)

    request = captured['request']
    assert 'q=%E4%BA%BA%E4%BD%93%E5%B7%A5%E5%AD%A6+%E6%A4%85' in request.full_url
    assert request.get_header('Authorization') == 'Token api-secret'
    assert request.get_header('X-agent-skill') == 'furniture-catalog'
    assert captured['timeout'] == 12
    assert result['request_id'] == 'server-request'


def test_http_error_never_echoes_api_token():
    def opener(request, timeout):
        raise HTTPError(
            request.full_url,
            500,
            'Server Error',
            {'X-Request-ID': 'failed-request'},
            BytesIO(b'{"detail":"failure api-secret"}'),
        )

    client = MODULE.FurnitureAPIClient(
        base_url='https://furniture.example.com',
        token='api-secret',
        opener=opener,
    )

    with pytest.raises(MODULE.FurnitureClientError) as error:
        client.capabilities()

    assert 'api-secret' not in error.value.detail
    assert '[REDACTED]' in error.value.detail
    assert error.value.request_id == 'failed-request'


def test_import_uses_multipart_and_preserves_confirmation_field(tmp_path):
    workbook = tmp_path / 'config.xlsx'
    workbook.write_bytes(b'fake-xlsx')
    captured = {}

    def opener(request, timeout):
        captured['request'] = request
        return FakeResponse({'detail': 'ok'})

    client = MODULE.FurnitureAPIClient(
        base_url='http://127.0.0.1:8000',
        token='local-token',
        skill='furniture-import',
        opener=opener,
    )

    client.confirm_import(
        7,
        str(workbook),
        mapping='{}',
        confirmation_token='one-time-ticket',
        replace_dimensions='false',
        replace_prices='true',
    )

    request = captured['request']
    assert request.full_url.endswith('/api/agent/products/7/config-import/confirm/')
    assert request.get_header('Content-type').startswith('multipart/form-data; boundary=')
    assert b'one-time-ticket' in request.data
    assert b'fake-xlsx' in request.data


def test_parse_json_requires_object():
    with pytest.raises(MODULE.FurnitureClientError, match='JSON 对象'):
        MODULE.parse_json_object('[1, 2]', 'selections')
