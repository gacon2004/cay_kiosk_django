// frontend/src/components/forgot_password.tsx
'use client'
/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const ForgotPassword: React.FC = () => {
    const router = useRouter();

    // State cho form
    const [email, setEmail] = useState('');

    // State cho UI
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    // Handle input changes
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setEmail(e.target.value);

        // Clear errors khi user nhập
        if (error) setError('');
        if (message) setMessage('');
    };

    // Handle form submit
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validate form
        if (!email) {
            setError('Vui lòng nhập địa chỉ email.');
            return;
        }

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setError('Vui lòng nhập địa chỉ email hợp lệ.');
            return;
        }

        setLoading(true);
        setError('');
        setMessage('');

        try {
            // Gọi API forgot password
            const response = await axios.post(`${API_URL}/auth/forgot-password`, {
                email: email
            });

            // Success
            setMessage('Email hướng dẫn đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư của bạn.');

        } catch (err: any) {
            // Error handling
            if (err.response && err.response.data) {
                setError(err.response.data.error || 'Có lỗi xảy ra. Vui lòng thử lại.');
            } else {
                setError('Không thể kết nối đến server. Vui lòng thử lại.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 px-4">
            <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
                <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
                    Quên Mật Khẩu
                </h2>
                <p className="text-center text-gray-600 mb-8 text-sm">
                    Nhập địa chỉ email của bạn để nhận hướng dẫn đặt lại mật khẩu.
                </p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                            Địa chỉ Email
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={email}
                            onChange={handleChange}
                            placeholder="Nhập địa chỉ email"
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
                        {loading ? 'Đang gửi...' : 'Gửi Hướng Dẫn'}
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

export default ForgotPassword;