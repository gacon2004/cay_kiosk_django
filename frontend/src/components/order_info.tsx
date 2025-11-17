'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
    CheckCircleOutlined,
    ClockCircleOutlined,
    UserOutlined,
    ArrowLeftOutlined
} from '@ant-design/icons';
import { Button, Card, message } from 'antd';
import { getOrderInfo } from '@/utils/session';
import type { OrderInfo } from '@/utils/session';

const OrderInfo: React.FC = () => {
    const router = useRouter();
    const [order, setOrder] = useState<OrderInfo | null>(null);

    useEffect(() => {
        const orderData = getOrderInfo();
        if (!orderData) {
            message.error('Không tìm thấy thông tin phiếu khám!');
            router.push('/select-service');
            return;
        }
        setOrder(orderData);
    }, [router]);

    if (!order) {
        return <div>Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-green-600 rounded-full mb-4 shadow-lg">
                        <CheckCircleOutlined className="text-4xl text-white" />
                    </div>
                    <h1 className="text-4xl font-bold text-gray-800 mb-2">
                        Phiếu Khám Bệnh
                    </h1>
                    <p className="text-lg text-gray-600">
                        Thông tin phiếu khám của bạn
                    </p>
                </div>

                {/* Main Card */}
                <Card className="shadow-2xl border-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Patient Info */}
                        <div className="space-y-4">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                                <UserOutlined className="mr-2 text-blue-600" />
                                Thông tin bệnh nhân
                            </h2>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="mb-3">
                                    <span className="text-gray-600 font-medium">Họ tên:</span>
                                    <div className="text-gray-900 font-semibold text-lg">
                                        {appointment.patient_name}
                                    </div>
                                </div>
                                <div className="mb-3">
                                    <span className="text-gray-600 font-medium">Dịch vụ:</span>
                                    <div className="text-gray-900 font-semibold">
                                        {appointment.service_name}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Appointment Info */}
                        <div className="space-y-4">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                                <ClockCircleOutlined className="mr-2 text-green-600" />
                                Thông tin phiếu khám
                            </h2>

                            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600 font-medium">Số thứ tự:</span>
                                    <span className="text-2xl font-bold text-red-600 bg-red-100 px-3 py-1 rounded">
                                        {appointment.appointment_number || 'Chưa có'}
                                    </span>
                                </div>

                                {appointment.doctor_name && (
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600 font-medium">Bác sĩ:</span>
                                        <span className="text-gray-900 font-semibold">
                                            {appointment.doctor_name}
                                        </span>
                                    </div>
                                )}

                                {appointment.room_name && (
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600 font-medium">Phòng:</span>
                                        <span className="text-gray-900 font-semibold">
                                            {appointment.room_name}
                                        </span>
                                    </div>
                                )}

                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600 font-medium">Trạng thái:</span>
                                    <span className={`font-semibold px-2 py-1 rounded text-sm ${
                                        appointment.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                        appointment.status === 'paid' ? 'bg-green-100 text-green-800' :
                                        'bg-red-100 text-red-800'
                                    }`}>
                                        {appointment.status === 'pending' ? 'Chờ thanh toán' :
                                         appointment.status === 'paid' ? 'Đã thanh toán' : 'Đã hủy'}
                                    </span>
                                </div>

                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600 font-medium">Thời gian tạo:</span>
                                    <span className="text-gray-900 font-semibold">
                                        {new Date(appointment.created_at).toLocaleString('vi-VN')}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Instructions */}
                    <div className="mt-8 bg-blue-50 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-blue-800 mb-3">
                            Hướng dẫn
                        </h3>
                        <ul className="text-blue-700 space-y-2">
                            <li>• Vui lòng đến quầy tiếp tân với số phiếu <strong>{appointment.appointment_number}</strong></li>
                            <li>• Theo dõi màn hình hiển thị để biết khi đến lượt</li>
                            <li>• Mang theo giấy tờ tùy thân và thẻ bảo hiểm (nếu có)</li>
                            <li>• Thời gian chờ có thể thay đổi tùy theo tình hình thực tế</li>
                        </ul>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-center mt-8 space-x-4">
                        <Button
                            type="default"
                            icon={<ArrowLeftOutlined />}
                            onClick={() => router.back()}
                            size="large"
                            className="px-8"
                        >
                            Quay lại
                        </Button>
                        <Button
                            type="primary"
                            onClick={() => router.push('/')}
                            size="large"
                            className="px-8 bg-blue-600 hover:bg-blue-700"
                        >
                            Về trang chủ
                        </Button>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default AppointmentInfo;