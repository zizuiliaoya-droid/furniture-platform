import { useEffect, useState } from 'react';
import { Card, Col, Input, Row, Space, Tree, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { productService } from '../../services/productService';
import api from '../../services/api';

const { Title, Text } = Typography;
const { Meta } = Card;

export default function CatalogPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [treeData, setTreeData] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchProducts = async (params?: any) => {
    const { data } = await api.get('/api/catalog/', { params });
    setProducts(data.results || data);
  };

  useEffect(() => {
    fetchProducts();
    productService.getCategoryTree('TYPE').then(({ data }) => {
      setTreeData(data.map((n: any) => ({ key: n.id, title: n.name, children: (n.children || []).map((c: any) => ({ key: c.id, title: c.name })) })));
    });
  }, []);

  return (
    <Row gutter={16}>
      <Col span={5}>
        <Card title="分类导航" size="small">
          <Tree treeData={treeData} onSelect={(keys) => fetchProducts(keys[0] ? { category: keys[0] } : {})} />
        </Card>
      </Col>
      <Col span={19}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input.Search placeholder="搜索产品..." allowClear onSearch={(v) => fetchProducts({ q: v })} />
          <Row gutter={[16, 16]}>
            {products.map((p: any) => (
              <Col xs={12} sm={8} md={6} key={p.id}>
                <Card hoverable onClick={() => navigate(`/products/${p.id}`)}
                  cover={p.cover_image ? <img alt={p.name} src={`/media/${p.cover_image.thumbnail_path?.medium || p.cover_image.image_path}`} style={{ height: 160, objectFit: 'cover' }} /> : <div style={{ height: 160, background: '#252b3b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Text type="secondary">暂无图片</Text></div>}>
                  <Meta title={p.name} description={p.code || ''} />
                </Card>
              </Col>
            ))}
          </Row>
        </Space>
      </Col>
    </Row>
  );
}
