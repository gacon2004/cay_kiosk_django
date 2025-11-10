'use client'
import React, { useState } from 'react';
import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    DashboardOutlined,
    HistoryOutlined,
    UserOutlined,
    LogoutOutlined,
} from '@ant-design/icons';
import { Button, Layout, Menu, theme, Typography, Card, Row, Col, Statistic } from 'antd';
import { useRouter } from 'next/navigation';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const Dashboard: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false);
    const [selectedKey, setSelectedKey] = useState('1');
    const router = useRouter();

    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    const handleMenuClick = (key: string) => {
        setSelectedKey(key);
        // Handle navigation logic here
        switch (key) {
            case '1':
                // Dashboard - stay on current page
                break;
            case '2':
                // Lịch sử giao dịch
                router.push('/history');
                break;
            case '3':
                // Quản lý tài khoản
                router.push('/profile');
                break;
            case '4':
                // Đăng xuất
                handleLogout();
                break;
        }
    };

    const handleLogout = () => {
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
    };

    const menuItems = [
        {
            key: '1',
            icon: <DashboardOutlined />,
            label: 'Dashboard',
        },
        {
            key: '2',
            icon: <HistoryOutlined />,
            label: 'Lịch sử giao dịch',
        },
        {
            key: '3',
            icon: <UserOutlined />,
            label: 'Quản lý tài khoản',
        },
        {
            key: '4',
            icon: <LogoutOutlined />,
            label: 'Đăng xuất',
            danger: true,
        },
    ];

    const renderContent = () => {
        switch (selectedKey) {
            case '1':
                return (
                    <div>
                        <Title level={2}>Dashboard</Title>
                        <Row gutter={16} style={{ marginTop: 24 }}>
                            <Col span={8}>
                                <Card>
                                    <Statistic
                                        title="Tổng số lượt khám"
                                        value={1128}
                                        prefix={<UserOutlined />}
                                    />
                                </Card>
                            </Col>
                            <Col span={8}>
                                <Card>
                                    <Statistic
                                        title="Lịch hẹn hôm nay"
                                        value={25}
                                        prefix={<HistoryOutlined />}
                                    />
                                </Card>
                            </Col>
                            <Col span={8}>
                                <Card>
                                    <Statistic
                                        title="Bệnh nhân đang chờ"
                                        value={8}
                                        prefix={<DashboardOutlined />}
                                    />
                                </Card>
                            </Col>
                        </Row>
                        <Card style={{ marginTop: 24 }}>
                            <Title level={4}>Thông tin hệ thống</Title>
                            <p>Chào mừng đến với hệ thống Kiosk Y Tế. Đây là trang tổng quan hiển thị các thông tin quan trọng về hoạt động của hệ thống.</p>
                        </Card>
                    </div>
                );
            case '2':
                return (
                    <div>
                        <Title level={2}>Lịch sử giao dịch</Title>
                        <Card style={{ marginTop: 24 }}>
                            <p>Nội dung lịch sử giao dịch sẽ được hiển thị ở đây.</p>
                        </Card>
                    </div>
                );
            case '3':
                return (
                    <div>
                        <Title level={2}>Quản lý tài khoản</Title>
                        <Card style={{ marginTop: 24 }}>
                            <p>Nội dung quản lý tài khoản sẽ được hiển thị ở đây.</p>
                        </Card>
                    </div>
                );
            default:
                return (
                    <div>
                        <Title level={2}>Dashboard</Title>
                        <Card style={{ marginTop: 24 }}>
                            <p>Chào mừng đến với hệ thống Kiosk Y Tế.</p>
                        </Card>
                    </div>
                );
        }
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider
                trigger={null}
                collapsible
                collapsed={collapsed}
                style={{
                    background: '#001529',
                }}
            >
                <div
                    style={{
                        height: 64,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: '#002140',
                        marginBottom: 16,
                    }}
                >
                    <Title
                        level={collapsed ? 5 : 4}
                        style={{
                            color: 'white',
                            margin: 0,
                            textAlign: 'center'
                        }}
                    >
                        {collapsed ? 'Kiosk' : 'Kiosk Y Tế'}
                    </Title>
                </div>
                <Menu
                    theme="dark"
                    mode="inline"
                    selectedKeys={[selectedKey]}
                    onClick={({ key }) => handleMenuClick(key)}
                    items={menuItems}
                />
            </Sider>
            <Layout>
                <Header
                    style={{
                        padding: 0,
                        background: colorBgContainer,
                        display: 'flex',
                        alignItems: 'center',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    }}
                >
                    <Button
                        type="text"
                        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => setCollapsed(!collapsed)}
                        style={{
                            fontSize: '16px',
                            width: 64,
                            height: 64,
                        }}
                    />
                    <div style={{ marginLeft: 'auto', marginRight: 24 }}>
                        <Title level={4} style={{ margin: 0 }}>
                            Hệ thống Kiosk Y Tế
                        </Title>
                    </div>
                </Header>
                <Content
                    className="m-4"
                    style={{
                        padding: 24,
                        minHeight: 280,
                        background: colorBgContainer,
                        borderRadius: borderRadiusLG,
                    }}
                >
                    {renderContent()}
                </Content>
            </Layout>
        </Layout>
    );
};

export default Dashboard;