import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, Form, Image, Input, message, Space, Table, Typography } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { shareService } from '../../services/shareService';

const { Title, Text, Paragraph } = Typography;

export default function ShareViewPage() {
  const { token } = useParams();
  const [content, setContent] = useState<any>(null);
  const [needsPassword, setNeedsPassword] = useState(false);
  const [shareTitle, setShareTitle] = useState('');
  const [branding, setBranding] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    shareService.getSharedContent(token).then(({ data }) => {
      if (data.requires_password) {
        setNeedsPassword(true);
        setShareTitle(data.title);
      } else {
        setContent(data);
        setBranding(data.branding);
      }
    }).catch((err) => setError(err.response?.data?.detail || '链接无效'));
  }, [token]);

  const handleVerify = async (values: { password: string }) => {
    try {
      const { data } = await shareService.verifyPassword(token!, values.password);
      setContent(data);
      setBranding(data.branding);
      setNeedsPassword(false);
    } catch { message.error('密码错误'); }
  };

  if (error) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Card><Title level={4}>{error}</Title></Card>
    </div>
  );

  if (needsPassword) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#161b26' }}>
      <Card style={{ width: 400, textAlign: 'center' }}>
        <LockOutlined style={{ fontSize: 48, color: 'rgba(255,255,255,0.38)', marginBottom: 16 }} />
        <Title level={4}>{shareTitle}</Title>
        <Text type="secondary">此内容需要密码访问</Text>
        <Form onFinish={handleVerify} style={{ marginTop: 24 }}>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password placeholder="请输入访问密码" size="large" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block size="large">验证</Button>
        </Form>
      </Card>
    </div>
  );

  if (!content) return null;

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '0 20px' }}>
      {/* 品牌展示头部 */}
      {branding && (branding.company_name || branding.logo_path) && (
        <div style={{ textAlign: 'center', padding: '32px 0 16px', borderBottom: '1px solid #f0f0f0', marginBottom: 24 }}>
          {branding.logo_path && (
            <img src={`/media/${branding.logo_path}`} alt="Logo" style={{ maxHeight: 60, marginBottom: 12 }} />
          )}
          {branding.company_name && <Title level={4} style={{ margin: 0 }}>{branding.company_name}</Title>}
          {branding.contact_info && <Paragraph type="secondary" style={{ marginTop: 8, whiteSpace: 'pre-line' }}>{branding.contact_info}</Paragraph>}
        </div>
      )}

      <Title level={3} style={{ marginBottom: 24 }}>{content.title}</Title>

      {content.type === 'product' && content.data && (
        <Card>
          <Descriptions column={2}>
            <Descriptions.Item label="名称">{content.data.name}</Descriptions.Item>
            <Descriptions.Item label="编号">{content.data.code || '-'}</Descriptions.Item>
            <Descriptions.Item label="品牌">{content.data.brand_name || '-'}</Descriptions.Item>
            <Descriptions.Item label="产地">{content.data.origin || '-'}</Descriptions.Item>
            <Descriptions.Item label="描述" span={2}>{content.data.description || '-'}</Descriptions.Item>
          </Descriptions>
          {content.data.images?.length > 0 && (
            <Image.PreviewGroup>
              <Space wrap style={{ marginTop: 16 }}>
                {content.data.images.map((img: any) => (
                  <Image key={img.id} width={150} height={150} style={{ objectFit: 'cover' }}
                    src={`/media/${img.thumbnail_path?.medium || img.image_path}`} />
                ))}
              </Space>
            </Image.PreviewGroup>
          )}
        </Card>
      )}

      {content.type === 'quote' && content.data && (
        <Card>
          <Descriptions column={2}>
            <Descriptions.Item label="客户">{content.data.customer_name}</Descriptions.Item>
            <Descriptions.Item label="总金额">¥{content.data.total_amount}</Descriptions.Item>
          </Descriptions>
          <Table dataSource={content.data.items} rowKey="id" pagination={false} style={{ marginTop: 16 }} columns={[
            {
              title: '图片', dataIndex: 'image_url', width: 60,
              render: (url: string) => url ? <img src={`/media/${url}`} alt="" style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 4 }} /> : '-',
            },
            { title: '产品', dataIndex: 'product_name' },
            { title: '配置', dataIndex: 'config_name' },
            { title: '单价', dataIndex: 'unit_price', render: (v: number) => `¥${v}` },
            { title: '数量', dataIndex: 'quantity' },
            { title: '小计', dataIndex: 'subtotal', render: (v: number) => `¥${v}` },
          ]} />
        </Card>
      )}

      {content.type === 'case' && content.data && (
        <Card>
          <Title level={4}>{content.data.title}</Title>
          <Text>{content.data.description}</Text>
          {content.data.images?.length > 0 && (
            <Image.PreviewGroup>
              <Space wrap style={{ marginTop: 16 }}>
                {content.data.images.map((img: any) => (
                  <Image key={img.id} width={150} height={150} style={{ objectFit: 'cover' }}
                    src={`/media/${img.thumbnail_path?.medium || img.image_path}`} loading="lazy" />
                ))}
              </Space>
            </Image.PreviewGroup>
          )}
        </Card>
      )}

      {/* 批量分享（案例集合） */}
      {content.type === 'batch_cases' && Array.isArray(content.data) && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {content.data.map((c: any) => (
            <Card key={c.id} title={c.title}>
              <Text>{c.description}</Text>
              {c.images?.length > 0 && (
                <Image.PreviewGroup>
                  <Space wrap style={{ marginTop: 12 }}>
                    {c.images.slice(0, 6).map((img: any) => (
                      <Image key={img.id} width={120} height={90} style={{ objectFit: 'cover' }}
                        src={`/media/${img.thumbnail_path?.medium || img.image_path}`} loading="lazy" />
                    ))}
                  </Space>
                </Image.PreviewGroup>
              )}
            </Card>
          ))}
        </Space>
      )}

      {content.type === 'catalog' && content.data && (
        <Space wrap>
          {content.data.map((p: any) => (
            <Card key={p.id} style={{ width: 200 }}
              cover={p.cover_image && <img alt={p.name} src={`/media/${p.cover_image.thumbnail_path?.medium || p.cover_image.image_path}`} style={{ height: 120, objectFit: 'cover' }} />}>
              <Card.Meta title={p.name} description={p.code} />
            </Card>
          ))}
        </Space>
      )}
    </div>
  );
}
