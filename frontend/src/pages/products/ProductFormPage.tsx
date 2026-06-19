import { useEffect, useState } from 'react';
import {
  Button, Card, Col, Divider, Form, Image, Input, InputNumber, message, Popconfirm,
  Row, Select, Space, Table, Tabs, Tag, Typography, Upload,
} from 'antd';
import { DeleteOutlined, InboxOutlined, PlusOutlined, StarOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { productService } from '../../services/productService';
import { brandService } from '../../services/brandService';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Dragger } = Upload;

export default function ProductFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [brands, setBrands] = useState<any[]>([]);
  const [categoryOptions, setCategoryOptions] = useState<any>(null);
  const [selectedL1, setSelectedL1] = useState<string>('');
  const navigate = useNavigate();

  // 配置维度管理
  const [dimensions, setDimensions] = useState<any[]>([]);
  const [configExcelPreview, setConfigExcelPreview] = useState<any>(null);
  const [configExcelFile, setConfigExcelFile] = useState<File | null>(null);

  // 图片管理
  const [images, setImages] = useState<any[]>([]);
  const loadImages = () => {
    if (id) productService.getProduct(Number(id)).then(({ data }) => setImages(data.images || []));
  };

  const handleUploadImages = async (file: File) => {
    if (!id) return;
    const fd = new FormData();
    fd.append('images', file);
    try {
      await productService.uploadImages(Number(id), fd);
      message.success('图片上传成功');
      loadImages();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '图片上传失败');
    }
  };

  const handleDeleteImage = async (imageId: number) => {
    try {
      await productService.deleteImage(imageId);
      message.success('图片已删除');
      loadImages();
    } catch { message.error('删除失败'); }
  };

  const handleSetCover = async (imageId: number) => {
    try {
      await productService.setCoverImage(imageId);
      message.success('已设为封面');
      loadImages();
    } catch { message.error('操作失败'); }
  };

  useEffect(() => {
    brandService.getBrands().then(({ data }) => setBrands(data.results || data));
    productService.getCategoryOptions().then(({ data }) => setCategoryOptions(data));
    if (isEdit) {
      productService.getProduct(Number(id)).then(({ data }) => {
        form.setFieldsValue(data);
        setSelectedL1(data.category_l1 || '');
        setImages(data.images || []);
      });
      productService.getConfigDimensions(Number(id)).then(({ data }) => setDimensions(data));
    }
  }, [id]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (isEdit) {
        await productService.updateProduct(Number(id), values);
        message.success('产品更新成功');
      } else {
        await productService.createProduct(values);
        message.success('产品创建成功');
      }
      navigate('/products');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    } finally { setLoading(false); }
  };

  const handleL1Change = (value: string) => {
    setSelectedL1(value);
    form.setFieldValue('category_l2', '');
  };

  // 配置 Excel 上传
  const handleConfigExcelUpload = async (file: File) => {
    if (!id) return;
    try {
      const { data } = await productService.uploadConfigExcel(Number(id), file, false);
      setConfigExcelPreview(data);
      setConfigExcelFile(file);
      message.info(`解析完成：${data.dimensions_count} 个维度，${data.price_entries_count} 条价格`);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '解析失败');
    }
  };

  const handleConfigExcelConfirm = async () => {
    if (!id || !configExcelPreview || !configExcelFile) {
      message.error('请先上传并预览配置 Excel');
      return;
    }
    try {
      message.loading({ content: '正在导入...', key: 'confirm-import' });
      await productService.uploadConfigExcel(Number(id), configExcelFile, true);
      message.success({ content: '配置导入成功', key: 'confirm-import' });
      setConfigExcelPreview(null);
      setConfigExcelFile(null);
      // 刷新维度
      productService.getConfigDimensions(Number(id)).then(({ data }) => setDimensions(data));
    } catch (err: any) {
      message.error({ content: err.response?.data?.detail || '导入失败', key: 'confirm-import' });
    }
  };

  // 手工添加维度
  const [newDimForm] = Form.useForm();
  const handleAddDimension = async () => {
    if (!id) return;
    try {
      const values = await newDimForm.validateFields();
      const options = (values.options_text || '').split(',').map((o: string) => ({ key: o.trim(), label: o.trim() })).filter((o: any) => o.key);
      await productService.addConfigDimension(Number(id), {
        dimension_key: values.dimension_key,
        dimension_label: values.dimension_label,
        options,
        parent_dimension: values.parent_dimension || '',
        is_required: values.is_required ?? true,
        sort_order: dimensions.length,
      });
      message.success('维度添加成功');
      newDimForm.resetFields();
      productService.getConfigDimensions(Number(id)).then(({ data }) => setDimensions(data));
    } catch (err: any) {
      message.error(err.response?.data?.detail || '添加失败');
    }
  };

  const l2Options = categoryOptions?.category_l2?.[selectedL1] || [];

  return (
    <div style={{ maxWidth: 900 }}>
      <Title level={4}>{isEdit ? '编辑产品' : '新建产品'}</Title>

      <Tabs defaultActiveKey="basic" items={[
        {
          key: 'basic',
          label: '基本信息',
          children: (
            <Form form={form} layout="vertical" onFinish={handleSubmit}>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="name" label="产品名称" rules={[{ required: true }]}><Input /></Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="code" label="产品编号"><Input /></Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="category_l1" label="一级类别" rules={[{ required: true }]}>
                    <Select
                      options={categoryOptions?.category_l1?.map((c: any) => ({ value: c.value, label: c.label })) || []}
                      onChange={handleL1Change}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="category_l2" label="二级类别">
                    <Select
                      options={l2Options.map((c: any) => ({ value: c.value, label: c.label }))}
                      disabled={!selectedL1}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="brand" label="品牌">
                    <Select
                      options={brands.map((b: any) => ({ value: b.id, label: b.name }))}
                      allowClear
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="origin" label="产地" rules={[{ required: true }]}>
                    <Select options={[{ value: 'IMPORT', label: '进口' }, { value: 'DOMESTIC', label: '国产' }]} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="lead_time" label="货期">
                    <Select options={[
                      { value: 'WITHIN_45D', label: '45天内' },
                      { value: '2_4M_VIETNAM', label: '2-4月【越南】' },
                      { value: '2_4M_MALAYSIA', label: '2-4月【马来西亚】' },
                      { value: '4_6M_EU', label: '4-6月【荷兰/意大利/德国】' },
                    ]} allowClear />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="pricing_mode" label="定价模式">
                    <Select options={[
                      { value: 'MATRIX', label: '配置-价格映射表' },
                      { value: 'RULE', label: '基准价+加价规则' },
                    ]} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="base_price" label="基准价（RULE模式）">
                    <InputNumber style={{ width: '100%' }} min={0} precision={2} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="min_price" label="最低售价">
                    <InputNumber style={{ width: '100%' }} min={0} precision={2} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="length_mm" label="长度 (mm)"><InputNumber style={{ width: '100%' }} min={0} /></Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="width_mm" label="宽度 (mm)"><InputNumber style={{ width: '100%' }} min={0} /></Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="height_mm" label="高度 (mm)"><InputNumber style={{ width: '100%' }} min={0} /></Form.Item>
                </Col>
              </Row>

              <Form.Item name="official_url" label="官网链接"><Input /></Form.Item>
              <Form.Item name="model_3d_url" label="3D 模型链接"><Input /></Form.Item>
              <Form.Item name="description" label="产品描述"><TextArea rows={4} /></Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>{isEdit ? '保存' : '创建'}</Button>
              </Form.Item>
            </Form>
          ),
        },
        ...(isEdit ? [{
          key: 'images',
          label: '图片管理',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card title="上传图片" size="small">
                <Dragger
                  accept="image/*"
                  multiple
                  showUploadList={false}
                  beforeUpload={(file) => { handleUploadImages(file); return false; }}
                >
                  <p className="ant-upload-drag-icon"><InboxOutlined /></p>
                  <p>点击或拖拽上传产品图片（支持多张，单张 ≤ 10MB）</p>
                </Dragger>
              </Card>
              <Card title="已有图片" size="small">
                {images.length === 0 ? <Text type="secondary">暂无图片</Text> : (
                  <Image.PreviewGroup>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                      {images.map((img: any) => (
                        <div key={img.id} style={{
                          border: img.is_cover ? '2px solid #1890ff' : '1px solid #f0f0f0',
                          borderRadius: 4, padding: 4, width: 150,
                        }}>
                          <Image width={138} height={138} style={{ objectFit: 'cover', borderRadius: 4 }}
                            src={`/media/${img.thumbnail_path?.medium || img.image_path}`} />
                          <div style={{ marginTop: 4, textAlign: 'center' }}>
                            {img.is_cover ? <Tag color="blue">封面</Tag> : (
                              <Button size="small" type="link" icon={<StarOutlined />} onClick={() => handleSetCover(img.id)}>设为封面</Button>
                            )}
                            <Popconfirm title="删除该图片？" okText="删除" cancelText="取消"
                              okButtonProps={{ danger: true }} onConfirm={() => handleDeleteImage(img.id)}>
                              <Button size="small" type="link" danger icon={<DeleteOutlined />} />
                            </Popconfirm>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Image.PreviewGroup>
                )}
              </Card>
            </Space>
          ),
        }] : []),
        ...(isEdit ? [{
          key: 'config',
          label: '配置管理',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 已有维度列表 */}
              <Card title="已有配置维度" size="small">
                <Table
                  dataSource={dimensions}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  columns={[
                    { title: '维度键', dataIndex: 'dimension_key', width: 150 },
                    { title: '展示名', dataIndex: 'dimension_label', width: 150 },
                    { title: '选项', dataIndex: 'options', render: (opts: any[]) => opts?.map(o => o.label || o.key).join(', ') },
                    { title: '必填', dataIndex: 'is_required', render: (v: boolean) => v ? '是' : '否', width: 60 },
                    { title: '级联', dataIndex: 'parent_dimension', width: 120 },
                  ]}
                />
              </Card>

              {/* Excel 导入 */}
              <Card title="配置 Excel 导入" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space>
                    <Button icon={<UploadOutlined />} onClick={() => productService.downloadConfigTemplate().then(({ data }) => {
                      const url = URL.createObjectURL(data);
                      const a = document.createElement('a'); a.href = url; a.download = 'product_config_template.xlsx'; a.click();
                    })}>下载模板</Button>
                  </Space>
                  <Dragger
                    accept=".xlsx"
                    maxCount={1}
                    beforeUpload={(file) => {
                      handleConfigExcelUpload(file);
                      return false;
                    }}
                  >
                    <p className="ant-upload-drag-icon"><InboxOutlined /></p>
                    <p>点击或拖拽上传配置 Excel</p>
                  </Dragger>
                  {configExcelPreview && (
                    <Card size="small" style={{ marginTop: 8 }}>
                      <Text>模式: {configExcelPreview.pricing_mode} | 维度: {configExcelPreview.dimensions_count} | 价格条目: {configExcelPreview.price_entries_count}</Text>
                      {configExcelPreview.errors?.length > 0 && (
                        <div style={{ color: 'red', marginTop: 4 }}>
                          {configExcelPreview.errors.map((e: string, i: number) => <div key={i}>{e}</div>)}
                        </div>
                      )}
                      <Button type="primary" style={{ marginTop: 8 }} onClick={handleConfigExcelConfirm}
                        disabled={configExcelPreview.errors?.length > 0}>
                        确认导入
                      </Button>
                    </Card>
                  )}
                </Space>
              </Card>

              {/* 手工添加维度 */}
              <Card title="手工添加维度" size="small">
                <Form form={newDimForm} layout="inline" style={{ flexWrap: 'wrap', gap: 8 }}>
                  <Form.Item name="dimension_key" rules={[{ required: true, message: '必填' }]}>
                    <Input placeholder="维度键 (如 frame_color)" />
                  </Form.Item>
                  <Form.Item name="dimension_label" rules={[{ required: true, message: '必填' }]}>
                    <Input placeholder="展示名 (如 框架颜色)" />
                  </Form.Item>
                  <Form.Item name="options_text" rules={[{ required: true, message: '必填' }]}>
                    <Input placeholder="选项 (逗号分隔: P1,P2,P3)" style={{ width: 200 }} />
                  </Form.Item>
                  <Form.Item name="parent_dimension">
                    <Input placeholder="父维度 (可空)" />
                  </Form.Item>
                  <Form.Item name="is_required" initialValue={true}>
                    <Select style={{ width: 80 }} options={[{ value: true, label: '必填' }, { value: false, label: '可选' }]} />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleAddDimension}>添加</Button>
                  </Form.Item>
                </Form>
              </Card>
            </Space>
          ),
        }] : []),
      ]} />
    </div>
  );
}
