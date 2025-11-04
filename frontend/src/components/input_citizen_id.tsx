'use client'
import { useGlobalContext } from "@/context/app_context";
import { IdcardOutlined, LoadingOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { Button, Form, Input, message, Modal } from "antd";
import { useRouter } from "next/navigation";
import { useState } from "react";

const InputCitizenID = () => {
    const [form] = Form.useForm();
    const router = useRouter();
    const { mode } = useGlobalContext();
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string>('');
    
    const onFinish = async (values: { citizenId: string }) => {
        setLoading(true);
        try {
            // TODO: Call API to check citizen ID
            console.log('Citizen ID:', values.citizenId);
            console.log('Mode:', mode);

            // Simulate API call

            setSuccess(true);
            message.success('Đã tìm thấy thông tin bệnh nhân!');

            // Navigate to next page after success
            setTimeout(() => {
                router.push('/thong-tin-benh-nhan');
            }, 1000);

        } catch (error) {
            message.error('Không tìm thấy thông tin. Vui lòng kiểm tra lại!');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        router.back();
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        const allowedKeys = ["Backspace", "Tab", "Delete", "ArrowLeft", "ArrowRight", "Home", "End"];
        if (!/[0-9]/.test(e.key) && !allowedKeys.includes(e.key)) {
            e.preventDefault();
            setErrorMessage('⚠️ Chỉ được nhập số từ 0-9!');
            setTimeout(() => setErrorMessage(''), 2000);
        }
    }

    return (
        <>
            {/* Loading Modal */}
            <Modal
                open={loading || success}
                footer={null}
                closable={false}
                centered
                maskClosable={false}
                styles={{ body: { textAlign: "center" } }}
            >
                {loading && <LoadingOutlined spin style={{ fontSize: 48, color: "#10b981" }} className="mb-3" />}
                {success && <CheckCircleOutlined style={{ fontSize: 48, color: "#10b981" }} className="mb-3" />}
                <div className={`text-lg font-semibold ${loading ? 'text-emerald-600' : 'text-gray-600'}`}>{loading ? 'Đang kiểm tra thông tin...' : 'Thông tin đã được xác thực!'}</div>
            </Modal>

            <div className="h-[80vh] bg-linear-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center p-4">
                <div className="w-full max-w-md">
                    {/* Header */}
                    <div className="text-center mb-6">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-600 rounded-full mb-3 shadow-lg">
                            <IdcardOutlined className="text-3xl text-white" />
                        </div>
                        <h1 className="text-2xl font-bold text-emerald-800 mb-1">
                            Nhập Căn Cước Công Dân
                        </h1>
                        <p className="text-base text-gray-600">
                            {mode && <span className="font-semibold text-emerald-700">{mode}</span>}
                        </p>
                    </div>

                    {/* Form Card */}
                    <div className="bg-white rounded-xl shadow-xl p-6">
                        <Form
                            form={form}
                            layout="vertical"
                            onFinish={onFinish}
                        >
                            <Form.Item
                                label={<span className="text-base font-semibold text-gray-700">Số Căn Cước Công Dân</span>}
                                name="citizenId"
                                rules={[
                                    { required: true, message: 'Vui lòng nhập số CCCD!' },
                                    {
                                        pattern: /^[0-9]{12}$/,
                                        message: 'CCCD phải có đúng 12 chữ số!'
                                    }
                                ]}
                                help={errorMessage || undefined}
                                validateStatus={errorMessage ? 'warning' : undefined}
                            >
                                <Input
                                    placeholder="Nhập 12 số CCCD"
                                    maxLength={12}
                                    prefix={<IdcardOutlined className="text-gray-400" />}
                                    className="text-lg py-2"
                                    autoFocus
                                    onKeyDown={handleKeyDown}
                                />
                            </Form.Item>


                            <div className="flex gap-3 mt-6">
                                <Button
                                    type="default"
                                    onClick={handleBack}
                                    className="flex-1 h-11 text-base font-semibold"
                                    disabled={loading}
                                >
                                    Quay lại
                                </Button>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    loading={loading}
                                    className="flex-1 h-11 text-base font-semibold bg-emerald-600 hover:bg-emerald-700"
                                >
                                    Tiếp tục
                                </Button>
                            </div>
                        </Form>

                        {/* Info Box */}
                        <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-xs text-blue-800">
                                <strong>Lưu ý:</strong> Vui lòng nhập đúng số căn cước công dân 12 số.
                            </p>
                        </div>
                    </div>

                    {/* Helper Text */}
                    <div className="text-center mt-4 text-gray-500 text-xs">
                        Cần hỗ trợ? Vui lòng liên hệ quầy tiếp tân
                    </div>
                </div>
            </div>
        </>
    )
}

export default InputCitizenID;