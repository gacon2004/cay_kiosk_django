// frontend/src/app/(admin)/dashboard/page.tsx
import Dashboard from '@/components/dashboard';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: "Dashboard",
    description: "Khôi phục mật khẩu tài khoản trên hệ thống Kiosk TC để tiếp tục quản lý hồ sơ sức khỏe một cách nhanh chóng và tiện lợi.",
};

export default function DashboardPage() {
    return <Dashboard />;
}