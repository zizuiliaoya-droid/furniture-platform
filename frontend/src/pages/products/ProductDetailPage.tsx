import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, Image, Space, Table, Tag, Typography, message } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { productService } from '../../services/productService';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;

export default function ProductDetailPage() {
  const { id } = useParams();
  const [product, setProduct] = useState<any>(null);
  const navigate = useNavigate();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  useEffect(() => {
    if (id) productService.getProduct(Number(id)).then(({ data }) => setProduct(data));
  }, [id]);

  if (!product) return null;

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>{product.name}</Title>
        {isAdmin && <Button icon={<EditOutlined />} onClick={() => navigate(`/products/${id}/edit`)}>编辑</Button>}
      </Space>
      <Card>
        <Descriptions column={2}>
          <Descriptions.Item label="编号">{product.code || '-'}</Descriptions.Item>
          <Descriptions.Item label="产地">{{ IMPORT: '进口', DOMESTIC: '国产', CUSTOM: '定制' }[product.origin as string]}</Descriptions.Item>
          <Descriptions.Item label="最低售价">{product.min_price ? `¥${product.min_price}` : '-'}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={product.is_active ? 'green' : 'default'}>{product.is_active ? '上架' : '下架'}</Tag></Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>{product.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>
      {product.images?.length > 0 && (
        <Card title="产品图片" style={{ marginTop: 16 }}>
          <Image.PreviewGroup>
            <Space wrap>{product.images.map((img: any) => (
              <Image key={img.id} width={120} height={120} style={{ objectFit: 'cover', borderRadius: 4 }}
                src={`/media/${img.thumbnail_path?.medium || img.image_path}`} />
            ))}</Space>
          </Image.PreviewGroup>
        </Card>
      )}
      {product.configs?.length > 0 && (
        <Card title="产品配置" style={{ marginTop: 16 }}>
          <Table dataSource={product.configs} rowKey="id" pagination={false} size="small" columns={[
            { title: '配置名称', dataIndex: 'config_name' },
            { title: '指导价格', dataIndex: 'guide_price', render: (v: number) => v ? `¥${v}` : '-' },
            { title: '属性', dataIndex: 'attributes', render: (v: any) => JSON.stringify(v) },
          ]} />
        </Card>
      )}
    </div>
  );
}
