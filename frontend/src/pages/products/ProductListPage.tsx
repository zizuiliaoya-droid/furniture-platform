import { useEffect, useState } from 'react';
import { Button, Input, InputNumber, message, Modal, Popconfirm, Select, Space, Table, Tag, Typography, Upload } from 'antd';
import { DeleteOutlined, DownloadOutlined, EditOutlined, ImportOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useProductStore } from '../../store/productStore';
import { useAuthStore } from '../../store/authStore';
import { productService } from '../../services/productService';
import { brandService } from '../../services/brandService';

const { Title, Text } = Typography;

function downloadBlob(data: Blob, filename: string) {
  const url = URL.createObjectURL(data);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export default function ProductListPage() {
  const navigate = useNavigate();
  const { products, total, loading, page, pageSize, filters, fetchProducts, setFilters, resetFilters, setPage } = useProductStore();
  const isAdmin = !!useAuthStore((s) => s.user?.is_admin);
  const [categoryOptions, setCategoryOptions] = useState<any>(null);
  const [brands, setBrands] = useState<any[]>([]);
  const [batchOpen, setBatchOpen] = useState(false);
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [batchPreview, setBatchPreview] = useState<any>(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const selectedL1 = filters.category_l1 || '';

  useEffect(() => {
    // 进入页面重置筛选，避免全局 store 残留的隐形筛选导致列表变少
    resetFilters();
    productService.getCategoryOptions().then(({ data }) => setCategoryOptions(data));
    brandService.getBrands().then(({ data }) => setBrands(data.results || data));
  }, []);

  const handleBatchUpload = async (file: File) => {
    setBatchFile(file);
    try {
      const { data } = await productService.batchImport(file, false);
      setBatchPreview(data);
      message.info(`解析完成：${data.product_count} 个产品`);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '解析失败');
    }
  };

  const handleBatchConfirm = async () => {
    if (!batchFile) { message.error('请先上传文件'); return; }
    setBatchLoading(true);
    try {
      const { data } = await productService.batchImport(batchFile, true);
      message.success(`导入成功：新增 ${data.created}，更新 ${data.updated}`);
      setBatchOpen(false);
      setBatchFile(null);
      setBatchPreview(null);
      fetchProducts();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '导入失败');
    } finally {
      setBatchLoading(false);
    }
  };

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
        {isAdmin && (
          <Space>
            <Button icon={<ImportOutlined />} onClick={() => setBatchOpen(true)}>批量导入</Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/products/new')}>新建产品</Button>
          </Space>
        )}
      </Space>
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search placeholder="搜索产品..." allowClear onSearch={(v) => setFilters({ search: v })} style={{ width: 220 }} />
        <Select placeholder="一级分类" allowClear style={{ width: 150 }}
          value={filters.category_l1}
          onChange={(v) => setFilters({ category_l1: v, category_l2: undefined })}
          options={(categoryOptions?.category_l1 || []).map((c: any) => ({ value: c.value, label: c.label }))} />
        <Select placeholder="二级分类" allowClear style={{ width: 160 }} disabled={!selectedL1}
          value={filters.category_l2}
          onChange={(v) => setFilters({ category_l2: v })}
          options={(categoryOptions?.category_l2?.[selectedL1] || []).map((c: any) => ({ value: c.value, label: c.label }))} />
        <Select placeholder="品牌" allowClear style={{ width: 130 }}
          value={filters.brand}
          onChange={(v) => setFilters({ brand: v })}
          options={brands.map((b: any) => ({ value: b.id, label: b.name }))} />
        <Select placeholder="产地" allowClear style={{ width: 110 }}
          value={filters.origin}
          onChange={(v) => setFilters({ origin: v })}
          options={[{ value: 'IMPORT', label: '进口' }, { value: 'DOMESTIC', label: '国产' }, { value: 'CUSTOM', label: '定制' }]} />
        <Select placeholder="货期" allowClear style={{ width: 150 }}
          value={filters.lead_time}
          onChange={(v) => setFilters({ lead_time: v })}
          options={[
            { value: 'WITHIN_45D', label: '45天内' },
            { value: '2_4M_VIETNAM', label: '2-4月【越南】' },
            { value: '2_4M_MALAYSIA', label: '2-4月【马来西亚】' },
            { value: '4_6M_EU', label: '4-6月【荷兰/意大利/德国】' },
          ]} />
        <InputNumber placeholder="最低价" min={0} style={{ width: 100 }} value={filters.min_price}
          onChange={(v) => setFilters({ min_price: (v as number) || undefined })} />
        <InputNumber placeholder="最高价" min={0} style={{ width: 100 }} value={filters.max_price}
          onChange={(v) => setFilters({ max_price: (v as number) || undefined })} />
        <Button onClick={() => resetFilters()}>清除筛选</Button>
      </Space>
      <Table dataSource={products} rowKey="id" loading={loading}
        pagination={{ current: page, pageSize, total, onChange: setPage }}
        onRow={(r) => ({ onClick: () => navigate(`/products/${r.id}`), style: { cursor: 'pointer' } })}
        columns={columns} />

      <Modal
        title="批量导入产品"
        open={batchOpen}
        onCancel={() => { setBatchOpen(false); setBatchFile(null); setBatchPreview(null); }}
        onOk={handleBatchConfirm}
        confirmLoading={batchLoading}
        okText="确认导入"
        okButtonProps={{ disabled: !batchPreview || batchPreview.errors?.length > 0 }}
        width={640}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Button icon={<DownloadOutlined />} onClick={() =>
            productService.downloadBatchTemplate().then(({ data }) => downloadBlob(data, 'product_customer_template.xlsx'))
          }>下载客户自助模板（每产品一个配置 Sheet）</Button>
          <Upload
            accept=".xlsx"
            maxCount={1}
            showUploadList={false}
            beforeUpload={(file) => { handleBatchUpload(file); return false; }}
          >
            <Button icon={<UploadOutlined />} type="dashed" block>上传并预览</Button>
          </Upload>
          {batchFile && <Text type="secondary">已选择：{batchFile.name}</Text>}
          {batchPreview && (
            <div style={{ background: '#f6ffed', padding: 12, borderRadius: 4 }}>
              <Text>格式：{batchPreview.format === 'horizontal' ? '客户横向模板' : '旧版长格式'}；共解析 <Text strong>{batchPreview.product_count}</Text> 个产品</Text>
              {(batchPreview.products || []).map((p: any) => (
                <div key={`${p.sheet_name || ''}-${p.code || p.name}`} style={{ marginTop: 4 }}>
                  <Text type="secondary">
                    {p.sheet_name ? `[${p.sheet_name}] ` : ''}{p.name}（{p.code || '无编号'}）：
                    {p.dimension_count} 维度 / {p.option_count} 选项 / {p.preset_count} 预设 / {p.price_count || 0} 组合价格
                  </Text>
                  {(p.price_count || 0) === 0 && batchPreview.format === 'horizontal' && (
                    <Tag color="orange" style={{ marginLeft: 8 }}>可导入配置，但暂无价格，不能加入报价单</Tag>
                  )}
                </div>
              ))}
              {batchPreview.warnings?.length > 0 && (
                <div style={{ color: '#ad6800', marginTop: 8 }}>
                  {batchPreview.warnings.map((warning: string, index: number) => <div key={index}>警告：{warning}</div>)}
                </div>
              )}
              {batchPreview.errors?.length > 0 && (
                <div style={{ color: 'red', marginTop: 8 }}>
                  {batchPreview.errors.map((error: string, index: number) => <div key={index}>错误：{error}</div>)}
                </div>
              )}
            </div>
          )}
        </Space>
      </Modal>
    </div>
  );
}
