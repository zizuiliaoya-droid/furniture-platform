import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, Image, Space, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { caseService } from '../../services/caseService';
import { useAuthStore } from '../../store/authStore';

const { Title, Text } = Typography;

const INDUSTRY_MAP: Record<string, string> = {
  TECH_OFFICE: '科技/互联网办公', FINANCE_OFFICE: '金融/保险/财税办公',
  REALESTATE_OFFICE: '地产/建筑/设计院', EDUCATION_OFFICE: '教育培训办公',
  MEDICAL_OFFICE: '医疗/大健康办公', MEDIA_OFFICE: '广告/文创/传媒办公',
  MANUFACTURE_OFFICE: '制造/实业/工厂办公', GOVERNMENT_OFFICE: '政府/国企/事业单位',
  OTHER: '其他',
};

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
          <Descriptions.Item label="行业">{INDUSTRY_MAP[caseData.industry] || caseData.industry}</Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>{caseData.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 案例图片：平铺加载 + 懒加载 + 缩略图 */}
      {caseData.images?.length > 0 && (
        <Card title={`案例图片 (${caseData.images.length})`} style={{ marginTop: 16 }}>
          <Image.PreviewGroup>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
              {caseData.images.map((img: any) => (
                <Image
                  key={img.id}
                  width={200}
                  height={150}
                  style={{ objectFit: 'cover', borderRadius: 4 }}
                  src={`/media/${img.thumbnail_path?.medium || img.image_path}`}
                  preview={{ src: `/media/${img.image_path}` }}
                  loading="lazy"
                  placeholder={
                    <div style={{ width: 200, height: 150, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Text type="secondary">加载中...</Text>
                    </div>
                  }
                />
              ))}
            </div>
          </Image.PreviewGroup>
        </Card>
      )}

      {/* 关联产品 */}
      {caseData.products?.length > 0 && (
        <Card title="关联产品" style={{ marginTop: 16 }}>
          <Space wrap>
            {caseData.products.map((p: any) => (
              <Button key={p.id} type="link" onClick={() => navigate(`/products/${p.id}`)}>
                {p.name}
              </Button>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
}
