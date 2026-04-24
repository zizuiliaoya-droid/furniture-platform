import { useEffect, useState } from 'react';
import { Button, Card, Form, Input, message, Modal, Select, Space, Tree, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { productService } from '../../services/productService';

const { Title } = Typography;

export default function CategoryManagementPage() {
  const [dimension, setDimension] = useState('TYPE');
  const [treeData, setTreeData] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchTree = async () => {
    const { data } = await productService.getCategoryTree(dimension);
    setTreeData(convertToTreeData(data));
  };

  useEffect(() => { fetchTree(); }, [dimension]);

  const convertToTreeData = (nodes: any[]): any[] =>
    nodes.map((n) => ({ key: n.id, title: n.name, children: convertToTreeData(n.children || []) }));

  const handleCreate = async (values: any) => {
    await productService.createCategory({ ...values, dimension });
    message.success('分类创建成功');
    setModalOpen(false);
    form.resetFields();
    fetchTree();
  };

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>分类管理</Title>
        <Space>
          <Select value={dimension} onChange={setDimension} style={{ width: 120 }}
            options={[{ value: 'TYPE', label: '按类型' }, { value: 'SPACE', label: '按空间' }, { value: 'ORIGIN', label: '按产地' }]} />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建分类</Button>
        </Space>
      </Space>
      <Card><Tree treeData={treeData} defaultExpandAll /></Card>
      <Modal title="新建分类" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="分类名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="parent" label="父分类（留空为顶级）"><Input type="number" /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
