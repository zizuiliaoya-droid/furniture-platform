import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, Form, Image, Input, message, Space, Table, Typography } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { shareService } from '../../services/shareService';

const { Title, Text } = Typography;

export default function ShareViewPage() {
  const { token } = useParams();
  const [content, setContent] = useState<any>(null);
  const [needsPassword, setNeedsPassword] = useState(false);
  const [shareTitle, setShareTitle] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    shareService.getSharedContent(token).then(({ data }) => {
      if (data.requires_password) {
        setNeedsPassword(true);
        setShareTitle(data.title);
      } else {
        setContent(data);
      }
    }).catch((err) => setError(err.response?.data?.detail || '链接无效'));
  }, [token]);

  const handleVerify = async (values: { password: string }) => {
    try {
      const { data } = await shareService.verifyPassword(token!, values.password);
      setContent(data);
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
    <div style={{ maxWidth: 1000, margin: '40px auto', padding: '0 20px' }}>
      <Title level={3} style={{ marginBottom: 24 }}>{content.title}</Title>
      {content.type === 'product' && content.data && (
        <Card>
          <Descriptions column={2}>
            <Descriptions.Item label="名称">{content.data.name}</Descriptions.Item>
            <Descriptions.Item label="编号">{content.data.code || '-'}</Descriptions.Item>
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
            { title: '产品', dataIndex: 'product_name' },
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
        </Card>
      )}
      {content.type === 'catalog' && content.data && (
        <Space wrap>
          {content.data.map((p: any) => (
            <Card key={p.id} style={{ width: 200 }}>
              <Card.Meta title={p.name} description={p.code} />
            </Card>
          ))}
        </Space>
      )}
    </div>
  );
}
