/* eslint-disable @typescript-eslint/no-explicit-any */
'use client'
import { checkInsuranceByCitizenID, getPatientByCitizenID } from "@/api/request";
import { useGlobalContext } from "@/context/app_context";
import { IdcardOutlined, LoadingOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { Button, Form, Input, message, Modal } from "antd";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useState } from "react";

interface InsuranceDataResponse {
    insurance_id: string;
    citizen_id: string;
    fullname: string;
    gender: boolean;
    dob: string;
    phone_number: string;
    registration_place: string;
    valid_from: string;
    expired: string
    is_valid: string
    days_until_expiry: number;
}

interface NoneInsuranceDataResponse {
    // Định nghĩa các trường dữ liệu không bảo hiểm nếu cần
    citizen_id: string;
    fullname: string;
    gender: boolean;
    phone_number: string;
    dob: string;
    age: number;
    occupation: string;
    address: string;
    is_insurance: boolean;
    ethnicity: string;
}

const InputCitizenID = () => {
    const [form] = Form.useForm();
    const router = useRouter();
    const { mode } = useGlobalContext();
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string>('');
    const [error, setError] = useState(false);
    const [insuranceData, setInsuranceData] = useState<InsuranceDataResponse | null>(null);
    const [patientData, setPatientData] = useState<NoneInsuranceDataResponse | null>(null);

    const onFinish = async (values: { citizenId: string }) => {
        const { citizenId } = values;
        console.log("🔍 Current mode:", mode);
        setLoading(true);
        setError(false);
        setSuccess(false);

        try {
            if (mode === "insurance") {
                const response = await checkInsuranceByCitizenID(citizenId);
                console.log("✅ API Response:", response);
                
                if (response.data) {
                    setInsuranceData(response.data.insurance);
                    setSuccess(true);
                    console.log("🎉 Setting success=true, insuranceData:", response.data);
                    message.success("Đã tìm thấy thông tin bảo hiểm!");
                } else {
                    setError(true);
                    setErrorMessage("Không tìm thấy thông tin bảo hiểm!");
                }
            } else {
                const response = await getPatientByCitizenID(citizenId);
                console.log("✅ Response Data:", response.data);
                
                if (response.data) {
                    setPatientData(response.data);
                    setSuccess(true);
                    message.success("Đã tìm thấy thông tin người khám!");
                } else {
                    setError(true);
                    setErrorMessage("Không tìm thấy thông tin người khám!");
                }
            }

        } catch (error: any) {
            setError(true);

            // Axios error có cấu trúc riêng
            if (axios.isAxiosError(error)) {
                if (error.response) {
                    // Server trả về lỗi HTTP (ví dụ: 404, 500)
                    console.error("📡 API Error:", error.response.data);
                    const errorMsg = error.response.data?.detail ||
                        error.response.data?.message ||
                        `Lỗi ${error.response.status}: Không tìm thấy thông tin.`;
                    setErrorMessage(errorMsg);
                } else if (error.request) {
                    // Request gửi đi nhưng không nhận phản hồi
                    console.error("No Response:", error.request);
                    setErrorMessage("Không có phản hồi từ máy chủ!");
                } else {
                    // Lỗi khác (VD: cấu hình axios sai)
                    console.error("Axios config error:", error.message);
                    setErrorMessage("Lỗi cấu hình API!");
                }
            } else {
                // Lỗi khác không phải từ axios
                console.error("Unknown error:", error);
                setErrorMessage("Đã xảy ra lỗi không xác định!");
            }
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
                open={loading || success || error}
                footer={null}
                closable={false}
                centered
                maskClosable={false}
                styles={{ body: { textAlign: "center" } }}
            >
                {loading && (
                    <>
                        <LoadingOutlined spin style={{ fontSize: 48, color: "#10b981" }} className="mb-3" />
                        <div className="text-lg font-semibold text-emerald-600">Đang kiểm tra thông tin...</div>
                    </>
                )}

                {success && insuranceData && (
                    <>
                        <CheckCircleOutlined style={{ fontSize: 48, color: "#10b981" }} className="mb-3" />
                        <div className="text-lg font-semibold text-emerald-600 mb-4">Thông tin bảo hiểm y tế</div>

                        <div className="text-left bg-gray-50 rounded-lg p-4 space-y-2">
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số thẻ BHYT:</span>
                                <span className="text-gray-900 font-semibold">{insuranceData.insurance_id}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số CCCD:</span>
                                <span className="text-gray-900 font-semibold">{insuranceData.citizen_id}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Họ và tên:</span>
                                <span className="text-gray-900 font-semibold">{insuranceData.fullname}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Ngày sinh:</span>
                                <span className="text-gray-900">{insuranceData.dob}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Giới tính:</span>
                                <span className="text-gray-900">{insuranceData.gender === true ? "Nam" : "Nữ"}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số điện thoại:</span>
                                <span className="text-gray-900">{insuranceData.phone_number}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Ngày cấp:</span>
                                <span className="text-gray-900">{insuranceData.valid_from}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Ngày hết hạn:</span>
                                <span className="text-gray-900">{insuranceData.expired}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Nơi đăng ký KCB:</span>
                                <span className="text-gray-900">{insuranceData.registration_place}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Trạng thái:</span>
                                <span className="text-gray-900">{insuranceData.is_valid ? "Còn hiệu lực" : "Hết hiệu lực"}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Còn lại (ngày):</span>
                                <span className="text-gray-900">{insuranceData.days_until_expiry}</span>
                            </div>
                        </div>

                        <Button
                            type="primary"
                            className="mt-4 bg-emerald-600 w-full"
                            onClick={() => {
                                setSuccess(false);
                                setInsuranceData(null);
                                form.resetFields();
                                router.push("/chon-dich-vu");
                            }}
                        >
                            Bước tiếp theo
                        </Button>
                    </>
                )}

                {success && patientData && (
                    <>
                        <CheckCircleOutlined style={{ fontSize: 48, color: "#10b981" }} className="mb-3" />
                        <div className="text-lg font-semibold text-emerald-600 mb-4">Thông tin người khám</div>

                        <div className="text-left bg-gray-50 rounded-lg p-4 space-y-2">
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số CCCD:</span>
                                <span className="text-gray-900 font-semibold">{patientData.citizen_id}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Họ và tên:</span>
                                <span className="text-gray-900 font-semibold">{patientData.fullname}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Ngày sinh:</span>
                                <span className="text-gray-900">{patientData.dob}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Giới tính:</span>
                                <span className="text-gray-900">{patientData.gender === true ? "Nam" : "Nữ"}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số điện thoại:</span>
                                <span className="text-gray-900">{patientData.phone_number}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Tuổi:</span>
                                <span className="text-gray-900">{patientData.age}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Nghề nghiệp:</span>
                                <span className="text-gray-900">{patientData.occupation}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Địa chỉ:</span>
                                <span className="text-gray-900">{patientData.address}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Bảo hiểm y tế:</span>
                                <span className="text-gray-900">{patientData.is_insurance ? "Có" : "Không"}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Sử dụng bảo hiểm y tế:</span>
                                <span className="text-gray-900">{"Không"}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Dân tộc:</span>
                                <span className="text-gray-900">{patientData.ethnicity}</span>
                            </div>
                        </div>
                        <Button
                            type="primary"
                            className="mt-4 bg-emerald-600 w-full"
                            onClick={() => {
                                setSuccess(false);
                                setPatientData(null);
                                form.resetFields();
                                router.push("/chon-dich-vu");
                            }}
                        >
                            Bước tiếp theo
                        </Button>
                    </>
                )}

                {error && (
                    <>
                        <IdcardOutlined style={{ fontSize: 48, color: "#ef4444" }} className="mb-3" />
                        <div className="text-lg font-semibold text-red-600">Không tìm thấy thông tin!</div>
                        {errorMessage && (
                            <div className="text-sm text-gray-600 mt-2">{errorMessage}</div>
                        )}
                        <Button
                            type="primary"
                            className="mt-3 bg-emerald-600"
                            onClick={() => {
                                router.push("/chon-dich-vu");
                                setError(false);
                                setErrorMessage('');
                            }}
                        >
                            Thử lại
                        </Button>
                    </>
                )}
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