/* eslint-disable @typescript-eslint/no-explicit-any */
'use client'
import { getServiceExams } from "@/api/request";
import { saveSelectedService } from "@/utils/session";
import { useGlobalContext } from "@/context/app_context";
import { 
    MedicineBoxOutlined, 
    LoadingOutlined, 
    CheckCircleOutlined,
    DollarOutlined 
} from "@ant-design/icons";
import { Button, Card, message, Modal, Spin, Empty } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface ServiceExam {
    id: number;
    name: string;
    description: string;
    prices_non_insurance: number;
    prices_insurance: number;
    is_active: boolean;
}

const SelectService = () => {
    const router = useRouter();
    const { mode } = useGlobalContext();
    const [loading, setLoading] = useState(false);
    const [services, setServices] = useState<ServiceExam[]>([]);
    const [selectedService, setSelectedService] = useState<ServiceExam | null>(null);
    const [confirming, setConfirming] = useState(false);

    // Load danh sách dịch vụ khi component mount
    useEffect(() => {
        fetchServices();
    }, []);

    const fetchServices = async () => {
        setLoading(true);
        try {
            const response = await getServiceExams();
            console.log("✅ Services loaded:", response.data);
            
            // Chỉ lấy các dịch vụ đang active
            const activeServices = response.data.results.filter((service: ServiceExam) => service.is_active).map((service: any) => ({
                ...service,
                prices_insurance: parseFloat(service.prices_insurance),
                prices_non_insurance: parseFloat(service.prices_non_insurance),
            }));
            setServices(activeServices);
        } catch (error: any) {
            console.error("❌ Error loading services:", error);
            message.error("Không thể tải danh sách dịch vụ!");
        } finally {
            setLoading(false);
        }
    };

    const getPrice = (service: ServiceExam) => {
        // Nếu mode là "insurance" thì dùng giá bảo hiểm, ngược lại dùng giá không bảo hiểm
        return mode === 'insurance' ? service.prices_insurance : service.prices_non_insurance;
    };

    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
    };

    const handleSelectService = (service: ServiceExam) => {
        setSelectedService(service);
        setConfirming(true);
    };

    const handleConfirm = () => {
        if (selectedService) {
            message.success(`Đã chọn dịch vụ: ${selectedService.name}`);
            
            // Lưu dịch vụ đã chọn vào sessionStorage
            saveSelectedService(selectedService);
            
            // TODO: Chuyển sang bước tiếp theo (chọn bác sĩ, phòng khám, v.v.)
            // router.push('/chon-bac-si');
            
            setConfirming(false);
        }
    };

    const handleBack = () => {
        router.back();
    };

    return (
        <>
            {/* Confirmation Modal */}
            <Modal
                open={confirming}
                onCancel={() => setConfirming(false)}
                footer={null}
                centered
                width={500}
            >
                {selectedService && (
                    <div className="text-center py-4">
                        <CheckCircleOutlined 
                            style={{ fontSize: 56, color: "#10b981" }} 
                            className="mb-4" 
                        />
                        <h2 className="text-xl font-bold text-gray-800 mb-2">
                            Xác nhận dịch vụ
                        </h2>
                        <div className="bg-gray-50 rounded-lg p-4 my-4 text-left">
                            <div className="mb-3">
                                <span className="text-gray-600 font-medium">Dịch vụ:</span>
                                <div className="text-gray-900 font-semibold text-lg">
                                    {selectedService.name}
                                </div>
                            </div>
                            <div className="mb-3">
                                <span className="text-gray-600 font-medium">Mô tả:</span>
                                <div className="text-gray-700 text-sm">
                                    {selectedService.description}
                                </div>
                            </div>
                            <div className="flex justify-between items-center pt-3 border-t">
                                <span className="text-gray-600 font-medium">Giá dịch vụ:</span>
                                <span className="text-emerald-600 font-bold text-xl">
                                    {formatPrice(getPrice(selectedService))}
                                </span>
                            </div>
                            {mode && (
                                <div className="text-xs text-gray-500 mt-2 text-center">
                                    ({mode === 'insurance' ? 'Có bảo hiểm' : 'Không bảo hiểm'})
                                </div>
                            )}
                        </div>
                        
                        <div className="flex gap-3 mt-6">
                            <Button
                                type="default"
                                onClick={() => setConfirming(false)}
                                className="flex-1 h-11 text-base font-semibold"
                            >
                                Quay lại
                            </Button>
                            <Button
                                type="primary"
                                onClick={handleConfirm}
                                className="flex-1 h-11 text-base font-semibold bg-emerald-600 hover:bg-emerald-700"
                            >
                                Xác nhận
                            </Button>
                        </div>
                    </div>
                )}
            </Modal>

            <div className="min-h-[80vh] bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-6">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-600 rounded-full mb-3 shadow-lg">
                            <MedicineBoxOutlined className="text-3xl text-white" />
                        </div>
                        <h1 className="text-3xl font-bold text-emerald-800 mb-2">
                            Chọn Dịch Vụ Khám
                        </h1>
                        <p className="text-base text-gray-600">
                            {mode && <span className="font-semibold text-emerald-700">{mode === 'insurance' ? 'Có bảo hiểm' : 'Không bảo hiểm'}</span>}
                        </p>
                    </div>

                    {/* Services Grid */}
                    {loading ? (
                        <div className="flex justify-center items-center py-20">
                            <Spin 
                                indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} 
                                tip={<span className="text-lg text-gray-600 ml-3">Đang tải dịch vụ...</span>}
                            />
                        </div>
                    ) : services.length === 0 ? (
                        <div className="bg-white rounded-xl shadow-lg p-12">
                            <Empty
                                description={
                                    <span className="text-gray-500 text-lg">
                                        Không có dịch vụ khám nào
                                    </span>
                                }
                            />
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                            {services.map((service) => (
                                <Card
                                    key={service.id}
                                    hoverable
                                    className="shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-emerald-500"
                                    onClick={() => handleSelectService(service)}
                                >
                                    <div className="flex flex-col h-full">
                                        {/* Service Icon */}
                                        <div className="flex justify-center mb-3">
                                            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center">
                                                <MedicineBoxOutlined className="text-3xl text-emerald-600" />
                                            </div>
                                        </div>

                                        {/* Service Name */}
                                        <h3 className="text-lg font-bold text-gray-800 text-center mb-2 line-clamp-2 min-h-14">
                                            {service.name}
                                        </h3>

                                        {/* Description */}
                                        <p className="text-sm text-gray-600 text-center mb-4 line-clamp-3 grow">
                                            {service.description || "Không có mô tả"}
                                        </p>

                                        {/* Price */}
                                        <div className="border-t pt-4 mt-auto">
                                            <div className="flex items-center justify-center gap-2 mb-2">
                                                <DollarOutlined className="text-emerald-600" />
                                                <span className="text-2xl font-bold text-emerald-600">
                                                    {formatPrice(getPrice(service))}
                                                </span>
                                            </div>
                                            <div className="text-center">
                                                <Button
                                                    type="primary"
                                                    className="w-full bg-emerald-600 hover:bg-emerald-700 font-semibold"
                                                    onClick={() => handleSelectService(service)}
                                                >
                                                    Chọn dịch vụ
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}

                    {/* Back Button */}
                    <div className="flex justify-center mt-6">
                        <Button
                            type="default"
                            onClick={handleBack}
                            className="w-48 h-12 text-base font-semibold"
                        >
                            Quay lại
                        </Button>
                    </div>

                    {/* Helper Text */}
                    <div className="text-center mt-6 text-gray-500 text-sm">
                        Cần hỗ trợ? Vui lòng liên hệ quầy tiếp tân
                    </div>
                </div>
            </div>
        </>
    );
};

export default SelectService;
