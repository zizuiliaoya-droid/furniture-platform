import { useEffect, useState } from 'react';
import { Button, Input, InputNumber, message, Popconfirm, Select, Space, Table, Tag, Typography } from 'antd';
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useProductStore } from '../../store/productStore';
import { useAuthStore } from '../../store/authStore';
import { productService } from '../../services/productService';
import { brandService } from '../../services/brandService';

const { Title } = Typography;

export default function ProductListPage() {
  const navigate = useNavigate();
  const { products, total, loading, page, pageSize, fetchProducts, setFilters, setPage } = useProductStore();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');
  const [categoryOptions, setCategoryOptions] = useState<any>(null);
  const [brands, setBrands] = useState<any[]>([]);
  const [selectedL1, setSelectedL1] = useState<string>('');

  useEffect(() => {
    fetchProducts();
    productService.getCategoryOptions().then(({ data }) => setCategoryOptions(data));
    brandService.getBrands().then(({ data }) => setBrands(data.results || data));
  }, []);

  const handleDeactivate = async (id: number) => {
    try {
      await productService.deleteProduct(id);
      message.success('已下架');
      fetchProducts();
    } catch {
      message.error('下架失败');
    }
  };

  const handleHardDelete = async (id: number) => {
    try {
      await productService.deleteProduct(id, true);
      message.success('已删除');
      fetchProducts();
    } catch {
      message.error('删除失败');
    }
  };

  const handleReactivate = async (id: number) => {
    try {
      await productService.reactivateProduct(id);
      message.success('已上架');
      fetchProducts();
    } catch {
      message.error('上架失败');
    }
  };

  const columns: any[] = [
    { title: '名称', dataIndex: 'name' },
    { title: '编号', dataIndex: 'code' },
    { title: '产地', dataIndex: 'origin', render: (v: string) => ({ IMPORT: '进口', DOMESTIC: '国产', CUSTOM: '定制' }[v]) },
    { title: '最低售价', dataIndex: 'min_price', render: (v: number) => v ? `¥${v}` : '-' },
    { title: '状态', dataIndex: 'is_active', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '上架' : '下架'}</Tag> },
  ];

  if (isAdmin) {
    columns.push({
      title: '操作',
      width: 200,
      render: (_: any, record: any) => (
        <Space size="small" onClick={(e) => e.stopPropagation()}>
          <Button size="small" icon={<EditOutlined />} onClick={() => navigate(`/products/${record.id}/edit`)} />
          {record.is_active ? (
            <Popconfirm
              title="确认下架？"
              description="下架后产品不再展示，仍可再次执行删除。"
              okText="下架"
              cancelText="取消"
              onConfirm={() => handleDeactivate(record.id)}
            >
              <Button size="small">下架</Button>
            </Popconfirm>
          ) : (
            <>
              <Button size="small" onClick={() => handleReactivate(record.id)}>上架</Button>
              <Popconfirm
                title="确认删除？"
                description="将永久删除该产品，无法恢复。"
                okText="删除"
                cancelText="取消"
                okButtonProps={{ danger: true }}
                onConfirm={() => handleHardDelete(record.id)}
              >
                <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    });
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>产品管理</Title>
        {isAdmin && <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/products/new')}>新建产品</Button>}
      </Space>
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search placeholder="搜索产品..." allowClear onSearch={(v) => setFilters({ search: v })} style={{ width: 220 }} />
        <Select placeholder="一级分类" allowClear style={{ width: 150 }}
          value={selectedL1 || undefined}
          onChange={(v) => { setSelectedL1(v || ''); setFilters({ category_l1: v, category_l2: undefined }); }}
          options={(categoryOptions?.category_l1 || []).map((c: any) => ({ value: c.value, label: c.label }))} />
        <Select placeholder="二级分类" allowClear style={{ width: 160 }} disabled={!selectedL1}
          onChange={(v) => setFilters({ category_l2: v })}
          options={(categoryOptions?.category_l2?.[selectedL1] || []).map((c: any) => ({ value: c.value, label: c.label }))} />
        <Select placeholder="品牌" allowClear style={{ width: 130 }}
          onChange={(v) => setFilters({ brand: v })}
          options={brands.map((b: any) => ({ value: b.id, label: b.name }))} />
        <Select placeholder="产地" allowClear style={{ width: 110 }} onChange={(v) => setFilters({ origin: v })}
          options={[{ value: 'IMPORT', label: '进口' }, { value: 'DOMESTIC', label: '国产' }, { value: 'CUSTOM', label: '定制' }]} />
        <Select placeholder="货期" allowClear style={{ width: 150 }}
          onChange={(v) => setFilters({ lead_time: v })}
          options={[
            { value: 'WITHIN_45D', label: '45天内' },
            { value: '2_4M_VIETNAM', label: '2-4月【越南】' },
            { value: '2_4M_MALAYSIA', label: '2-4月【马来西亚】' },
            { value: '4_6M_EU', label: '4-6月【荷兰/意大利/德国】' },
          ]} />
        <InputNumber placeholder="最低价" min={0} style={{ width: 100 }} onChange={(v) => setFilters({ min_price: (v as number) || undefined })} />
        <InputNumber placeholder="最高价" min={0} style={{ width: 100 }} onChange={(v) => setFilters({ max_price: (v as number) || undefined })} />
      </Space>
      <Table dataSource={products} rowKey="id" loading={loading}
        pagination={{ current: page, pageSize, total, onChange: setPage }}
        onRow={(r) => ({ onClick: () => navigate(`/products/${r.id}`), style: { cursor: 'pointer' } })}
        columns={columns} />
    </div>
  );
}
