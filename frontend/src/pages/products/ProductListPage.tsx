import { useEffect } from 'react';
import { Button, Input, Select, Space, Table, Tag, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useProductStore } from '../../store/productStore';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;

export default function ProductListPage() {
  const navigate = useNavigate();
  const { products, total, loading, page, pageSize, fetchProducts, setFilters, setPage } = useProductStore();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  useEffect(() => { fetchProducts(); }, []);

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>产品管理</Title>
        {isAdmin && <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/products/new')}>新建产品</Button>}
      </Space>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search placeholder="搜索产品..." allowClear onSearch={(v) => setFilters({ search: v })} style={{ width: 250 }} />
        <Select placeholder="产地" allowClear style={{ width: 120 }} onChange={(v) => setFilters({ origin: v })}
          options={[{ value: 'IMPORT', label: '进口' }, { value: 'DOMESTIC', label: '国产' }, { value: 'CUSTOM', label: '定制' }]} />
      </Space>
      <Table dataSource={products} rowKey="id" loading={loading}
        pagination={{ current: page, pageSize, total, onChange: setPage }}
        onRow={(r) => ({ onClick: () => navigate(`/products/${r.id}`), style: { cursor: 'pointer' } })}
        columns={[
          { title: '名称', dataIndex: 'name' },
          { title: '编号', dataIndex: 'code' },
          { title: '产地', dataIndex: 'origin', render: (v: string) => ({ IMPORT: '进口', DOMESTIC: '国产', CUSTOM: '定制' }[v]) },
          { title: '最低售价', dataIndex: 'min_price', render: (v: number) => v ? `¥${v}` : '-' },
          { title: '状态', dataIndex: 'is_active', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '上架' : '下架'}</Tag> },
        ]} />
    </div>
  );
}
