import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, Image, Space, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;

export default function CaseDetailPage() {
  const { id } = useParams();
  const [caseData, setCaseData] = useState<any>(null);
  const navigate = useNavigate();
  const isAdmin = useAuthStore((s) => s.user?.role === 'ADMIN');

  useEffect(() => {
    if (id) caseService.getCase(Number(id)).then(({ data }) => setCaseData(data));
  }, [id]);

  if (!caseData) return null;

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>{caseData.title}</Title>
        {isAdmin && <Button icon={<EditOutlined />} onClick={() => navigate(`/cases/${id}/edit`)}>编辑</Button>}
      </Space>
      <Card>
        <Descriptions column={2}>
          <Descriptions.Item label="行业">{caseData.industry}</Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>{caseData.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>
      {caseData.images?.length > 0 && (
        <Card title="案例图片" style={{ marginTop: 16 }}>
          <Image.PreviewGroup>
            <Space wrap>{caseData.images.map((img: any) => (
              <Image key={img.id} width={120} height={120} style={{ objectFit: 'cover' }}
                src={`/media/${img.thumbnail_path?.medium || img.image_path}`} />
            ))}</Space>
          </Image.PreviewGroup>
        </Card>
      )}
    </div>
  );
}
