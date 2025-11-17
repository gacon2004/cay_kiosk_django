'use client'
import { payOrder } from "@/api/request";
import { getOrderInfo, getSelectedService, saveOrderInfo } from "@/utils/session";
import { Button, Card, message, Radio, Space, Typography } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const { Title, Text } = Typography;

const PaymentPage = () => {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [paymentMethod, setPaymentMethod] = useState('cash');

    const orderInfo = getOrderInfo();
    const selectedService = getSelectedService();

    useEffect(() => {
        if (!orderInfo || !selectedService) {
            message.error("Không tìm thấy thông tin đơn hàng!");
            router.push('/select-service');
            return;
        }
    }, [orderInfo, selectedService, router]);

    const handlePayment = async () => {
        if (!orderInfo) return;

        setLoading(true);
        try {
            const response = await payOrder(orderInfo.id, paymentMethod);
            message.success("Thanh toán thành công!");

            // Cập nhật thông tin đơn hàng đã thanh toán vào session
            saveOrderInfo(response.data);

            // Chuyển sang trang xem phiếu khám
            router.push('/appointment-info');
        } catch (error: unknown) {
            console.error("❌ Payment error:", error);
            message.error("Thanh toán thất bại! Vui lòng thử lại.");
        } finally {
            setLoading(false);
        }
    };

    if (!orderInfo || !selectedService) {
        return <div>Đang tải...</div>;
    }

    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <Card className="w-full max-w-md shadow-lg">
                <div className="text-center mb-6">
                    <Title level={3} className="text-blue-600 mb-2">
                        Thanh toán dịch vụ
                    </Title>
                    <Text className="text-gray-600">
                        Vui lòng chọn phương thức thanh toán
                    </Text>
                </div>

                {/* Thông tin đơn hàng */}
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <Text strong>Dịch vụ:</Text>
                            <Text>{selectedService.name}</Text>
                        </div>
                        <div className="flex justify-between">
                            <Text strong>Bệnh nhân:</Text>
                            <Text>{orderInfo.patient_name}</Text>
                        </div>
                        <div className="flex justify-between">
                            <Text strong>Số tiền:</Text>
                            <Text className="text-lg font-bold text-green-600">
                                {formatPrice(orderInfo.amount)}
                            </Text>
                        </div>
                    </div>
                </div>

                {/* Phương thức thanh toán */}
                <div className="mb-6">
                    <Text strong className="block mb-3">Phương thức thanh toán:</Text>
                    <Radio.Group
                        value={paymentMethod}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                        className="w-full"
                    >
                        <Space direction="vertical" className="w-full">
                            <Radio value="cash" className="w-full">
                                <div className="flex items-center">
                                    <span className="mr-2">💵</span>
                                    Tiền mặt
                                </div>
                            </Radio>
                            <Radio value="card" className="w-full">
                                <div className="flex items-center">
                                    <span className="mr-2">💳</span>
                                    Thẻ tín dụng
                                </div>
                            </Radio>
                            <Radio value="insurance" className="w-full">
                                <div className="flex items-center">
                                    <span className="mr-2">🏥</span>
                                    Bảo hiểm y tế
                                </div>
                            </Radio>
                        </Space>
                    </Radio.Group>
                </div>

                {/* Nút thanh toán */}
                <Button
                    type="primary"
                    size="large"
                    block
                    loading={loading}
                    onClick={handlePayment}
                    className="bg-blue-600 hover:bg-blue-700"
                >
                    {loading ? 'Đang xử lý...' : 'Thanh toán'}
                </Button>

                {/* Nút quay lại */}
                <Button
                    type="link"
                    block
                    onClick={() => router.back()}
                    className="mt-3"
                >
                    Quay lại
                </Button>
            </Card>
        </div>
    );
};

export default PaymentPage;