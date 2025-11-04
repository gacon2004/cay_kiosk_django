'use client';
import { Button, DatePicker, Form, Input, Radio, Row, Col, Card, message } from "antd";
import { IdcardOutlined, PhoneOutlined, UserOutlined, HomeOutlined, CalendarOutlined } from "@ant-design/icons";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Provinces from "./province";
import dayjs from "dayjs";

// Types
interface RegisterFormValues {
    citizenId: string;
    phone: string;
    fullName: string;
    address: string;
    occupation: string;
    dateOfBirth: dayjs.Dayjs;
    ethnicity: string;
    gender: 'male' | 'female' | 'other';
}

const Register = () => {
    const [form] = Form.useForm();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [fullAddress, setFullAddress] = useState<string>('');

    const onFinish = async (values: RegisterFormValues) => {
        setLoading(true);
        try {
            const formData = {
                ...values,
                dateOfBirth: values.dateOfBirth.format('YYYY-MM-DD'),
                address: fullAddress,
            };

            console.log('Form Data:', formData);

            // TODO: Call API to register patient
            // await fetch('/api/patients/register', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(formData)
            // });

            message.success('Đăng ký thành công!');

            // Navigate to next page
            setTimeout(() => {
                router.push('/thanh-cong');
            }, 1500);

        } catch (error) {
            message.error('Đăng ký thất bại. Vui lòng thử lại!');
            console.error('Registration error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        form.resetFields();
        setFullAddress('');
    };

    return (
        <div className="min-h-screen bg-linear-to-br from-emerald-50 via-teal-50 to-cyan-50 py-8 px-4 mb-14">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-6">
                    <h1 className="text-3xl font-bold text-emerald-800 mb-2">
                        Đăng Ký Khám Bệnh
                    </h1>
                    <p className="text-gray-600">
                        Vui lòng điền đầy đủ thông tin để đăng ký
                    </p>
                </div>

                {/* Form Card */}
                <Card className="shadow-xl">
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={onFinish}
                        size="large"
                        scrollToFirstError
                    >
                        {/* Thông tin cá nhân */}
                        <div className="mb-0">
                            <h3 className="text-lg font-semibold text-emerald-700 mb-4 border-b pb-2">
                                Thông tin cá nhân
                            </h3>

                            <Row gutter={[16, 0]}>
                                {/* Căn cước công dân */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Số Căn Cước Công Dân</span>}
                                        name="citizenId"
                                        rules={[
                                            { required: true, message: 'Vui lòng nhập số CCCD!' },
                                            { pattern: /^[0-9]{12}$/, message: 'CCCD phải có đúng 12 chữ số!' }
                                        ]}
                                    >
                                        <Input
                                            placeholder="Nhập 12 số CCCD"
                                            maxLength={12}
                                            prefix={<IdcardOutlined className="text-gray-400" />}
                                            onKeyDown={(e) => {
                                                const allowedKeys = ["Backspace", "Tab", "Delete", "ArrowLeft", "ArrowRight"];
                                                if (!/[0-9]/.test(e.key) && !allowedKeys.includes(e.key)) {
                                                    e.preventDefault();
                                                }
                                            }}
                                        />
                                    </Form.Item>
                                </Col>

                                {/* Họ và tên */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Họ và Tên</span>}
                                        name="fullName"
                                        rules={[
                                            { required: true, message: 'Vui lòng nhập họ tên!' },
                                            { min: 3, message: 'Họ tên phải có ít nhất 3 ký tự!' }
                                        ]}
                                    >
                                        <Input
                                            placeholder="Nhập họ và tên đầy đủ"
                                            prefix={<UserOutlined className="text-gray-400" />}
                                        />
                                    </Form.Item>
                                </Col>

                                {/* Số điện thoại */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Số Điện Thoại</span>}
                                        name="phone"
                                        rules={[
                                            { required: true, message: 'Vui lòng nhập số điện thoại!' },
                                            { pattern: /^[0-9]{10}$/, message: 'Số điện thoại phải có 10 chữ số!' }
                                        ]}
                                    >
                                        <Input
                                            placeholder="Nhập số điện thoại"
                                            maxLength={10}
                                            prefix={<PhoneOutlined className="text-gray-400" />}
                                            onKeyDown={(e) => {
                                                const allowedKeys = ["Backspace", "Tab", "Delete", "ArrowLeft", "ArrowRight"];
                                                if (!/[0-9]/.test(e.key) && !allowedKeys.includes(e.key)) {
                                                    e.preventDefault();
                                                }
                                            }}
                                        />
                                    </Form.Item>
                                </Col>

                                {/* Ngày sinh */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Ngày Tháng Năm Sinh</span>}
                                        name="dateOfBirth"
                                        rules={[
                                            { required: true, message: 'Vui lòng chọn ngày sinh!' },
                                            {
                                                validator: (_, value) => {
                                                    if (value && value.isAfter(dayjs())) {
                                                        return Promise.reject('Ngày sinh không được trong tương lai!');
                                                    }
                                                    return Promise.resolve();
                                                }
                                            }
                                        ]}
                                    >
                                        <DatePicker
                                            placeholder="Chọn ngày sinh"
                                            format="DD/MM/YYYY"
                                            className="w-full"
                                            disabledDate={(current) => current && current > dayjs()}
                                            suffixIcon={<CalendarOutlined />}
                                        />
                                    </Form.Item>
                                </Col>

                                {/* Dân tộc */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Dân Tộc</span>}
                                        name="ethnicity"
                                        rules={[{ required: true, message: 'Vui lòng nhập dân tộc!' }]}
                                    >
                                        <Input placeholder="Nhập dân tộc (VD: Kinh)" />
                                    </Form.Item>
                                </Col>

                                {/* Nghề nghiệp */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Nghề Nghiệp</span>}
                                        name="occupation"
                                        rules={[{ required: true, message: 'Vui lòng nhập nghề nghiệp!' }]}
                                    >
                                        <Input placeholder="Nhập nghề nghiệp" />
                                    </Form.Item>
                                </Col>

                                {/* Giới tính */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Giới Tính</span>}
                                        name="gender"
                                        rules={[{ required: true, message: 'Vui lòng chọn giới tính!' }]}
                                    >
                                        <Radio.Group className="w-full">
                                            <Radio value="male">Nam</Radio>
                                            <Radio value="female">Nữ</Radio>
                                        </Radio.Group>
                                    </Form.Item>
                                </Col>
                            </Row>
                        </div>

                        {/* Địa chỉ */}
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-emerald-700 mb-4 border-b pb-2">
                                Địa chỉ
                            </h3>
                            <div className="">
                                <Form.Item
                                    label={<span className="font-semibold">Tỉnh/Thành phố</span>}
                                    name="province"
                                    rules={[{ required: true, message: 'Vui lòng chọn tỉnh!' }]}
                                >
                                    <div>
                                        <Provinces onSelect={(address) => setFullAddress(address)} />
                                    </div>
                                </Form.Item>
                            </div>

                            {fullAddress && (
                                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 mb-4">
                                    <p className="text-sm text-emerald-700">
                                        <strong>Địa chỉ đầy đủ:</strong> {form.getFieldValue('address') ? `${form.getFieldValue('address')}, ` : ''}{fullAddress}
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Buttons */}
                        <div className="flex gap-4 justify-end pt-4 border-t">
                            <Button size="large" onClick={handleReset} disabled={loading}>
                                Làm mới
                            </Button>
                            <Button type="primary" htmlType="submit" size="large" loading={loading}
                                className="bg-emerald-600 hover:bg-emerald-700 min-w-[120px]"
                            >
                                Đăng ký
                            </Button>
                        </div>
                    </Form>
                </Card>

                {/* Helper text */}
                <div className="text-center mt-4 text-gray-500 text-sm">
                    <p>Thông tin của bạn sẽ được bảo mật tuyệt đối</p>
                </div>
            </div>
        </div>
    );
};

export default Register;