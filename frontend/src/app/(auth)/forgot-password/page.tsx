// frontend/src/app/forgot-password/page.tsx
import ForgotPassword from '@/components/forgot_password';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: "Quên mật khẩu",
    description: "Khôi phục mật khẩu tài khoản trên hệ thống Kiosk TC để tiếp tục quản lý hồ sơ sức khỏe một cách nhanh chóng và tiện lợi.",
};

export default function ForgotPasswordPage() {
    return <ForgotPassword />;
}