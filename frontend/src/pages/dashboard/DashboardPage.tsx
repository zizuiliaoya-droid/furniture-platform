import { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Typography } from 'antd';
import { ShoppingOutlined, BookOutlined, DollarOutlined, FileTextOutlined } from '@ant-design/icons';
import { dashboardService } from '../../services/dashboardService';

const { Title } = Typography;

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    dashboardService.getStats().then(({ data }) => setStats(data));
  }, []);

  if (!stats) return null;

  const cards = [
    { title: '产品总数', value: stats.totals.product_count, icon: <ShoppingOutlined />, color: '#6b8acd' },
    { title: '案例总数', value: stats.totals.case_count, icon: <BookOutlined />, color: '#6dae82' },
    { title: '报价单总数', value: stats.totals.quote_count, icon: <DollarOutlined />, color: '#d4a44a' },
    { title: '文档总数', value: stats.totals.document_count, icon: <FileTextOutlined />, color: '#5fa8d3' },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>仪表盘</Title>
      <Row gutter={[16, 16]}>
        {cards.map((c) => (
          <Col xs={12} sm={6} key={c.title}>
            <Card hoverable>
              <Statistic title={c.title} value={c.value} prefix={c.icon} valueStyle={{ color: c.color }} />
            </Card>
          </Col>
        ))}
      </Row>
      <Card title="本月新增" style={{ marginTop: 16 }}>
        <Row gutter={16}>
          <Col span={8}><Statistic title="新增产品" value={stats.monthly.new_products} /></Col>
          <Col span={8}><Statistic title="新增案例" value={stats.monthly.new_cases} /></Col>
          <Col span={8}><Statistic title="新增报价" value={stats.monthly.new_quotes} /></Col>
        </Row>
      </Card>
      <Card title="最近活动" style={{ marginTop: 16 }}>
        <Table dataSource={stats.recent_activities} rowKey="id" pagination={false} size="small"
          columns={[
            { title: '报价单', dataIndex: 'title' },
            { title: '客户', dataIndex: 'customer_name' },
            { title: '状态', dataIndex: 'status' },
            { title: '更新时间', dataIndex: 'updated_at', render: (v: string) => v?.slice(0, 10) },
          ]} />
      </Card>
    </div>
  );
}
