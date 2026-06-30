import { useCallback, useEffect, useState } from 'react';
import {
  Button, Card, Col, Descriptions, Divider, Image, InputNumber, List,
  message, Modal, Row, Select, Space, Spin, Tag, Typography,
} from 'antd';
import { EditOutlined, PlusOutlined, ShoppingCartOutlined } from '@ant-design/icons';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { productService } from '../../services/productService';
import { quoteService } from '../../services/quoteService';
import { useAuthStore } from '../../store/authStore';

const { Title, Text, Paragraph } = Typography;

/**
 * 判断某配置维度在当前已选项下是否应显示。
 * parent_dimension 格式：
 *   ""                       —— 始终显示
 *   "parent_key"             —— 父维度已选（任意值）即显示
 *   "parent_key=parent_val"  —— 父维度已选且值等于 parent_val 才显示
 */
function isDimVisible(dim: any, selections: Record<string, string>): boolean {
  const parent = (dim.parent_dimension || '').trim();
  if (!parent) return true;
  const [pk, pv] = parent.split('=');
  const parentKey = pk.trim();
  const requiredVal = pv !== undefined ? pv.trim() : null;
  const parentVal = selections[parentKey];
  if (parentVal === undefined || parentVal === null || parentVal === '') return false;
  if (requiredVal !== null && parentVal !== requiredVal) return false;
  return true;
}

export default function ProductDetailPage() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const preselectedQuoteId = searchParams.get('quoteId');
  const [product, setProduct] = useState<any>(null);
  const [dimensions, setDimensions] = useState<any[]>([]);
  const [selections, setSelections] = useState<Record<string, string>>({});
  const [priceResult, setPriceResult] = useState<any>(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [documents, setDocuments] = useState<any[]>([]);
  const [quoteModalOpen, setQuoteModalOpen] = useState(false);
  const [quotes, setQuotes] = useState<any[]>([]);
  const [selectedQuoteId, setSelectedQuoteId] = useState<number | null>(null);
  const [selectedImageId, setSelectedImageId] = useState<number | null>(null);
  const [mainImagePath, setMainImagePath] = useState<string>('');
  const [quantity, setQuantity] = useState(1);
  const [discount, setDiscount] = useState(0);
  const [addingToQuote, setAddingToQuote] = useState(false);
  const navigate = useNavigate();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  useEffect(() => {
    if (!id) return;
    productService.getProduct(Number(id)).then(({ data }) => setProduct(data));
    productService.getConfigDimensions(Number(id)).then(({ data }) => setDimensions(data));
    productService.getProductDocuments(Number(id)).then(({ data }) => setDocuments(data));
  }, [id]);

  // 初始化主图（封面优先）
  useEffect(() => {
    if (product?.images?.length) {
      const cover = product.images.find((i: any) => i.is_cover) || product.images[0];
      setMainImagePath(cover.image_path);
    }
  }, [product]);

  // 价格计算（debounce 300ms）
  useEffect(() => {
    if (!id || !Object.keys(selections).length) {
      setPriceResult(null);
      return;
    }
    const timer = setTimeout(() => {
      setPriceLoading(true);
      productService.calculatePrice(Number(id), selections)
        .then(({ data }) => setPriceResult(data))
        .catch(() => setPriceResult(null))
        .finally(() => setPriceLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [id, selections]);

  const handleDimensionChange = (key: string, value: string) => {
    setSelections(prev => {
      const next: Record<string, string> = { ...prev };
      if (value === undefined || value === null || value === '') {
        delete next[key];
      } else {
        next[key] = value;
      }
      // 连锁清理：父条件不再满足的子维度选项一并移除
      let changed = true;
      while (changed) {
        changed = false;
        for (const dim of dimensions) {
          if (dim.dimension_key in next && !isDimVisible(dim, next)) {
            delete next[dim.dimension_key];
            changed = true;
          }
        }
      }
      return next;
    });
  };

  const openQuoteModal = useCallback(async () => {
    const { data } = await quoteService.getQuotes({ status: 'DRAFT' });
    setQuotes(data.results || data);
    if (preselectedQuoteId) {
      setSelectedQuoteId(Number(preselectedQuoteId));
    }
    setQuoteModalOpen(true);
  }, [preselectedQuoteId]);

  const handleAddToQuote = async () => {
    if (!selectedQuoteId || !product) return;
    setAddingToQuote(true);
    try {
      await quoteService.addItemFromProduct(selectedQuoteId, {
        product_id: product.id,
        selections,
        image_id: selectedImageId,
        quantity,
        discount,
      });
      message.success('已加入报价单');
      setQuoteModalOpen(false);
      if (preselectedQuoteId) {
        navigate(`/quotes/${preselectedQuoteId}`);
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '加入失败');
    } finally {
      setAddingToQuote(false);
    }
  };

  if (!product) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const ORIGIN_MAP: Record<string, string> = { IMPORT: '进口', DOMESTIC: '国产' };
  const LEAD_TIME_MAP: Record<string, string> = {
    WITHIN_45D: '45天内', '2_4M_VIETNAM': '2-4月【越南】',
    '2_4M_MALAYSIA': '2-4月【马来西亚】', '4_6M_EU': '4-6月【荷兰/意大利/德国】',
  };

  return (
    <div>
      {/* 顶部操作栏 */}
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>{product.name}</Title>
        <Space>
          {isAdmin && <Button icon={<EditOutlined />} onClick={() => navigate(`/products/${id}/edit`)}>编辑</Button>}
        </Space>
      </Space>

      <Row gutter={24}>
        {/* 左侧：图片 */}
        <Col xs={24} md={10}>
          <Card>
            {product.images?.length > 0 ? (
              <Image.PreviewGroup>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Image
                    width="100%"
                    style={{ maxHeight: 400, objectFit: 'contain' }}
                    src={`/media/${mainImagePath || product.images[0]?.image_path}`}
                  />
                  <Space wrap>
                    {product.images.map((img: any) => {
                      const isActive = (mainImagePath || product.images[0]?.image_path) === img.image_path;
                      return (
                        <img
                          key={img.id}
                          width={80}
                          height={80}
                          onClick={() => setMainImagePath(img.image_path)}
                          style={{
                            objectFit: 'cover', borderRadius: 4, cursor: 'pointer',
                            border: isActive ? '2px solid #1890ff' : '2px solid transparent',
                          }}
                          src={`/media/${img.thumbnail_path?.small || img.image_path}`}
                        />
                      );
                    })}
                  </Space>
                </Space>
              </Image.PreviewGroup>
            ) : (
              <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5' }}>
                <Text type="secondary">暂无图片</Text>
              </div>
            )}
          </Card>
        </Col>

        {/* 右侧：信息 + 配置选择器 + 价格 */}
        <Col xs={24} md={14}>
          <Card>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="编号">{product.code || '-'}</Descriptions.Item>
              <Descriptions.Item label="品牌">{product.brand_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="产地">{ORIGIN_MAP[product.origin] || '-'}</Descriptions.Item>
              <Descriptions.Item label="货期">{LEAD_TIME_MAP[product.lead_time] || '-'}</Descriptions.Item>
              <Descriptions.Item label="类别">{product.category_l1} / {product.category_l2}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={product.is_active ? 'green' : 'default'}>{product.is_active ? '上架' : '下架'}</Tag>
              </Descriptions.Item>
              {product.length_mm && <Descriptions.Item label="尺寸">{product.length_mm}×{product.width_mm}×{product.height_mm} mm</Descriptions.Item>}
              {product.official_url && <Descriptions.Item label="官网"><a href={product.official_url} target="_blank" rel="noreferrer">查看</a></Descriptions.Item>}
              {product.model_3d_url && <Descriptions.Item label="3D 模型"><a href={product.model_3d_url} target="_blank" rel="noreferrer">查看</a></Descriptions.Item>}
            </Descriptions>
            {product.description && <Paragraph style={{ marginTop: 12 }}>{product.description}</Paragraph>}
          </Card>

          {/* 配置选择器 */}
          {dimensions.length > 0 && (
            <Card title="配置选择" style={{ marginTop: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {dimensions.filter((dim: any) => isDimVisible(dim, selections)).map((dim: any) => (
                  <div key={dim.dimension_key}>
                    <Text strong>{dim.dimension_label}{dim.is_required && <Text type="danger"> *</Text>}</Text>
                    <div style={{ marginTop: 4 }}>
                      <Select
                        placeholder={`请选择${dim.dimension_label}`}
                        style={{ width: '100%' }}
                        value={selections[dim.dimension_key] || undefined}
                        onChange={v => handleDimensionChange(dim.dimension_key, v)}
                        options={dim.options.map((opt: any) => ({
                          label: opt.label || opt.key,
                          value: opt.key,
                        }))}
                        allowClear
                      />
                    </div>
                  </div>
                ))}
              </Space>

              {/* 实时价格展示 */}
              <Divider />
              {priceLoading ? (
                <Spin size="small" />
              ) : priceResult ? (
                priceResult.valid ? (
                  <Space direction="vertical">
                    <Text strong style={{ fontSize: 24, color: '#1890ff' }}>¥{priceResult.price}</Text>
                    <Text type="secondary">
                      {Object.entries(selections).map(([k, v]) => `${k}: ${v}`).join(' / ')}
                    </Text>
                  </Space>
                ) : (
                  <Space direction="vertical">
                    <Text type="danger">{priceResult.reason || '该配置组合无对应价格'}</Text>
                    {priceResult.missing_dimensions?.length > 0 && (
                      <Text type="secondary">缺少: {priceResult.missing_dimensions.join(', ')}</Text>
                    )}
                  </Space>
                )
              ) : (
                <Text type="secondary">请选择配置查看价格</Text>
              )}

              {/* 加入报价单按钮 */}
              <div style={{ marginTop: 16 }}>
                <Button
                  type="primary"
                  icon={<ShoppingCartOutlined />}
                  size="large"
                  disabled={!priceResult?.valid}
                  onClick={openQuoteModal}
                >
                  加入报价单
                </Button>
              </div>
            </Card>
          )}

          {/* 关联文档 */}
          {documents.length > 0 && (
            <Card title="关联文档" style={{ marginTop: 16 }}>
              {['DESIGN', 'TRAINING', 'CERTIFICATE'].map(type => {
                const docs = documents.filter((d: any) => d.relation_type === type);
                if (!docs.length) return null;
                const label = { DESIGN: '设计资源', TRAINING: '培训资料', CERTIFICATE: '资质文件' }[type];
                return (
                  <div key={type} style={{ marginBottom: 12 }}>
                    <Text strong>{label}</Text>
                    <List
                      size="small"
                      dataSource={docs}
                      renderItem={(doc: any) => (
                        <List.Item>
                          <a href={`/media/${doc.file_path}`} target="_blank" rel="noreferrer">{doc.document_name}</a>
                          <Text type="secondary" style={{ marginLeft: 8 }}>{doc.mime_type}</Text>
                        </List.Item>
                      )}
                    />
                  </div>
                );
              })}
            </Card>
          )}
        </Col>
      </Row>

      {/* 加入报价单弹窗 */}
      <Modal
        title="加入报价单"
        open={quoteModalOpen}
        onCancel={() => setQuoteModalOpen(false)}
        onOk={handleAddToQuote}
        confirmLoading={addingToQuote}
        okText="确认加入"
        okButtonProps={{ disabled: !selectedQuoteId }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {/* 选择目标报价单 */}
          <div>
            <Text strong>目标报价单</Text>
            <Select
              placeholder="选择报价单"
              style={{ width: '100%', marginTop: 4 }}
              value={selectedQuoteId}
              onChange={setSelectedQuoteId}
              options={quotes.map((q: any) => ({ label: `${q.title} - ${q.customer_name}`, value: q.id }))}
            />
            <Button type="link" size="small" icon={<PlusOutlined />}
              onClick={() => navigate('/quotes/new')}>
              新建报价单
            </Button>
          </div>

          {/* 选择明细展示图 */}
          {product.images?.length > 0 && (
            <div>
              <Text strong>选择明细展示图</Text>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 4 }}>
                {product.images.map((img: any) => (
                  <div
                    key={img.id}
                    onClick={() => setSelectedImageId(img.id)}
                    style={{
                      border: selectedImageId === img.id ? '2px solid #1890ff' : '2px solid transparent',
                      borderRadius: 4, cursor: 'pointer', padding: 2,
                    }}
                  >
                    <img
                      src={`/media/${img.thumbnail_path?.small || img.image_path}`}
                      alt="" style={{ width: 60, height: 60, objectFit: 'cover', borderRadius: 4 }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 数量 + 折扣 */}
          <Row gutter={16}>
            <Col span={12}>
              <Text strong>数量</Text>
              <InputNumber min={1} value={quantity} onChange={v => setQuantity(v || 1)} style={{ width: '100%', marginTop: 4 }} />
            </Col>
            <Col span={12}>
              <Text strong>折扣 (%)</Text>
              <InputNumber min={0} max={100} value={discount} onChange={v => setDiscount(v || 0)} style={{ width: '100%', marginTop: 4 }} />
            </Col>
          </Row>

          {/* 价格预览 */}
          {priceResult?.valid && (
            <div style={{ background: '#f6ffed', padding: 12, borderRadius: 4 }}>
              <Text>单价: ¥{priceResult.price} × {quantity} × (1 - {discount}%) = </Text>
              <Text strong>¥{(Number(priceResult.price) * quantity * (1 - discount / 100)).toFixed(2)}</Text>
            </div>
          )}
        </Space>
      </Modal>
    </div>
  );
}
