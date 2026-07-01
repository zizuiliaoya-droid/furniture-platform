import { useEffect, useState } from 'react';
import {
  Button, Card, Descriptions, Image, InputNumber, message, Popconfirm,
  Select, Space, Table, Tag, Tooltip, Typography,
} from 'antd';
import {
  CopyOutlined, DeleteOutlined, EditOutlined, FilePdfOutlined,
  PlusOutlined, ShoppingCartOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { quoteService } from '../../services/quoteService';

const { Title, Text } = Typography;

// 状态流转（与后端 VALID_TRANSITIONS 保持一致）
const VALID_TRANSITIONS: Record<string, string[]> = {
  DRAFT: ['SENT', 'CANCELLED'],
  SENT: ['CONFIRMED', 'CANCELLED'],
  CONFIRMED: ['CANCELLED'],
  CANCELLED: [],
};

export default function QuoteDetailPage() {
  const { id } = useParams();
  const [quote, setQuote] = useState<any>(null);
  const [editingItem, setEditingItem] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<any>({});
  const navigate = useNavigate();

  const loadQuote = () => {
    if (id) quoteService.getQuote(Number(id)).then(({ data }) => setQuote(data));
  };

  useEffect(() => { loadQuote(); }, [id]);

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

  const startEdit = (item: any) => {
    setEditingItem(item.id);
    setEditValues({ quantity: item.quantity, discount: item.discount });
  };

  const saveEdit = async (itemId: number) => {
    try {
      await quoteService.updateItem(itemId, editValues);
      message.success('已更新');
      setEditingItem(null);
      loadQuote();
    } catch { message.error('更新失败'); }
  };

  const deleteItem = async (itemId: number) => {
    try {
      await quoteService.deleteItem(itemId);
      message.success('已删除');
      loadQuote();
    } catch { message.error('删除失败'); }
  };

  const handleStatusChange = async (newStatus: string) => {
    try {
      await quoteService.updateQuote(Number(id), { status: newStatus });
      message.success('状态已更新');
      loadQuote();
    } catch (err: any) {
      message.error(err.response?.data?.detail || err.response?.data?.[0] || '状态更新失败');
    }
  };

  if (!quote) return null;

  const STATUS_COLOR: Record<string, string> = {
    DRAFT: 'default', SENT: 'processing', CONFIRMED: 'success', CANCELLED: 'error',
  };
  const STATUS_LABEL: Record<string, string> = {
    DRAFT: '草稿', SENT: '已发送', CONFIRMED: '已确认', CANCELLED: '已取消',
  };

  const columns = [
    {
      title: '图片',
      dataIndex: 'image_url',
      width: 70,
      render: (url: string) => url ? (
        <Image width={50} height={50} style={{ objectFit: 'cover', borderRadius: 4 }}
          src={`/media/${url}`} preview={{ mask: '预览' }} />
      ) : <Text type="secondary">-</Text>,
    },
    { title: '产品', dataIndex: 'product_name', ellipsis: true },
    {
      title: '配置',
      dataIndex: 'config_name',
      ellipsis: true,
      render: (text: string, record: any) => (
        <Tooltip title={record.config_attributes ? JSON.stringify(record.config_attributes) : ''}>
          <Text>{text || '-'}</Text>
        </Tooltip>
      ),
    },
    { title: '单价', dataIndex: 'unit_price', width: 90, render: (v: number) => `¥${v}` },
    {
      title: '数量',
      dataIndex: 'quantity',
      width: 100,
      render: (v: number, record: any) => editingItem === record.id ? (
        <InputNumber size="small" min={1} value={editValues.quantity}
          onChange={val => setEditValues((prev: any) => ({ ...prev, quantity: val }))} />
      ) : v,
    },
    {
      title: '折扣',
      dataIndex: 'discount',
      width: 100,
      render: (v: number, record: any) => editingItem === record.id ? (
        <InputNumber size="small" min={0} max={100} value={editValues.discount} suffix="%"
          onChange={val => setEditValues((prev: any) => ({ ...prev, discount: val }))} />
      ) : `${v}%`,
    },
    { title: '小计', dataIndex: 'subtotal', width: 100, render: (v: number) => `¥${v}` },
    {
      title: '操作',
      width: 120,
      render: (_: any, record: any) => editingItem === record.id ? (
        <Space size="small">
          <Button size="small" type="primary" onClick={() => saveEdit(record.id)}>保存</Button>
          <Button size="small" onClick={() => setEditingItem(null)}>取消</Button>
        </Space>
      ) : (
        <Space size="small">
          <Button size="small" icon={<EditOutlined />} onClick={() => startEdit(record)} />
          <Popconfirm title="确认删除？" onConfirm={() => deleteItem(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

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
          <Descriptions.Item label="状态">
            <Space>
              <Tag color={STATUS_COLOR[quote.status]}>{STATUS_LABEL[quote.status] || quote.status}</Tag>
              {(VALID_TRANSITIONS[quote.status] || []).length > 0 && (
                <Select
                  size="small"
                  placeholder="变更状态"
                  style={{ width: 120 }}
                  value={undefined}
                  onChange={handleStatusChange}
                  options={(VALID_TRANSITIONS[quote.status] || []).map((s) => ({
                    value: s, label: STATUS_LABEL[s] || s,
                  }))}
                />
              )}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="总金额">
            <Text strong style={{ fontSize: 18 }}>¥{quote.total_amount}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">{quote.created_at?.slice(0, 10)}</Descriptions.Item>
          {quote.notes && <Descriptions.Item label="备注" span={2}>{quote.notes}</Descriptions.Item>}
        </Descriptions>
      </Card>

      <Card
        title="报价明细"
        style={{ marginTop: 16 }}
        extra={
          <Button type="primary" icon={<PlusOutlined />}
            onClick={() => navigate(`/catalog?quoteId=${id}`)}>
            新增明细
          </Button>
        }
      >
        <Table
          dataSource={quote.items}
          rowKey="id"
          pagination={false}
          columns={columns}
          size="small"
          scroll={{ x: 800 }}
          summary={() => (
            <Table.Summary.Row>
              <Table.Summary.Cell index={0} colSpan={6} align="right">
                <Text strong>合计</Text>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={1}>
                <Text strong>¥{quote.total_amount}</Text>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={2} />
            </Table.Summary.Row>
          )}
        />
      </Card>
    </div>
  );
}
