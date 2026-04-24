import { useEffect, useState } from 'react';
import { Button, Form, Input, InputNumber, message, Select, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { productService } from '../../services/productService';

const { Title } = Typography;
const { TextArea } = Input;

export default function ProductFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    productService.getCategories().then(({ data }) => setCategories(data.results || data));
    if (isEdit) {
      productService.getProduct(Number(id)).then(({ data }) => form.setFieldsValue(data));
    }
  }, [id]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (isEdit) {
        await productService.updateProduct(Number(id), values);
        message.success('产品更新成功');
      } else {
        await productService.createProduct(values);
        message.success('产品创建成功');
      }
      navigate('/products');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    } finally { setLoading(false); }
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <Title level={4}>{isEdit ? '编辑产品' : '新建产品'}</Title>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item name="name" label="产品名称" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="code" label="产品编号"><Input /></Form.Item>
        <Form.Item name="category" label="主分类" rules={[{ required: true }]}>
          <Select options={categories.map((c: any) => ({ value: c.id, label: c.name }))} />
        </Form.Item>
        <Form.Item name="origin" label="产地" rules={[{ required: true }]}>
          <Select options={[{ value: 'IMPORT', label: '进口' }, { value: 'DOMESTIC', label: '国产' }, { value: 'CUSTOM', label: '定制' }]} />
        </Form.Item>
        <Form.Item name="min_price" label="最低售价"><InputNumber style={{ width: '100%' }} min={0} precision={2} /></Form.Item>
        <Form.Item name="description" label="描述"><TextArea rows={4} /></Form.Item>
        <Form.Item><Button type="primary" htmlType="submit" loading={loading}>{isEdit ? '保存' : '创建'}</Button></Form.Item>
      </Form>
    </div>
  );
}
