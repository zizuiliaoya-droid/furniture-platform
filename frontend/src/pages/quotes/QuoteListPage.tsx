import { useEffect, useState } from 'react';
import { Button, Input, Select, Space, Table, Tag, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { quoteService } from '../../services/quoteService';

const { Title } = Typography;
const STATUS_MAP: Record<string, { label: string; color: string }> = {
  DRAFT: { label: '草稿', color: 'default' }, SENT: { label: '已发送', color: 'blue' },
  CONFIRMED: { label: '已确认', color: 'green' }, CANCELLED: { label: '已取消', color: 'red' },
};

export default function QuoteListPage() {
  const [quotes, setQuotes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const fetchQuotes = async (params?: any) => {
    setLoading(true);
    try { const { data } = await quoteService.getQuotes(params); setQuotes(data.results || data); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchQuotes(); }, []);

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>报价方案</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/quotes/new')}>新建报价单</Button>
      </Space>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search placeholder="搜索标题/客户..." allowClear onSearch={(v) => fetchQuotes({ search: v })} style={{ width: 250 }} />
        <Select placeholder="状态" allowClear style={{ width: 120 }} onChange={(v) => fetchQuotes(v ? { status: v } : {})}
          options={Object.entries(STATUS_MAP).map(([k, v]) => ({ value: k, label: v.label }))} />
      </Space>
      <Table dataSource={quotes} rowKey="id" loading={loading}
        onRow={(r) => ({ onClick: () => navigate(`/quotes/${r.id}`), style: { cursor: 'pointer' } })}
        columns={[
          { title: '标题', dataIndex: 'title' },
          { title: '客户', dataIndex: 'customer_name' },
          { title: '状态', dataIndex: 'status', render: (v: string) => <Tag color={STATUS_MAP[v]?.color}>{STATUS_MAP[v]?.label}</Tag> },
          { title: '总金额', dataIndex: 'total_amount', render: (v: number) => `¥${v}` },
          { title: '更新时间', dataIndex: 'updated_at', render: (v: string) => v?.slice(0, 10) },
        ]} />
    </div>
  );
}
