import { Menu } from 'antd';
import {
  AppstoreOutlined, BookOutlined, FileTextOutlined,
  HomeOutlined, PictureOutlined, ShareAltOutlined,
  ShoppingOutlined, TeamOutlined, DollarOutlined,
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === 'ADMIN';

  const items = [
    { key: '/', icon: <HomeOutlined />, label: '首页' },
    { key: '/products', icon: <ShoppingOutlined />, label: '产品管理' },
    { key: '/categories', icon: <AppstoreOutlined />, label: '分类管理' },
    { key: '/catalog', icon: <PictureOutlined />, label: '产品图册' },
    { key: '/cases', icon: <BookOutlined />, label: '客户案例' },
    {
      key: 'documents', icon: <FileTextOutlined />, label: '内部文档',
      children: [
        { key: '/documents/design', label: '设计资源' },
        { key: '/documents/training', label: '培训资料' },
        { key: '/documents/certificates', label: '资质文件' },
      ],
    },
    { key: '/quotes', icon: <DollarOutlined />, label: '报价方案' },
    { key: '/shares', icon: <ShareAltOutlined />, label: '分享管理' },
    ...(isAdmin ? [{ key: '/users', icon: <TeamOutlined />, label: '用户管理' }] : []),
  ];

  return (
    <Menu mode="inline" selectedKeys={[location.pathname]}
      items={items} onClick={({ key }) => navigate(key)}
      style={{ height: '100%', borderRight: 0 }} />
  );
}
