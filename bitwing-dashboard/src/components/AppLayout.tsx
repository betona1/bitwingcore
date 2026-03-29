/** 앱 메인 레이아웃 — Ant Design Layout + 사이드바 */

import { useState } from 'react'
import { Layout, Menu, theme, Typography } from 'antd'
import {
  DashboardOutlined,
  CalendarOutlined,
  CheckSquareOutlined,
  FileTextOutlined,
  DollarOutlined,
  DesktopOutlined,
  BarChartOutlined,
  TeamOutlined,
  MessageOutlined,
  MailOutlined,
  FolderOutlined,
  ApiOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'

const { Sider, Content, Header } = Layout
const { Title } = Typography

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '대시보드' },
  { key: '/chat', icon: <MessageOutlined />, label: '채팅' },
  { key: '/managers', icon: <TeamOutlined />, label: '매니저' },
  { key: '/calendar', icon: <CalendarOutlined />, label: '일정' },
  { key: '/todos', icon: <CheckSquareOutlined />, label: '할일' },
  { key: '/memos', icon: <FileTextOutlined />, label: '메모' },
  { key: '/finance', icon: <DollarOutlined />, label: '가계부' },
  { key: '/emails', icon: <MailOutlined />, label: '이메일' },
  { key: '/files', icon: <FolderOutlined />, label: '파일' },
  { key: '/pcs', icon: <DesktopOutlined />, label: 'PC 관리' },
  { key: '/reports', icon: <BarChartOutlined />, label: '리포트' },
  { key: '/integrations', icon: <ApiOutlined />, label: '연동' },
]

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { token } = theme.useToken()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{ background: token.colorBgContainer }}
      >
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <Title level={collapsed ? 5 : 4} style={{ margin: 0, color: token.colorPrimary }}>
            {collapsed ? 'BW' : 'Bitwing'}
          </Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: token.colorBgContainer, padding: '0 24px', display: 'flex', alignItems: 'center' }}>
          <Title level={4} style={{ margin: 0 }}>Bitwing Dashboard</Title>
        </Header>
        <Content style={{ margin: '16px', padding: '24px', background: token.colorBgContainer, borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
