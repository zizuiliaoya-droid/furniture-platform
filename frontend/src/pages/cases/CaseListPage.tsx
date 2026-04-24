import { useEffect, useState } from 'react';
import { Button, Select, Space, Table, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;
const INDUSTRIES = [
  { value: 'TECH', label: '科技/互联网' }, { value: 'FINANCE', label: '金融/保险/财税' },
  { value: 'REALESTATE', label: '地产/建筑/设计院' }, { value: 'EDUCATION', label: '教育培训' },
  { value: 'MEDICAL', label: '医疗/大健康' }, { value: 'MEDIA', label: '广告/文创/传媒' },
  { value: 'MANUFACTURE', label: '制造/实业/工厂' }, { value: 'GOVERNMENT', label: '政府/国企/事业单位' },
  { value: 'OTHER', label: '其他' },
];

export default function CaseListPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  const fetchCases = async (params?: any) => {
    setLoading(true);
    try { const { data } = await caseService.getCases(params); setCases(data.results || data); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchCases(); }, []);

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>客户案例</Title>
        {isAdmin && <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/cases/new')}>新建案例</Button>}
      </Space>
      <Select placeholder="行业筛选" allowClear style={{ width: 200, marginBottom: 16 }} options={INDUSTRIES}
        onChange={(v) => fetchCases(v ? { industry: v } : {})} />
      <Table dataSource={cases} rowKey="id" loading={loading}
        onRow={(r) => ({ onClick: () => navigate(`/cases/${r.id}`), style: { cursor: 'pointer' } })}
        columns={[
          { title: '标题', dataIndex: 'title' },
          { title: '行业', dataIndex: 'industry', render: (v: string) => INDUSTRIES.find((i) => i.value === v)?.label },
          { title: '创建时间', dataIndex: 'created_at', render: (v: string) => v?.slice(0, 10) },
        ]} />
    </div>
  );
}
