import { useEffect, useMemo, useState } from 'react';
import { Button, Form, Input, message, Modal, Select, Space, Switch, Table, Typography } from 'antd';
import { EditOutlined, KeyOutlined, PlusOutlined } from '@ant-design/icons';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;
const ROLE_LABELS: Record<string, string> = {
  SUPER_ADMIN: '超级管理员', ADMIN: '管理员', DEPT_MANAGER: '部门主管', STAFF: '员工',
};

function apiError(err: any, fallback: string) {
  const data = err.response?.data;
  if (typeof data?.detail === 'string') return data.detail;
  if (data && typeof data === 'object') {
    const first = Object.values(data).flat()[0];
    if (typeof first === 'string') return first;
  }
  return fallback;
}

export default function UserManagementPage() {
  const currentUser = useAuthStore((state) => state.user);
  const [users, setUsers] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [resetUser, setResetUser] = useState<any | null>(null);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [userResponse, departmentResponse] = await Promise.all([
        authService.getUsers(), authService.getDepartments(),
      ]);
      setUsers(userResponse.data.results || userResponse.data);
      setDepartments(departmentResponse.data.results || departmentResponse.data);
    } catch (err: any) {
      message.error(apiError(err, '用户数据加载失败'));
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const departmentMap = useMemo(
    () => Object.fromEntries(departments.map((department) => [department.id, department.name])),
    [departments],
  );

  const canManage = (target: any) => {
    if (!currentUser?.is_admin) return false;
    if (target?.role === 'SUPER_ADMIN' && currentUser.role !== 'SUPER_ADMIN') return false;
    return true;
  };

  const openCreate = () => {
    setEditingUser(null);
    form.resetFields();
    form.setFieldsValue({ role: 'STAFF' });
    setModalOpen(true);
  };

  const openEdit = (user: any) => {
    setEditingUser(user);
    form.setFieldsValue({
      display_name: user.display_name,
      role: user.role,
      department: user.department,
    });
    setModalOpen(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        await authService.updateUser(editingUser.id, values);
        message.success('用户已更新');
      } else {
        await authService.createUser(values);
        message.success('用户创建成功');
      }
      setModalOpen(false);
      form.resetFields();
      fetchData();
    } catch (err: any) {
      message.error(apiError(err, editingUser ? '用户更新失败' : '用户创建失败'));
    }
  };

  const handleToggle = async (user: any) => {
    try {
      await authService.toggleUserStatus(user.id);
      message.success(user.is_active ? '用户已停用' : '用户已启用');
      fetchData();
    } catch (err: any) { message.error(apiError(err, '状态修改失败')); }
  };

  const handleResetPassword = async (values: any) => {
    if (!resetUser) return;
    try {
      await authService.resetPassword(resetUser.id, values.new_password);
      message.success('密码重置成功');
      setResetUser(null);
      passwordForm.resetFields();
    } catch (err: any) { message.error(apiError(err, '密码重置失败')); }
  };

  const roleOptions = [
    ...(currentUser?.role === 'SUPER_ADMIN' ? [{ value: 'SUPER_ADMIN', label: '超级管理员' }] : []),
    { value: 'ADMIN', label: '管理员' },
    { value: 'DEPT_MANAGER', label: '部门主管' },
    { value: 'STAFF', label: '员工' },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>用户管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>创建用户</Button>
      </Space>
      <Table dataSource={users} rowKey="id" loading={loading} columns={[
        { title: '用户名', dataIndex: 'username' },
        { title: '显示名称', dataIndex: 'display_name' },
        { title: '角色', dataIndex: 'role', render: (value: string) => ROLE_LABELS[value] || value },
        { title: '部门', dataIndex: 'department', render: (value: number | null) => value ? (departmentMap[value] || `部门 #${value}`) : '-' },
        {
          title: '状态', dataIndex: 'is_active',
          render: (value: boolean, user: any) => (
            <Switch checked={value} disabled={!canManage(user) || user.id === currentUser?.id}
              onChange={() => handleToggle(user)} />
          ),
        },
        {
          title: '操作', width: 150,
          render: (_: any, user: any) => (
            <Space size="small">
              <Button size="small" icon={<EditOutlined />} disabled={!canManage(user)} onClick={() => openEdit(user)} />
              <Button size="small" icon={<KeyOutlined />} disabled={!canManage(user)} onClick={() => setResetUser(user)}>重置密码</Button>
            </Space>
          ),
        },
      ]} />

      <Modal title={editingUser ? '编辑用户' : '创建用户'} open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          {!editingUser && (
            <>
              <Form.Item name="username" label="用户名" rules={[{ required: true }]}><Input /></Form.Item>
              <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}><Input.Password /></Form.Item>
            </>
          )}
          <Form.Item name="display_name" label="显示名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Select disabled={!!editingUser && editingUser.id === currentUser?.id} options={roleOptions} />
          </Form.Item>
          <Form.Item name="department" label="部门">
            <Select allowClear options={departments.map((department) => ({ value: department.id, label: department.name }))} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title={`重置密码：${resetUser?.display_name || resetUser?.username || ''}`}
        open={!!resetUser} onCancel={() => setResetUser(null)} onOk={() => passwordForm.submit()}>
        <Form form={passwordForm} layout="vertical" onFinish={handleResetPassword}>
          <Form.Item name="new_password" label="新密码" rules={[{ required: true, min: 6, message: '密码至少 6 位' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="confirm_password" label="确认新密码" dependencies={['new_password']} rules={[
            { required: true },
            ({ getFieldValue }) => ({
              validator(_, value) {
                return !value || getFieldValue('new_password') === value
                  ? Promise.resolve() : Promise.reject(new Error('两次输入的密码不一致'));
              },
            }),
          ]}>
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
