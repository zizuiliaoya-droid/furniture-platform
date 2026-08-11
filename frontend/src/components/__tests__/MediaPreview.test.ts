import { describe, expect, it } from 'vitest';

import { sanitizeRichText } from '../MediaPreview';


describe('sanitizeRichText', () => {
  it('removes executable markup while preserving safe formatting', () => {
    const sanitized = sanitizeRichText(
      '<p><strong>安全内容</strong></p>' +
      '<img src=x onerror="window.__xss = true">' +
      '<script>window.__xss = true</script>',
    );

    expect(sanitized).toContain('<strong>安全内容</strong>');
    expect(sanitized).not.toContain('onerror');
    expect(sanitized).not.toContain('<script');
  });
});
