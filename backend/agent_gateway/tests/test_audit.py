"""Agent 审计日志安全测试。"""
from agent_gateway.services import sanitize_for_audit


def test_sensitive_values_are_redacted_recursively():
    payload = {
        'query': '人体工学椅',
        'password': 'customer-password',
        'nested': {
            'api_token': 'top-secret-token',
            'Authorization': 'Token abc',
            'normal': 'visible',
        },
        'items': [{'client_secret': 'secret'}, {'id': 2}],
    }

    sanitized = sanitize_for_audit(payload)

    assert sanitized['query'] == '人体工学椅'
    assert sanitized['password'] == '[REDACTED]'
    assert sanitized['nested']['api_token'] == '[REDACTED]'
    assert sanitized['nested']['Authorization'] == '[REDACTED]'
    assert sanitized['nested']['normal'] == 'visible'
    assert sanitized['items'][0]['client_secret'] == '[REDACTED]'


def test_large_values_are_bounded():
    sanitized = sanitize_for_audit({'notes': 'x' * 5000})

    assert len(sanitized['notes']) <= 1001
    assert sanitized['notes'].endswith('…')
