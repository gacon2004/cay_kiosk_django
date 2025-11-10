import InputCitizenID from "@/components/input_citizen_id"
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Nhập CCCD ",
    description: "Nhập số CCCD để tiếp tục.",
};

const InputCitizenIdPage = () => {
    return (
        <>
            <InputCitizenID />
        </>
    )
}

export default InputCitizenIdPage;