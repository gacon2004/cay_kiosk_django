"use client";
import type { Province, Ward } from "@/api/provinces/request";
import { Button, DatePicker, Form, Input, Radio, Row, Col, Card, message, Select, Modal } from "antd";
import { IdcardOutlined, PhoneOutlined, UserOutlined, CalendarOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Provinces from "./province";
import dayjs from "dayjs";
import { register } from "@/api/request";
import { saveUserInfo } from "@/utils/session";

// Types
interface RegisterFormValues {
    citizen_id: string;
    phone_number: string;
    fullname: string;
    address: string;
    occupation: string;
    dob: dayjs.Dayjs;
    ethnicity: string;
    gender: 'male' | 'female';
}

interface UserData {
    citizen_id: string;
    phone_number: string;
    fullname: string;
    address: string;
    occupation: string;
    dob: string;
    ethnicity: string;
    gender: 'male' | 'female';
}

const Register = () => {
    const [form] = Form.useForm();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [provinceValue, setProvinceValue] = useState<{ province: Province | null; ward: Ward | null }>({ province: null, ward: null });
    const [modalVisible, setModalVisible] = useState(false);
    const [userData, setUserData] = useState<UserData | null>(null);

    const onFinish = async (values: RegisterFormValues) => {
        setLoading(true);
        try {
            const address = provinceValue && provinceValue.ward && provinceValue.province
                ? `${provinceValue.ward.name}, ${provinceValue.province.name}`
                : '';
            const formData = {
                ...values,
                dob: values.dob.format('YYYY-MM-DD'),
                address,
            };

            console.log('Form Data:', formData);

            const response = await register(formData);

            if (response.status === 201) {
                setUserData(formData as UserData);
                // Lưu thông tin user vào sessionStorage
                saveUserInfo(formData as UserData);
                setModalVisible(true);
            } else if (response.status === 400) {
                message.error('Đăng ký thất bại. Vui lòng kiểm tra lại thông tin!');
            } else {
                message.error('Đăng ký thất bại. Vui lòng thử lại!');
            }

        } catch (error) {
            message.error('Đăng ký thất bại. Vui lòng thử lại!');
            console.error('Registration error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleNextStep = () => {
        setModalVisible(false);
        router.push('/chon-dich-vu');
    };

    const handleReset = () => {
        form.resetFields();
        setProvinceValue({ province: null, ward: null });
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
                                        name="citizen_id"
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
                                        name="fullname"
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
                                        name="phone_number"
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
                                        name="dob"
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
                                        rules={[{ required: true, message: 'Vui lòng chọn dân tộc!' }]}
                                    >
                                        <Select
                                            showSearch
                                            placeholder="Chọn dân tộc"
                                            optionFilterProp="children"
                                            filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
                                            options={[
                                                { label: "Kinh", value: "Kinh" },
                                                { label: "Tày", value: "Tày" },
                                                { label: "Thái", value: "Thái" },
                                                { label: "Mường", value: "Mường" },
                                                { label: "Khmer", value: "Khmer" },
                                                { label: "Hoa", value: "Hoa" },
                                                { label: "Nùng", value: "Nùng" },
                                                { label: "H'Mông", value: "H'Mông" },
                                                { label: "Dao", value: "Dao" },
                                                { label: "Gia-rai", value: "Gia-rai" },
                                                { label: "Ngái", value: "Ngái" },
                                                { label: "Ê-đê", value: "Ê-đê" },
                                                { label: "Ba Na", value: "Ba Na" },
                                                { label: "Xơ Đăng", value: "Xơ Đăng" },
                                                { label: "Sán Chay", value: "Sán Chay" },
                                                { label: "Cơ Ho", value: "Cơ Ho" },
                                                { label: "Chăm", value: "Chăm" },
                                                { label: "Sán Dìu", value: "Sán Dìu" },
                                                { label: "Hrê", value: "Hrê" },
                                                { label: "Mnông", value: "Mnông" },
                                                { label: "Ra Glai", value: "Ra Glai" },
                                                { label: "Xtiêng", value: "Xtiêng" },
                                                { label: "Bru-Vân Kiều", value: "Bru-Vân Kiều" },
                                                { label: "Thổ", value: "Thổ" },
                                                { label: "Giáy", value: "Giáy" },
                                                { label: "Cơ Tu", value: "Cơ Tu" },
                                                { label: "Gié-Triêng", value: "Gié-Triêng" },
                                                { label: "Mạ", value: "Mạ" },
                                                { label: "Khơ Mú", value: "Khơ Mú" },
                                                { label: "Co", value: "Co" },
                                                { label: "Tà Ôi", value: "Tà Ôi" },
                                                { label: "Chơ Ro", value: "Chơ Ro" },
                                                { label: "Kháng", value: "Kháng" },
                                                { label: "Xinh Mun", value: "Xinh Mun" },
                                                { label: "Hà Nhì", value: "Hà Nhì" },
                                                { label: "Chu Ru", value: "Chu Ru" },
                                                { label: "Lào", value: "Lào" },
                                                { label: "La Chí", value: "La Chí" },
                                                { label: "La Ha", value: "La Ha" },
                                                { label: "Phù Lá", value: "Phù Lá" },
                                                { label: "La Hủ", value: "La Hủ" },
                                                { label: "Lự", value: "Lự" },
                                                { label: "Lô Lô", value: "Lô Lô" },
                                                { label: "Chứt", value: "Chứt" },
                                                { label: "Mảng", value: "Mảng" },
                                                { label: "Pà Thẻn", value: "Pà Thẻn" },
                                                { label: "Co Lao", value: "Co Lao" },
                                                { label: "Cống", value: "Cống" },
                                                { label: "Bố Y", value: "Bố Y" },
                                                { label: "Si La", value: "Si La" },
                                                { label: "Pu Péo", value: "Pu Péo" },
                                                { label: "Brâu", value: "Brâu" },
                                                { label: "Ơ Đu", value: "Ơ Đu" },
                                                { label: "Rơ Măm", value: "Rơ Măm" },
                                                { label: "Người nước ngoài", value: "Người nước ngoài" },
                                            ]}
                                        />
                                    </Form.Item>
                                </Col>

                                {/* Nghề nghiệp */}
                                <Col xs={24} md={12} lg={8} xl={6}>
                                    <Form.Item
                                        label={<span className="font-semibold">Nghề Nghiệp</span>}
                                        name="occupation"
                                        rules={[{ required: true, message: 'Vui lòng chọn nghề nghiệp!' }]}
                                    >
                                        <Select
                                            showSearch
                                            placeholder="Chọn nghề nghiệp"
                                            optionFilterProp="children"
                                            filterOption={(input, option) => (option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
                                            options={[
                                                { label: "Học sinh", value: "Học sinh" },
                                                { label: "Sinh viên", value: "Sinh viên" },
                                                { label: "Công nhân", value: "Công nhân" },
                                                { label: "Nông dân", value: "Nông dân" },
                                                { label: "Cán bộ nhà nước", value: "Cán bộ nhà nước" },
                                                { label: "Giáo viên", value: "Giáo viên" },
                                                { label: "Bác sĩ", value: "Bác sĩ" },
                                                { label: "Kỹ sư", value: "Kỹ sư" },
                                                { label: "Lái xe", value: "Lái xe" },
                                                { label: "Kinh doanh tự do", value: "Kinh doanh tự do" },
                                                { label: "Nội trợ", value: "Nội trợ" },
                                                { label: "Hưu trí", value: "Hưu trí" },
                                                { label: "Bộ đội", value: "Bộ đội" },
                                                { label: "Công an", value: "Công an" },
                                                { label: "Luật sư", value: "Luật sư" },
                                                { label: "Nhân viên văn phòng", value: "Nhân viên văn phòng" },
                                                { label: "Chưa có việc làm", value: "Chưa có việc làm" },
                                                { label: "Khác", value: "Khác" },
                                            ]}
                                        />
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
                            <Form.Item
                                label={<span className="font-semibold">Tỉnh/Thành phố, Phường/Xã</span>}
                                required
                                validateStatus={provinceValue && provinceValue.province && provinceValue.ward ? undefined : 'error'}
                                help={!(provinceValue && provinceValue.province && provinceValue.ward) ? 'Vui lòng chọn tỉnh và phường/xã!' : ''}
                            >
                                <Provinces
                                    value={provinceValue}
                                    onChange={setProvinceValue}
                                />
                            </Form.Item>
                            {provinceValue && provinceValue.ward && provinceValue.province && (
                                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 mb-4">
                                    <p className="text-sm text-emerald-700">
                                        <strong>Địa chỉ đầy đủ:</strong> {provinceValue.ward.name}, {provinceValue.province.name}
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

            {/* Success Modal */}
            <Modal
                title={null}
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={[
                    <Button key="next" type="primary" onClick={handleNextStep}>
                        Đến bước tiếp theo
                    </Button>
                ]}
                width={600}
                centered
            >
                {userData && (
                    <div className="flex flex-col items-center justify-center">
                        <CheckCircleOutlined style={{ fontSize: 64, color: "#10b981" }} className="mb-3" />
                        <div className="text-2xl font-bold text-emerald-700 mb-2 text-center">Đăng ký thành công!</div>
                        <div className="text-lg font-semibold text-emerald-600 mb-4 text-center">Thông tin đăng ký</div>
                        <div className="w-full max-w-lg text-left bg-gray-50 rounded-lg p-4 space-y-2">
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Họ và tên:</span>
                                <span className="text-gray-900 font-semibold">{userData.fullname}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số CCCD:</span>
                                <span className="text-gray-900 font-semibold">{userData.citizen_id}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Số điện thoại:</span>
                                <span className="text-gray-900">{userData.phone_number}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Ngày sinh:</span>
                                <span className="text-gray-900">{userData.dob}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Giới tính:</span>
                                <span className="text-gray-900">{userData.gender === 'male' ? 'Nam' : 'Nữ'}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Dân tộc:</span>
                                <span className="text-gray-900">{userData.ethnicity}</span>
                            </div>
                            <div className="flex justify-between border-b pb-2">
                                <span className="text-gray-600 font-medium">Nghề nghiệp:</span>
                                <span className="text-gray-900">{userData.occupation}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600 font-medium">Địa chỉ:</span>
                                <span className="text-gray-900">{userData.address}</span>
                            </div>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default Register;