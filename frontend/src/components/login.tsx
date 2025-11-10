// frontend/src/components/login.tsx
'use client'
/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const Login: React.FC = () => {
    const router = useRouter();

    // State cho form
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });

    // State cho UI
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

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
        if (!formData.username || !formData.password) {
            setError('Vui lòng nhập đầy đủ thông tin đăng nhập.');
            return;
        }

        setLoading(true);
        setError('');
        setMessage('');

        try {
            // Gọi API login
            const response = await axios.post(`${API_URL}/auth/login`, {
                username: formData.username,
                password: formData.password
            });

            // Success - lưu tokens và chuyển hướng
            const { access, refresh } = response.data;

            // Lưu tokens vào localStorage
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);

            setMessage('Đăng nhập thành công! Đang chuyển hướng...');

            // Redirect to dashboard after 2 seconds
            setTimeout(() => {
                router.push('/dashboard');
            }, 2000);

        } catch (err: any) {
            // Error handling
            if (err.response && err.response.data) {
                setError(err.response.data.error || 'Đăng nhập thất bại.');
            } else {
                setError('Không thể kết nối đến server. Vui lòng thử lại.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 px-4">
            <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
                <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
                    Đăng Nhập
                </h2>
                <p className="text-center text-gray-600 mb-8 text-sm">
                    Vui lòng nhập thông tin tài khoản để tiếp tục.
                </p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                            Tên đăng nhập
                        </label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Nhập tên đăng nhập"
                            required
                            disabled={loading}
                            className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed transition duration-200"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                            Mật khẩu
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Nhập mật khẩu"
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
                        {loading ? 'Đang xử lý...' : 'Đăng Nhập'}
                    </button>
                </form>

                <div className="text-center mt-6 space-y-2">
                    <button
                        onClick={() => router.push('/forgot-password')}
                        className="text-blue-600 hover:text-blue-800 font-medium transition duration-200 block w-full"
                    >
                        Quên mật khẩu?
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;