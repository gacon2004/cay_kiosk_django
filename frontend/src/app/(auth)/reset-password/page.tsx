// frontend/src/app/reset-password/page.tsx
import ResetPassword from '@/components/reset_password';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: "Đặt lại mật khẩu",
    description: "Đặt lại mật khẩu tài khoản trên hệ thống Kiosk TC để tiếp tục quản lý hồ sơ sức khỏe một cách nhanh chóng và tiện lợi.",
};

export default function ResetPasswordPage() {
    return <ResetPassword />;
}