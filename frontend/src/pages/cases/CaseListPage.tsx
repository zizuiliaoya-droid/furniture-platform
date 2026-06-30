import { useEffect, useState } from 'react';
import { Button, message, Popconfirm, Space, Table, Tag, Typography } from 'antd';
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;

const INDUSTRIES = [
  { value: 'TECH_OFFICE', label: '科技/互联网办公' },
  { value: 'FINANCE_OFFICE', label: '金融/保险/财税办公' },
  { value: 'REALESTATE_OFFICE', label: '地产/建筑/设计院' },
  { value: 'EDUCATION_OFFICE', label: '教育培训办公' },
  { value: 'MEDICAL_OFFICE', label: '医疗/大健康办公' },
  { value: 'MEDIA_OFFICE', label: '广告/文创/传媒办公' },
  { value: 'MANUFACTURE_OFFICE', label: '制造/实业/工厂办公' },
  { value: 'GOVERNMENT_OFFICE', label: '政府/国企/事业单位' },
  { value: 'OTHER', label: '其他' },
];

export default function CaseListPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndustry, setSelectedIndustry] = useState<string | null>(null);
  const navigate = useNavigate();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  const fetchCases = async (params?: any) => {
    setLoading(true);
    try { const { data } = await caseService.getCases(params); setCases(data.results || data); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchCases(); }, []);

  const handleIndustryClick = (value: string) => {
    if (selectedIndustry === value) {
      setSelectedIndustry(null);
      fetchCases();
    } else {
      setSelectedIndustry(value);
      fetchCases({ industry: value });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await caseService.deleteCase(id);
      message.success('已删除');
      fetchCases(selectedIndustry ? { industry: selectedIndustry } : undefined);
    } catch {
      message.error('删除失败');
    }
  };

  const columns: any[] = [
    { title: '标题', dataIndex: 'title', sorter: (a: any, b: any) => a.title.localeCompare(b.title) },
    { title: '行业', dataIndex: 'industry', render: (v: string) => INDUSTRIES.find((i) => i.value === v)?.label || v },
    { title: '创建时间', dataIndex: 'created_at', render: (v: string) => v?.slice(0, 10) },
  ];

  if (isAdmin) {
    columns.push({
      title: '操作',
      width: 120,
      render: (_: any, record: any) => (
        <Space size="small" onClick={(e) => e.stopPropagation()}>
          <Button size="small" icon={<EditOutlined />} onClick={() => navigate(`/cases/${record.id}/edit`)} />
          <Popconfirm
            title="确认删除该案例？"
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
            onConfirm={() => handleDelete(record.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    });
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>客户案例</Title>
        {isAdmin && <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/cases/new')}>新建案例</Button>}
      </Space>

      {/* 行业树筛选（标签式） */}
      <Space wrap size={[8, 8]} style={{ marginBottom: 16 }}>
        {INDUSTRIES.map(ind => (
          <Tag.CheckableTag
            key={ind.value}
            checked={selectedIndustry === ind.value}
            onChange={() => handleIndustryClick(ind.value)}
          >
            {ind.label}
          </Tag.CheckableTag>
        ))}
      </Space>

      <Table
        dataSource={cases}
        rowKey="id"
        loading={loading}
        onRow={(r) => ({ onClick: () => navigate(`/cases/${r.id}`), style: { cursor: 'pointer' } })}
        columns={columns}
      />
    </div>
  );
}
