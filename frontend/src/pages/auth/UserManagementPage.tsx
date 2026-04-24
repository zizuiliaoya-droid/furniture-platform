import { useEffect, useState } from 'react';
import { Button, Form, Input, message, Modal, Select, Space, Switch, Table, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { authService } from '../../services/authService';

const { Title } = Typography;

export default function UserManagementPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const { data } = await authService.getUsers();
      setUsers(data.results || data);
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async (values: any) => {
    await authService.createUser(values);
    message.success('用户创建成功');
    setModalOpen(false);
    form.resetFields();
    fetchUsers();
  };

  const handleToggle = async (id: number) => {
    await authService.toggleUserStatus(id);
    fetchUsers();
  };

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>用户管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>创建用户</Button>
      </Space>
      <Table dataSource={users} rowKey="id" loading={loading} columns={[
        { title: '用户名', dataIndex: 'username' },
        { title: '显示名称', dataIndex: 'display_name' },
        { title: '角色', dataIndex: 'role', render: (v: string) => v === 'ADMIN' ? '管理员' : '员工' },
        { title: '状态', dataIndex: 'is_active', render: (v: boolean, r: any) => <Switch checked={v} onChange={() => handleToggle(r.id)} /> },
      ]} />
      <Modal title="创建用户" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}><Input.Password /></Form.Item>
          <Form.Item name="display_name" label="显示名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="role" label="角色" initialValue="STAFF">
            <Select options={[{ value: 'ADMIN', label: '管理员' }, { value: 'STAFF', label: '员工' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
