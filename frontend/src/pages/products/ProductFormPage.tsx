import { useEffect, useState } from 'react';
import {
  Alert, Button, Card, Checkbox, Col, Divider, Form, Image, Input, InputNumber, message, Modal, Popconfirm,
  Row, Select, Space, Table, Tabs, Tag, Typography, Upload,
} from 'antd';
import { DeleteOutlined, EditOutlined, InboxOutlined, PlusOutlined, StarOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { productService } from '../../services/productService';
import { brandService } from '../../services/brandService';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Dragger } = Upload;

const parseOptionsText = (value = '') => value
  .split(/[,，;；\n]+/)
  .map((token: string) => token.trim())
  .filter(Boolean)
  .map((token: string) => {
    const [key, ...labelParts] = token.split('|');
    return { key: key.trim(), label: (labelParts.join('|').trim() || key.trim()) };
  });

const formatOptionsText = (options: any[] = []) => options
  .map((option) => option.label && option.label !== option.key
    ? `${option.key}|${option.label}` : option.key)
  .join(', ');

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
  const [configMapping, setConfigMapping] = useState<any>({});
  const [replaceDimensions, setReplaceDimensions] = useState(false);
  const [replacePrices, setReplacePrices] = useState(true);
  const [dimensionModalOpen, setDimensionModalOpen] = useState(false);
  const [editingDimension, setEditingDimension] = useState<any>(null);
  const [dimensionImpact, setDimensionImpact] = useState<any>(null);
  const [dimensionForm] = Form.useForm();

  const reloadDimensions = () => {
    if (id) productService.getConfigDimensions(Number(id)).then(({ data }) => setDimensions(data));
  };

  // 新建模式下暂存（一页提交）：待上传图片 + 待创建维度
  const [pendingImages, setPendingImages] = useState<File[]>([]);
  const [pendingDims, setPendingDims] = useState<any[]>([]);

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
        await productService.createComposite({
          product: values,
          dimensions: pendingDims.map((dimension, index) => ({
            ...dimension,
            sort_order: index,
          })),
          presets: [],
          price_matrix: [],
        }, pendingImages);
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

  // 配置 Excel 上传：支持标准模板、自制横向/纵向/组合价格表及人工映射。
  const handleConfigExcelUpload = async (file: File, mapping: any = {}) => {
    if (!id) return;
    try {
      const { data } = await productService.uploadConfigExcel(
        Number(id), file, false, { mapping });
      setConfigExcelPreview(data);
      setConfigExcelFile(file);
      setConfigMapping(mapping);
      if (data.needs_mapping) {
        message.info('请先选择数据 Sheet 和结构，再重新解析');
      } else {
        message.info(`解析完成：${data.dimensions_count} 个维度，${data.price_entries_count} 条价格`);
      }
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
      await productService.uploadConfigExcel(Number(id), configExcelFile, true, {
        mapping: configMapping, replaceDimensions, replacePrices,
      });
      message.success({ content: '配置导入成功', key: 'confirm-import' });
      setConfigExcelPreview(null);
      setConfigExcelFile(null);
      setConfigMapping({});
      setReplaceDimensions(false);
      reloadDimensions();
    } catch (err: any) {
      const errors = err.response?.data?.errors;
      const detail = errors?.length ? errors.join('；') : err.response?.data?.detail;
      message.error({ content: detail || '导入失败', key: 'confirm-import' });
    }
  };

  // 手工添加维度
  const [newDimForm] = Form.useForm();
  const handleAddDimension = async () => {
    try {
      const values = await newDimForm.validateFields();
      const options = parseOptionsText(values.options_text);
      const payload = {
        dimension_key: values.dimension_key.trim(),
        dimension_label: values.dimension_label.trim(),
        options,
        parent_dimension: values.parent_dimension?.trim() || '',
        is_required: values.is_required ?? true,
        sort_order: dimensions.length,
      };
      if (!id) {
        setPendingDims((prev) => [...prev, payload]);
        newDimForm.resetFields();
        message.success('已添加（保存产品时一并创建）');
        return;
      }
      await productService.addConfigDimension(Number(id), payload);
      message.success('维度添加成功');
      newDimForm.resetFields();
      reloadDimensions();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '添加失败');
    }
  };

  const openDimensionEditor = async (dimension: any) => {
    if (!id) return;
    try {
      const { data: impact } = await productService.getConfigDimensionImpact(Number(id), dimension.id);
      setEditingDimension(dimension);
      setDimensionImpact(impact);
      dimensionForm.setFieldsValue({
        ...dimension,
        options_text: formatOptionsText(dimension.options),
      });
      setDimensionModalOpen(true);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '无法读取维度引用信息');
    }
  };

  const saveDimension = async () => {
    if (!id || !editingDimension) return;
    try {
      const values = await dimensionForm.validateFields();
      await productService.updateConfigDimension(Number(id), editingDimension.id, {
        dimension_key: values.dimension_key.trim(),
        dimension_label: values.dimension_label.trim(),
        options: parseOptionsText(values.options_text),
        parent_dimension: values.parent_dimension?.trim() || '',
        is_required: values.is_required,
        sort_order: values.sort_order ?? editingDimension.sort_order,
      });
      message.success('配置维度已更新');
      setDimensionModalOpen(false);
      reloadDimensions();
    } catch (err: any) {
      if (err?.errorFields) return;
      message.error(err.response?.data?.detail || '维度更新失败');
    }
  };

  const deleteDimension = async (dimension: any) => {
    if (!id) return;
    try {
      const { data: impact } = await productService.getConfigDimensionImpact(Number(id), dimension.id);
      if (impact.child_dimensions > 0) {
        message.error('该维度仍有下级维度，请先修改下级维度的级联关系');
        return;
      }
      Modal.confirm({
        title: impact.can_delete ? `删除维度“${dimension.dimension_label}”？` : '删除维度并清除受影响定价数据？',
        okText: impact.can_delete ? '删除' : '强制删除',
        okButtonProps: { danger: true },
        cancelText: '取消',
        content: (
          <Space direction="vertical" size={4}>
            <Text>组合价格：{impact.matrix_rows} 条；价格规则：{impact.rules} 条；默认配置：{impact.presets} 条。</Text>
            <Text>历史报价：{impact.quote_items} 条（仅保留快照，不会被改写）。</Text>
            {!impact.can_delete && <Text type="danger">强制删除会清除上述受影响定价和默认配置，产品可能暂时无法报价。</Text>}
          </Space>
        ),
        onOk: async () => {
          await productService.deleteConfigDimension(Number(id), dimension.id, !impact.can_delete);
          message.success('配置维度已删除');
          reloadDimensions();
        },
      });
    } catch (err: any) {
      message.error(err.response?.data?.detail || '维度删除失败');
    }
  };

  const l2Options = categoryOptions?.category_l2?.[selectedL1] || [];
  const selectedMappingSheet = configExcelPreview?.available_sheets?.find(
    (sheet: any) => sheet.name === configMapping.sheet);
  const mappingHeaders = selectedMappingSheet?.headers || [];

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

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="shape" label="形状">
                    <Select allowClear placeholder="方形/圆形/L形/异形…" options={[
                      { value: '方形', label: '方形' },
                      { value: '圆形', label: '圆形' },
                      { value: 'L形', label: 'L形' },
                      { value: '异形', label: '异形' },
                    ]} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="diameter_mm" label="直径 (mm，圆形用)"><InputNumber style={{ width: '100%' }} min={0} /></Form.Item>
                </Col>
              </Row>

              <Form.Item name="official_url" label="官网链接"><Input /></Form.Item>
              <Form.Item name="model_3d_url" label="3D 模型链接"><Input /></Form.Item>
              <Form.Item name="description" label="产品描述"><TextArea rows={4} /></Form.Item>

              {!isEdit && (
                <>
                  <Divider orientation="left">产品图片（可选）</Divider>
                  <Dragger
                    accept="image/*"
                    multiple
                    showUploadList={false}
                    beforeUpload={(file) => { setPendingImages((prev) => [...prev, file]); return false; }}
                  >
                    <p className="ant-upload-drag-icon"><InboxOutlined /></p>
                    <p>点击或拖拽添加图片（保存时随产品一起上传）</p>
                  </Dragger>
                  {pendingImages.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                      {pendingImages.map((f, i) => (
                        <div key={i} style={{ position: 'relative', width: 90 }}>
                          <img src={URL.createObjectURL(f)} alt="" style={{ width: 88, height: 88, objectFit: 'cover', borderRadius: 4 }} />
                          <Button size="small" danger type="link" icon={<DeleteOutlined />}
                            onClick={() => setPendingImages((prev) => prev.filter((_, idx) => idx !== i))} />
                        </div>
                      ))}
                    </div>
                  )}

                  <Divider orientation="left">配置维度（可选）</Divider>
                  <Form form={newDimForm} layout="inline" style={{ flexWrap: 'wrap', gap: 8, marginBottom: 8 }}>
                    <Form.Item name="dimension_key" rules={[{ required: true, message: '必填' }]}>
                      <Input placeholder="维度键 (如 frame_color)" />
                    </Form.Item>
                    <Form.Item name="dimension_label" rules={[{ required: true, message: '必填' }]}>
                      <Input placeholder="展示名 (如 框架颜色)" />
                    </Form.Item>
                    <Form.Item name="options_text" rules={[{ required: true, message: '必填' }]}>
                      <Input placeholder="选项 (逗号: P1,P2,P3)" style={{ width: 180 }} />
                    </Form.Item>
                    <Form.Item name="parent_dimension">
                      <Input placeholder="父维度 (可空)" />
                    </Form.Item>
                    <Form.Item name="is_required" initialValue={true}>
                      <Select style={{ width: 80 }} options={[{ value: true, label: '必填' }, { value: false, label: '可选' }]} />
                    </Form.Item>
                    <Form.Item>
                      <Button icon={<PlusOutlined />} onClick={handleAddDimension}>添加</Button>
                    </Form.Item>
                  </Form>
                  {pendingDims.length > 0 && (
                    <Table
                      dataSource={pendingDims}
                      rowKey={(_, i) => String(i)}
                      pagination={false}
                      size="small"
                      style={{ marginBottom: 12 }}
                      columns={[
                        { title: '维度键', dataIndex: 'dimension_key', width: 140 },
                        { title: '展示名', dataIndex: 'dimension_label', width: 140 },
                        { title: '选项', dataIndex: 'options', render: (opts: any[]) => opts?.map((o) => o.label).join(', ') },
                        {
                          title: '操作', width: 60,
                          render: (_: any, __: any, i: number) => (
                            <Button size="small" danger type="link" icon={<DeleteOutlined />}
                              onClick={() => setPendingDims((prev) => prev.filter((_, idx) => idx !== i))} />
                          ),
                        },
                      ]}
                    />
                  )}
                </>
              )}

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
              <Card title="已有配置维度" size="small"
                extra={
                  <Button size="small" icon={<UploadOutlined />} onClick={() =>
                    productService.exportConfig(Number(id)).then(({ data }) => {
                      const url = URL.createObjectURL(data);
                      const a = document.createElement('a'); a.href = url; a.download = `product_${id}_config.xlsx`; a.click();
                      URL.revokeObjectURL(url);
                    })
                  }>导出配置</Button>
                }
              >
                <Table
                  dataSource={dimensions}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  columns={[
                    { title: '维度键', dataIndex: 'dimension_key', width: 135 },
                    { title: '展示名', dataIndex: 'dimension_label', width: 135 },
                    { title: '选项', dataIndex: 'options', render: (opts: any[]) => opts?.map(o => o.label || o.key).join(', ') },
                    { title: '必填', dataIndex: 'is_required', render: (v: boolean) => v ? '是' : '否', width: 55 },
                    { title: '级联', dataIndex: 'parent_dimension', width: 115 },
                    {
                      title: '操作', width: 110, fixed: 'right' as const,
                      render: (_: any, record: any) => (
                        <Space size={2}>
                          <Button size="small" type="link" icon={<EditOutlined />}
                            onClick={() => openDimensionEditor(record)}>编辑</Button>
                          <Button size="small" type="link" danger icon={<DeleteOutlined />}
                            onClick={() => deleteDimension(record)}>删除</Button>
                        </Space>
                      ),
                    },
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
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text>
                          识别格式: {configExcelPreview.detected_format || '-'} ｜
                          维度: {configExcelPreview.dimensions_count} ｜
                          价格: {configExcelPreview.price_entries_count} ｜
                          默认配置: {configExcelPreview.preset_count || 0}
                        </Text>

                        {configExcelPreview.needs_mapping && (
                          <Alert type="info" showIcon message="需要确认自制 Excel 的数据结构"
                            description={
                              <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                                <Select placeholder="选择数据 Sheet" style={{ width: '100%' }}
                                  value={configMapping.sheet}
                                  onChange={(sheet) => setConfigMapping((prev: any) => ({ ...prev, sheet }))}
                                  options={configExcelPreview.available_sheets.map((sheet: any) => ({
                                    value: sheet.name, label: `${sheet.name}（${sheet.headers.join('、') || '无表头'}）`,
                                  }))} />
                                <Select placeholder="选择数据结构" style={{ width: '100%' }}
                                  value={configMapping.format}
                                  onChange={(format) => setConfigMapping((prev: any) => ({ ...prev, format }))}
                                  options={[
                                    { value: 'horizontal', label: '横向选项表（第一行是维度，每列向下是选项）' },
                                    { value: 'vertical', label: '纵向明细表（每行是维度 + 选项）' },
                                    { value: 'combination', label: '完整组合价格表（每行是一套配置 + 最终价格）' },
                                  ]} />
                                {configMapping.format === 'vertical' && (
                                  <Space wrap>
                                    <Select placeholder="维度名称列" style={{ width: 180 }}
                                      value={configMapping.dimension_column}
                                      onChange={(value) => setConfigMapping((prev: any) => ({ ...prev, dimension_column: value }))}
                                      options={mappingHeaders.map((header: string) => ({ value: header, label: header }))} />
                                    <Select placeholder="选项列" style={{ width: 180 }}
                                      value={configMapping.option_column}
                                      onChange={(value) => setConfigMapping((prev: any) => ({ ...prev, option_column: value }))}
                                      options={mappingHeaders.map((header: string) => ({ value: header, label: header }))} />
                                    <Select allowClear placeholder="是否必填列（可选）" style={{ width: 180 }}
                                      value={configMapping.required_column}
                                      onChange={(value) => setConfigMapping((prev: any) => ({ ...prev, required_column: value }))}
                                      options={mappingHeaders.map((header: string) => ({ value: header, label: header }))} />
                                    <Select allowClear placeholder="父维度列（可选）" style={{ width: 180 }}
                                      value={configMapping.parent_column}
                                      onChange={(value) => setConfigMapping((prev: any) => ({ ...prev, parent_column: value }))}
                                      options={mappingHeaders.map((header: string) => ({ value: header, label: header }))} />
                                  </Space>
                                )}
                                {configMapping.format === 'combination' && (
                                  <Select placeholder="最终价格列" style={{ width: 220 }}
                                    value={configMapping.price_column}
                                    onChange={(value) => setConfigMapping((prev: any) => ({ ...prev, price_column: value }))}
                                    options={mappingHeaders.map((header: string) => ({ value: header, label: header }))} />
                                )}
                                <Button type="primary" disabled={!configMapping.sheet || !configMapping.format}
                                  onClick={() => configExcelFile && handleConfigExcelUpload(configExcelFile, configMapping)}>
                                  按映射重新解析
                                </Button>
                              </Space>
                            } />
                        )}

                        {configExcelPreview.impact && !configExcelPreview.needs_mapping && (
                          <Alert type="info" showIcon message="导入影响预览"
                            description={`现有 ${configExcelPreview.impact.existing_dimensions} 个维度、${configExcelPreview.impact.existing_matrix_rows} 条组合价格、${configExcelPreview.impact.existing_presets} 个预设；本次识别 ${configExcelPreview.impact.incoming_dimensions} 个维度、${configExcelPreview.impact.incoming_prices} 条价格。`} />
                        )}
                        {configExcelPreview.warnings?.map((warning: string, index: number) => (
                          <Alert key={`warning-${index}`} type="warning" showIcon message={warning} />
                        ))}
                        {configExcelPreview.errors?.map((error: string, index: number) => (
                          <Alert key={`error-${index}`} type="error" showIcon message={error} />
                        ))}

                        {!configExcelPreview.needs_mapping && (
                          <Space direction="vertical">
                            <Checkbox checked={replaceDimensions} onChange={(event) => setReplaceDimensions(event.target.checked)}>
                              完全替换现有维度（默认不勾选，采用安全合并）
                            </Checkbox>
                            {configExcelPreview.price_entries_count > 0 && (
                              <Checkbox checked={replacePrices} onChange={(event) => setReplacePrices(event.target.checked)}>
                                用文件中的完整价格替换现有价格和默认配置
                              </Checkbox>
                            )}
                            <Button type="primary" onClick={handleConfigExcelConfirm}
                              disabled={configExcelPreview.errors?.length > 0 || configExcelPreview.dimensions_count === 0}>
                              确认导入
                            </Button>
                          </Space>
                        )}
                      </Space>
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

      <Modal
        title="编辑配置维度"
        open={dimensionModalOpen}
        onCancel={() => setDimensionModalOpen(false)}
        onOk={saveDimension}
        okText="保存"
        cancelText="取消"
        width={620}
      >
        {dimensionImpact?.history_note && (
          <Alert type="info" showIcon message={dimensionImpact.history_note} style={{ marginBottom: 16 }} />
        )}
        <Form form={dimensionForm} layout="vertical">
          <Form.Item name="dimension_key" label="维度键" rules={[{ required: true }]}>
            <Input disabled={!!dimensionImpact?.key_locked}
              addonAfter={dimensionImpact?.key_locked ? '已被引用，键已锁定' : undefined} />
          </Form.Item>
          <Form.Item name="dimension_label" label="展示名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="options_text" label="选项" rules={[{ required: true }]} extra="使用逗号分隔；需要区分键和展示名时使用 key|展示名。已被价格引用的选项键不能删除。">
            <TextArea rows={4} placeholder="P1|黑色, P2|白色, P3|灰色" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="parent_dimension" label="级联条件" extra="格式：父维度键 或 父维度键=父选项键">
                <Input allowClear placeholder="backrest_material=网" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="is_required" label="是否必填">
                <Select options={[{ value: true, label: '必填' }, { value: false, label: '可选' }]} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="sort_order" label="排序">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          {dimensionImpact && (
            <Text type="secondary">
              当前引用：组合价格 {dimensionImpact.matrix_rows} 条、规则 {dimensionImpact.rules} 条、
              默认配置 {dimensionImpact.presets} 条、历史报价 {dimensionImpact.quote_items} 条。
            </Text>
          )}
        </Form>
      </Modal>
    </div>
  );
}
