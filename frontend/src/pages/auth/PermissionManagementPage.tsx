import { useEffect, useState } from 'react';
import { Button, Card, Checkbox, message, Space, Table, Tabs, Tag, Typography } from 'antd';
import { authService } from '../../services/authService';

const { Title, Text } = Typography;

const ROLE_LABELS: Record<string, string> = {
  SUPER_ADMIN: '超级管理员', ADMIN: '管理员', DEPT_MANAGER: '部门主管', STAFF: '普通员工',
};
const MODULE_LABELS: Record<string, string> = {
  PRODUCT: '产品管理', CATALOG: '产品图册', CASE: '客户案例',
  DOCUMENT: '内部文档', QUOTE: '报价方案', PERMISSION: '权限管理',
};
const ACTION_LABELS: Record<string, string> = {
  view: '查看', create: '新增', update: '修改', delete: '删除', export: '导出', share: '分享',
};

export default function PermissionManagementPage() {
  const [data, setData] = useState<any>(null);
  const [dirty, setDirty] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);

  const load = () => authService.getPermissionMatrix().then(({ data }) => { setData(data); setDirty({}); });
  useEffect(() => { load(); }, []);

  if (!data) return null;

  const key = (r: string, m: string, a: string) => `${r}|${m}|${a}`;
  const isChecked = (r: string, m: string, a: string) => {
    const k = key(r, m, a);
    if (k in dirty) return dirty[k];
    return !!data.matrix?.[r]?.[m]?.[a];
  };
  const toggle = (r: string, m: string, a: string, v: boolean) =>
    setDirty((prev) => ({ ...prev, [key(r, m, a)]: v }));

  const handleSave = async () => {
    const items = Object.entries(dirty).map(([k, allowed]) => {
      const [role, module, action] = k.split('|');
      return { role, module, action, allowed };
    });
    if (!items.length) { message.info('没有改动'); return; }
    setSaving(true);
    try {
      await authService.updatePermissionMatrix(items);
      message.success('权限已保存');
      load();
    } catch { message.error('保存失败'); }
    finally { setSaving(false); }
  };

  const roleTabs = (data.roles || []).map((role: string) => {
    const readOnly = role === 'ADMIN' || role === 'SUPER_ADMIN';
    return {
      key: role,
      label: ROLE_LABELS[role] || role,
      children: (
        <Card size="small">
          {readOnly && <Tag color="gold" style={{ marginBottom: 8 }}>管理员级别默认拥有全部权限，不可编辑</Tag>}
          <Table
            dataSource={(data.modules || []).map((m: string) => ({ key: m, module: m }))}
            pagination={false}
            size="small"
            columns={[
              { title: '模块', dataIndex: 'module', width: 120, render: (m: string) => MODULE_LABELS[m] || m },
              ...(data.actions || []).map((a: string) => ({
                title: ACTION_LABELS[a] || a,
                key: a,
                align: 'center' as const,
                render: (_: any, row: any) => (
                  <Checkbox
                    disabled={readOnly}
                    checked={isChecked(role, row.module, a)}
                    onChange={(e) => toggle(role, row.module, a, e.target.checked)}
                  />
                ),
              })),
            ]}
          />
        </Card>
      ),
    };
  });

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}>权限管理</Title>
        <Button type="primary" loading={saving} onClick={handleSave}>保存</Button>
      </Space>
      <Text type="secondary">按角色配置"模块 × 操作"权限矩阵。管理员/超级管理员默认拥有全部权限。</Text>
      <Tabs items={roleTabs} style={{ marginTop: 12 }} />
    </div>
  );
}
