import { Layout, Button, Space, Typography } from 'antd';
import { LogoutOutlined } from '@ant-design/icons';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import GlobalSearch from '../components/GlobalSearch';
import { useAuthStore } from '../store/authStore';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

export default function MainLayout() {
  const { user, logout } = useAuthStore();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="dark" style={{ borderRight: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{
          padding: '16px 20px',
          fontWeight: 700,
          fontSize: 16,
          color: 'rgba(255,255,255,0.87)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          智楷家具
        </div>
        <Sidebar />
      </Sider>
      <Layout>
        <Header style={{
          background: '#1e2433',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          <GlobalSearch />
          <Space>
            <Text style={{ color: 'rgba(255,255,255,0.60)' }}>{user?.display_name || user?.username}</Text>
            <Button type="text" icon={<LogoutOutlined />} onClick={logout}
              style={{ color: 'rgba(255,255,255,0.60)' }}>退出</Button>
          </Space>
        </Header>
        <Content style={{
          margin: 24,
          padding: 24,
          background: '#1e2433',
          borderRadius: 8,
          minHeight: 360,
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
