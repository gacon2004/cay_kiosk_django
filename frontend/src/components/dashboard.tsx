'use client'
import React, { useState } from 'react';
import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    DashboardOutlined,
    HistoryOutlined,
    UserOutlined,
    LogoutOutlined,
    LoadingOutlined,
} from '@ant-design/icons';
import { Button, Layout, Menu, theme, Typography, Card, Row, Col, Statistic, Modal } from 'antd';
import { useRouter } from 'next/navigation';
import { logout } from '@/api/request';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const Dashboard: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false);
    const [selectedKey, setSelectedKey] = useState('1');
    const [logoutModalVisible, setLogoutModalVisible] = useState(false);
    const [isLoggingOut, setIsLoggingOut] = useState(false);
    const [confirmLogoutVisible, setConfirmLogoutVisible] = useState(false);
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
                // Đăng xuất - hiện modal xác nhận
                setConfirmLogoutVisible(true);
                break;
        }
    };

    const handleLogout = async () => {
        setIsLoggingOut(true);
        const refresh_token = localStorage.getItem('refresh_token');
        const access_token = localStorage.getItem('access_token');
        if (refresh_token && access_token) {

            await logout(refresh_token, access_token);
        }
        setTimeout(() => {
            // Clear tokens
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');

            setIsLoggingOut(false);
            // Show success modal
            setLogoutModalVisible(true);
        }, 1000)
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

            {/* Confirm Logout Modal */}
            <Modal
                open={confirmLogoutVisible}
                title="Xác nhận đăng xuất"
                onCancel={() => setConfirmLogoutVisible(false)}
                footer={[
                    <Button key="cancel" onClick={() => setConfirmLogoutVisible(false)}>
                        Hủy
                    </Button>,
                    <Button key="confirm" type="primary" danger onClick={() => {
                        setConfirmLogoutVisible(false);
                        handleLogout();
                    }}>
                        Đăng xuất
                    </Button>,
                ]}
                centered
            >
                <p>Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?</p>
            </Modal>

            {/* Logout Loading Modal */}
            <Modal
                open={isLoggingOut}
                footer={null}
                closable={false}
                centered
                styles={{ body: { textAlign: "center" } }}
            >
                <LoadingOutlined spin style={{ fontSize: 48, color: "#2563eb" }} className="mb-3" />
                <div className="text-lg font-semibold">Đang đăng xuất...</div>
            </Modal>

            {/* Logout Success Modal */}
            <Modal
                open={logoutModalVisible}
                title="Đăng xuất thành công"
                onCancel={() => setLogoutModalVisible(false)}
                footer={[
                    <Button key="ok" type="primary" onClick={() => router.push('/login')}>
                        OK
                    </Button>,
                ]}
                centered
            >
                <p>Bạn đã đăng xuất thành công khỏi hệ thống.</p>
            </Modal>
        </Layout>
    );
};

export default Dashboard;