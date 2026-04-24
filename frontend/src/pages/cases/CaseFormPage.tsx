import { useEffect, useState } from 'react';
import { Button, Form, Input, message, Select, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { caseService } from '../../services/caseService';

const { Title } = Typography;

export default function CaseFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (isEdit) caseService.getCase(Number(id)).then(({ data }) => form.setFieldsValue(data));
  }, [id]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (isEdit) await caseService.updateCase(Number(id), values);
      else await caseService.createCase(values);
      message.success(isEdit ? '案例更新成功' : '案例创建成功');
      navigate('/cases');
    } catch { message.error('操作失败'); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <Title level={4}>{isEdit ? '编辑案例' : '新建案例'}</Title>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item name="title" label="案例标题" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="industry" label="行业分类" rules={[{ required: true }]}>
          <Select options={[
            { value: 'TECH', label: '科技/互联网' }, { value: 'FINANCE', label: '金融/保险/财税' },
            { value: 'REALESTATE', label: '地产/建筑/设计院' }, { value: 'EDUCATION', label: '教育培训' },
            { value: 'MEDICAL', label: '医疗/大健康' }, { value: 'MEDIA', label: '广告/文创/传媒' },
            { value: 'MANUFACTURE', label: '制造/实业/工厂' }, { value: 'GOVERNMENT', label: '政府/国企/事业单位' },
            { value: 'OTHER', label: '其他' },
          ]} />
        </Form.Item>
        <Form.Item name="description" label="项目描述"><Input.TextArea rows={4} /></Form.Item>
        <Form.Item><Button type="primary" htmlType="submit" loading={loading}>{isEdit ? '保存' : '创建'}</Button></Form.Item>
      </Form>
    </div>
  );
}
