import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, message, Space, Table, Tag, Typography } from 'antd';
import { CopyOutlined, EditOutlined, FilePdfOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { quoteService } from '../../services/quoteService';

const { Title } = Typography;

export default function QuoteDetailPage() {
  const { id } = useParams();
  const [quote, setQuote] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (id) quoteService.getQuote(Number(id)).then(({ data }) => setQuote(data));
  }, [id]);

  const handleDuplicate = async () => {
    const { data } = await quoteService.duplicateQuote(Number(id));
    message.success('复制成功');
    navigate(`/quotes/${data.id}`);
  };

  const handleExportPdf = async () => {
    const { data } = await quoteService.exportPdf(Number(id));
    const url = URL.createObjectURL(data);
    const a = document.createElement('a');
    a.href = url; a.download = `quote_${id}.pdf`; a.click();
    URL.revokeObjectURL(url);
  };

  if (!quote) return null;

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>{quote.title}</Title>
        <Space>
          <Button icon={<EditOutlined />} onClick={() => navigate(`/quotes/${id}/edit`)}>编辑</Button>
          <Button icon={<CopyOutlined />} onClick={handleDuplicate}>复制</Button>
          <Button icon={<FilePdfOutlined />} onClick={handleExportPdf}>导出 PDF</Button>
        </Space>
      </Space>
      <Card>
        <Descriptions column={2}>
          <Descriptions.Item label="客户">{quote.customer_name}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag>{quote.status}</Tag></Descriptions.Item>
          <Descriptions.Item label="总金额">¥{quote.total_amount}</Descriptions.Item>
          <Descriptions.Item label="备注">{quote.notes || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="报价明细" style={{ marginTop: 16 }}>
        <Table dataSource={quote.items} rowKey="id" pagination={false} columns={[
          { title: '产品', dataIndex: 'product_name' },
          { title: '配置', dataIndex: 'config_name' },
          { title: '单价', dataIndex: 'unit_price', render: (v: number) => `¥${v}` },
          { title: '数量', dataIndex: 'quantity' },
          { title: '折扣', dataIndex: 'discount', render: (v: number) => `${v}%` },
          { title: '小计', dataIndex: 'subtotal', render: (v: number) => `¥${v}` },
        ]} />
      </Card>
    </div>
  );
}
