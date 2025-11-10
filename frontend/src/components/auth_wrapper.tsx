'use client'
import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface AuthWrapperProps {
    children: React.ReactNode;
}

const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
    const router = useRouter();
    const [showMessage, setShowMessage] = useState(false);
    const hasChecked = useRef(false);

    useEffect(() => {
        if (hasChecked.current) return;
        hasChecked.current = true;
        // Kiểm tra token trong localStorage
        const accessToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        if (!accessToken) {
            setTimeout(() => {
                setShowMessage(true);
                setTimeout(() => {
                    router.replace('/login');
                }, 2000);
            }, 0);
        }
    }, [router]);

    if (showMessage) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <div className="bg-white p-6 rounded shadow text-center">
                    <div className="text-red-600 font-bold text-lg mb-2">Phiên làm việc đã hết hoặc bạn chưa đăng nhập!</div>
                    <div className="text-gray-700">Bạn sẽ được chuyển về trang đăng nhập...</div>
                </div>
            </div>
        );
    }

    // Nếu có token thì render children, nếu không sẽ redirect
    return <>{children}</>;
};

export default AuthWrapper;
