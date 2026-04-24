import { useEffect, useState } from 'react';
import { Button, message, Popconfirm, Space, Table, Tag, Typography } from 'antd';
import { CopyOutlined, DeleteOutlined } from '@ant-design/icons';
import { shareService } from '../../services/shareService';

const { Title } = Typography;

export default function ShareManagementPage() {
  const [shares, setShares] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchShares = async () => {
    setLoading(true);
    try { const { data } = await shareService.getShares(); setShares(data.results || data); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchShares(); }, []);

  const copyLink = (token: string) => {
    navigator.clipboard.writeText(`${window.location.origin}/s/${token}`);
    message.success('链接已复制');
  };

  const handleDelete = async (id: number) => {
    await shareService.deleteShare(id);
    message.success('已删除');
    fetchShares();
  };

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>分享管理</Title>
      <Table dataSource={shares} rowKey="id" loading={loading} columns={[
        { title: '标题', dataIndex: 'title' },
        { title: '类型', dataIndex: 'content_type' },
        { title: '状态', dataIndex: 'is_active', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? '启用' : '禁用'}</Tag> },
        { title: '访问次数', dataIndex: 'access_count' },
        { title: '创建时间', dataIndex: 'created_at', render: (v: string) => v?.slice(0, 10) },
        { title: '操作', render: (_: any, r: any) => (
          <Space>
            <Button size="small" icon={<CopyOutlined />} onClick={() => copyLink(r.token)}>复制链接</Button>
            <Popconfirm title="确定删除？" onConfirm={() => handleDelete(r.id)}>
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Space>
        )},
      ]} />
    </div>
  );
}
