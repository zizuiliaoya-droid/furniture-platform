import { useCallback, useEffect, useMemo, useState } from 'react';
import { Badge, Button, Card, Checkbox, Col, Drawer, Input, Row, Select, Space, Tag, Typography } from 'antd';
import { FilterOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { catalogService } from '../../services/catalogService';

const { Title, Text } = Typography;
const { Meta } = Card;

interface FilterState {
  brand: string[];
  category_l1: string[];
  category_l2: string[];
  origin: string[];
  lead_time: string[];
  length_range: string;
  width_range: string;
  height_range: string;
  price_range: string;
  q: string;
  dynamic_attrs: Record<string, string[]>;
}

const EMPTY_FILTERS: FilterState = {
  brand: [], category_l1: [], category_l2: [], origin: [], lead_time: [],
  length_range: '', width_range: '', height_range: '', price_range: '', q: '',
  dynamic_attrs: {},
};

export default function CatalogPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [filters, setFilters] = useState<FilterState>(EMPTY_FILTERS);
  const [filterOptions, setFilterOptions] = useState<any>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const quoteId = searchParams.get('quoteId');

  // 加载筛选项聚合
  useEffect(() => {
    catalogService.getFilters().then(({ data }) => setFilterOptions(data));
  }, []);

  // 即时查询（debounce 300ms）
  useEffect(() => {
    const timer = setTimeout(() => fetchProducts(), 300);
    return () => clearTimeout(timer);
  }, [filters]);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filters.q) params.q = filters.q;
      if (filters.brand.length) params['brand[]'] = filters.brand;
      if (filters.category_l1.length) params['category_l1[]'] = filters.category_l1;
      if (filters.category_l2.length) params['category_l2[]'] = filters.category_l2;
      if (filters.origin.length) params['origin[]'] = filters.origin;
      if (filters.lead_time.length) params['lead_time[]'] = filters.lead_time;
      if (filters.length_range) params.length_range = filters.length_range;
      if (filters.width_range) params.width_range = filters.width_range;
      if (filters.height_range) params.height_range = filters.height_range;
      if (filters.price_range) params.price_range = filters.price_range;
      // 动态属性
      Object.entries(filters.dynamic_attrs).forEach(([key, vals]) => {
        if (vals && vals.length) params[`attr_${key}[]`] = vals;
      });
      const { data } = await catalogService.getCatalog(params);
      setProducts(data.results || data);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const updateFilter = (key: keyof FilterState, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => setFilters(EMPTY_FILTERS);

  // 已选条件数量
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.brand.length) count++;
    if (filters.category_l1.length) count++;
    if (filters.category_l2.length) count++;
    if (filters.origin.length) count++;
    if (filters.lead_time.length) count++;
    if (filters.length_range) count++;
    if (filters.width_range) count++;
    if (filters.height_range) count++;
    if (filters.price_range) count++;
    Object.values(filters.dynamic_attrs).forEach(vals => { if (vals && vals.length) count++; });
    return count;
  }, [filters]);

  // 可用的二级类别（根据已选一级联动）
  const availableL2 = useMemo(() => {
    if (!filterOptions?.category_l2 || !filters.category_l1.length) return [];
    const all: any[] = [];
    filters.category_l1.forEach(l1 => {
      const items = filterOptions.category_l2[l1] || [];
      all.push(...items);
    });
    return all;
  }, [filterOptions, filters.category_l1]);

  const handleProductClick = (productId: number) => {
    if (quoteId) {
      navigate(`/products/${productId}?quoteId=${quoteId}`);
    } else {
      navigate(`/products/${productId}`);
    }
  };

  return (
    <div>
      {/* 顶部：搜索 + 筛选按钮 */}
      <Space style={{ width: '100%', marginBottom: 16 }} direction="vertical">
        {quoteId && (
          <Tag color="blue" closable onClose={() => navigate('/catalog')}>
            正在为报价单 #{quoteId} 选品
          </Tag>
        )}
        <Row gutter={12} align="middle">
          <Col flex="auto">
            <Input
              prefix={<SearchOutlined />}
              placeholder="搜索产品名称、编号、材质、描述..."
              allowClear
              value={filters.q}
              onChange={e => updateFilter('q', e.target.value)}
              size="large"
            />
          </Col>
          <Col>
            <Badge count={activeFilterCount} size="small">
              <Button icon={<FilterOutlined />} size="large" onClick={() => setDrawerOpen(true)}>
                筛选
              </Button>
            </Badge>
          </Col>
          {activeFilterCount > 0 && (
            <Col>
              <Button size="large" onClick={clearFilters}>清除筛选</Button>
            </Col>
          )}
        </Row>

        {/* 多级类别快捷标签 */}
        {filterOptions?.category_l1 && (
          <Space wrap size={[8, 8]}>
            {filterOptions.category_l1.map((item: any) => (
              <Tag.CheckableTag
                key={item.value}
                checked={filters.category_l1.includes(item.value)}
                onChange={checked => {
                  const next = checked
                    ? [...filters.category_l1, item.value]
                    : filters.category_l1.filter((v: string) => v !== item.value);
                  updateFilter('category_l1', next);
                }}
              >
                {item.label}
              </Tag.CheckableTag>
            ))}
          </Space>
        )}

        {/* 二级类别（联动） */}
        {availableL2.length > 0 && (
          <Space wrap size={[8, 8]}>
            {availableL2.map((item: any) => (
              <Tag.CheckableTag
                key={item.value}
                checked={filters.category_l2.includes(item.value)}
                onChange={checked => {
                  const next = checked
                    ? [...filters.category_l2, item.value]
                    : filters.category_l2.filter((v: string) => v !== item.value);
                  updateFilter('category_l2', next);
                }}
              >
                {item.label}
              </Tag.CheckableTag>
            ))}
          </Space>
        )}

        {/* 已选条件面包屑 */}
        {activeFilterCount > 0 && (
          <Space wrap size={[4, 4]}>
            {filters.brand.map(b => (
              <Tag key={`b-${b}`} closable onClose={() => updateFilter('brand', filters.brand.filter(x => x !== b))}>
                品牌: {filterOptions?.brands?.find((x: any) => String(x.id) === b)?.name || b}
              </Tag>
            ))}
            {filters.origin.map(o => (
              <Tag key={`o-${o}`} closable onClose={() => updateFilter('origin', filters.origin.filter(x => x !== o))}>
                产地: {o === 'IMPORT' ? '进口' : '国产'}
              </Tag>
            ))}
            {filters.lead_time.map(lt => (
              <Tag key={`lt-${lt}`} closable onClose={() => updateFilter('lead_time', filters.lead_time.filter(x => x !== lt))}>
                货期: {lt}
              </Tag>
            ))}
            {filters.price_range && (
              <Tag closable onClose={() => updateFilter('price_range', '')}>价格: {filters.price_range}</Tag>
            )}
            {Object.entries(filters.dynamic_attrs).flatMap(([key, vals]) =>
              (vals || []).map(v => (
                <Tag
                  key={`attr-${key}-${v}`}
                  closable
                  onClose={() => setFilters(prev => ({
                    ...prev,
                    dynamic_attrs: {
                      ...prev.dynamic_attrs,
                      [key]: (prev.dynamic_attrs[key] || []).filter(x => x !== v),
                    },
                  }))}
                >
                  {key}: {v}
                </Tag>
              ))
            )}
          </Space>
        )}
      </Space>

      {/* 产品卡片网格 */}
      <Row gutter={[16, 16]}>
        {products.map((p: any) => (
          <Col xs={12} sm={8} md={6} lg={4} key={p.id}>
            <Card
              hoverable
              loading={loading}
              onClick={() => handleProductClick(p.id)}
              cover={
                p.cover_image ? (
                  <img
                    alt={p.name}
                    src={`/media/${p.cover_image.thumbnail_path?.medium || p.cover_image.image_path}`}
                    style={{ height: 180, objectFit: 'cover' }}
                  />
                ) : (
                  <div style={{ height: 180, background: '#252b3b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Text type="secondary">暂无图片</Text>
                  </div>
                )
              }
            >
              <Meta
                title={p.name}
                description={
                  <Space direction="vertical" size={2}>
                    <Text type="secondary">{p.code || ''}</Text>
                    <Text type="secondary">{p.brand_name || ''}</Text>
                    {p.min_price && <Text strong>¥{p.min_price} 起</Text>}
                  </Space>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 悬浮筛选面板 Drawer */}
      <Drawer
        title="筛选条件"
        placement="right"
        width={360}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        extra={<Button onClick={clearFilters}>重置</Button>}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 品牌 */}
          {filterOptions?.brands && (
            <div>
              <Title level={5}>品牌</Title>
              <Checkbox.Group
                value={filters.brand}
                onChange={v => updateFilter('brand', v)}
                options={filterOptions.brands.map((b: any) => ({ label: b.name, value: String(b.id) }))}
              />
            </div>
          )}

          {/* 产地 */}
          <div>
            <Title level={5}>产地</Title>
            <Checkbox.Group
              value={filters.origin}
              onChange={v => updateFilter('origin', v)}
              options={filterOptions?.origins || []}
            />
          </div>

          {/* 货期 */}
          <div>
            <Title level={5}>货期</Title>
            <Checkbox.Group
              value={filters.lead_time}
              onChange={v => updateFilter('lead_time', v)}
              options={filterOptions?.lead_times || []}
            />
          </div>

          {/* 价格区间 */}
          {filterOptions?.mece_ranges?.price && (
            <div>
              <Title level={5}>价格区间</Title>
              <Select
                allowClear
                placeholder="选择价格区间"
                style={{ width: '100%' }}
                value={filters.price_range || undefined}
                onChange={v => updateFilter('price_range', v || '')}
                options={filterOptions.mece_ranges.price}
              />
            </div>
          )}

          {/* 长度区间 */}
          {filterOptions?.mece_ranges?.length_mm && (
            <div>
              <Title level={5}>长度 (mm)</Title>
              <Select
                allowClear
                placeholder="选择长度区间"
                style={{ width: '100%' }}
                value={filters.length_range || undefined}
                onChange={v => updateFilter('length_range', v || '')}
                options={filterOptions.mece_ranges.length_mm}
              />
            </div>
          )}

          {/* 宽度区间 */}
          {filterOptions?.mece_ranges?.width_mm && (
            <div>
              <Title level={5}>宽度 (mm)</Title>
              <Select
                allowClear
                placeholder="选择宽度区间"
                style={{ width: '100%' }}
                value={filters.width_range || undefined}
                onChange={v => updateFilter('width_range', v || '')}
                options={filterOptions.mece_ranges.width_mm}
              />
            </div>
          )}

          {/* 高度区间 */}
          {filterOptions?.mece_ranges?.height_mm && (
            <div>
              <Title level={5}>高度 (mm)</Title>
              <Select
                allowClear
                placeholder="选择高度区间"
                style={{ width: '100%' }}
                value={filters.height_range || undefined}
                onChange={v => updateFilter('height_range', v || '')}
                options={filterOptions.mece_ranges.height_mm}
              />
            </div>
          )}

          {/* 动态属性 */}
          {filterOptions?.dynamic_attributes?.map((attr: any) => (
            <div key={attr.dimension_key}>
              <Title level={5}>{attr.dimension_label}</Title>
              <Checkbox.Group
                value={filters.dynamic_attrs[attr.dimension_key] || []}
                onChange={(vals) => setFilters(prev => ({
                  ...prev,
                  dynamic_attrs: { ...prev.dynamic_attrs, [attr.dimension_key]: vals as string[] },
                }))}
                options={attr.options.map((o: string) => ({ label: o, value: o }))}
              />
            </div>
          ))}
        </Space>
      </Drawer>
    </div>
  );
}
