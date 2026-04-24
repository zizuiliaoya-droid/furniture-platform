import { useEffect, useState } from 'react';
import { Button, Form, Input, message, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { quoteService } from '../../services/quoteService';

const { Title } = Typography;

export default function QuoteFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (isEdit) quoteService.getQuote(Number(id)).then(({ data }) => form.setFieldsValue(data));
  }, [id]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (isEdit) await quoteService.updateQuote(Number(id), values);
      else await quoteService.createQuote(values);
      message.success(isEdit ? '报价单更新成功' : '报价单创建成功');
      navigate('/quotes');
    } catch { message.error('操作失败'); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <Title level={4}>{isEdit ? '编辑报价单' : '新建报价单'}</Title>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item name="title" label="报价单标题" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="customer_name" label="客户名称" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="notes" label="备注"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="terms" label="条款"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item><Button type="primary" htmlType="submit" loading={loading}>{isEdit ? '保存' : '创建'}</Button></Form.Item>
      </Form>
    </div>
  );
}
