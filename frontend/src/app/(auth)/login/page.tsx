// frontend/src/app/(auth)/login/page.tsx
import Login from '@/components/login';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: "Đăng nhập",
    description: "Đăng nhập vào hệ thống Kiosk TC để quản lý hồ sơ sức khỏe một cách nhanh chóng và tiện lợi.",
};

export default function LoginPage() {
    return <Login />;
}