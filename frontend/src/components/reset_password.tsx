'use client'
/* eslint-disable @typescript-eslint/no-explicit-any */
// frontend/src/components/reset_password.tsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const ResetPassword: React.FC = () => {
    const searchParams = useSearchParams();
    const router = useRouter();

    // Lấy uid và token từ URL
    const uid = searchParams.get('uid');
    const token = searchParams.get('token');

    // State cho form
    const [formData, setFormData] = useState({
        newPassword: '',
        confirmPassword: ''
    });

    // State cho UI
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    // Validate URL params khi component mount
    useEffect(() => {
        if (!uid || !token) {
            setError('Link reset mật khẩu không hợp lệ hoặc đã hết hạn.');
        }
    }, [uid, token]);

    // Handle input changes
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Clear errors khi user nhập
        if (error) setError('');
        if (message) setMessage('');
    };

    // Handle form submit
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validate form
        if (!formData.newPassword || !formData.confirmPassword) {
            setError('Vui lòng nhập đầy đủ thông tin.');
            return;
        }

        if (formData.newPassword.length < 8) {
            setError('Mật khẩu mới phải có ít nhất 8 ký tự.');
            return;
        }

        if (formData.newPassword !== formData.confirmPassword) {
            setError('Mật khẩu xác nhận không khớp.');
            return;
        }

        // Validate URL params
        if (!uid || !token) {
            setError('Link reset mật khẩu không hợp lệ.');
            return;
        }

        setLoading(true);
        setError('');
        setMessage('');

        try {
            // Gọi API reset password
            const response = await axios.post(`${API_URL}/auth/reset-password`, {
                uid: uid,
                token: token,
                new_password: formData.newPassword,
                confirm_password: formData.confirmPassword
            });
            
            if(response.status !== 200) {
                throw new Error('Có lỗi xảy ra khi reset mật khẩu.');
            }

            // Success
            setMessage('Mật khẩu đã được reset thành công! Đang chuyển hướng...');

            // Redirect to login after 3 seconds
            setTimeout(() => {
                router.push('/login');
            }, 3000);

        } catch (err: any) {
            // Error handling
            if (err.response && err.response.data) {
                setError(err.response.data.error || 'Có lỗi xảy ra khi reset mật khẩu.');
            } else {
                setError('Không thể kết nối đến server. Vui lòng thử lại.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Nếu không có uid/token hợp lệ
    if (!uid || !token) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 px-4">
                <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
                    <h2 className="text-2xl font-bold text-center text-gray-800 mb-4">
                        Reset Mật Khẩu
                    </h2>
                    <div className="bg-red-50 border-l-4 border-red-400 text-red-700 p-4 mb-6">
                        {error}
                    </div>
                    <button
                        onClick={() => router.push('/forgot-password')}
                        className="w-full bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition duration-200"
                    >
                        Quay lại trang quên mật khẩu
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 px-4">
            <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
                <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
                    Đặt Lại Mật Khẩu
                </h2>
                <p className="text-center text-gray-600 mb-8 text-sm">
                    Vui lòng nhập mật khẩu mới cho tài khoản của bạn.
                </p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-2">
                            Mật Khẩu Mới
                        </label>
                        <input
                            type="password"
                            id="newPassword"
                            name="newPassword"
                            value={formData.newPassword}
                            onChange={handleChange}
                            placeholder="Nhập mật khẩu mới"
                            required
                            disabled={loading}
                            className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed transition duration-200"
                        />
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                            Xác Nhận Mật Khẩu
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            placeholder="Nhập lại mật khẩu mới"
                            required
                            disabled={loading}
                            className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed transition duration-200"
                        />
                    </div>

                    {error && (
                        <div className="bg-red-50 border-l-4 border-red-400 text-red-700 p-4">
                            {error}
                        </div>
                    )}

                    {message && (
                        <div className="bg-green-50 border-l-4 border-green-400 text-green-700 p-4">
                            {message}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium py-2 px-4 rounded-md transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                    >
                        {loading ? 'Đang xử lý...' : 'Đặt Lại Mật Khẩu'}
                    </button>
                </form>

                <div className="text-center mt-6">
                    <button
                        onClick={() => router.push('/login')}
                        className="text-blue-600 hover:text-blue-800 font-medium transition duration-200"
                    >
                        Quay lại đăng nhập
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ResetPassword;