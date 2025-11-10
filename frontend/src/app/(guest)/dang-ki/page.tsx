import Register from "@/components/register";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Đăng kí thông tin",
    description: "Đăng kí thông tin người khám",
};

const RegisterPage = () => {
    return (
        <Register />
    );
}
export default RegisterPage;