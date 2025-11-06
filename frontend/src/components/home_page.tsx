'use client';
import { useGlobalContext } from "@/context/app_context";
import { LoadingOutlined } from "@ant-design/icons";
import { Modal } from "antd";
import { useState } from "react";
import { useRouter } from "next/navigation";


function HomePage() {
    const [localLoading, setLocalLoading] = useState(false);
    const { setMode } = useGlobalContext()
    const button = ['Khám Bảo Hiểm', 'Khám dịch vụ'];
    const router = useRouter();
    const handleChange = (text: string) => {
        setLocalLoading(true);
        if (text === 'Khám Bảo Hiểm') {
            setMode('insurance');
        } else {
            setMode('non-insurance');
        }
        setTimeout(()=>{
            setLocalLoading(false);
            router.push('/nhap-cccd')
        }, 1000);
    }
    return (
        <>
            {/* modal load */}
            <Modal
                open={localLoading}
                footer={null}
                closable={false}
                centered
                maskClosable={false}
                styles={{ body: { textAlign: "center" } }}
            >
                <LoadingOutlined spin style={{ fontSize: 48, color: "#2563eb" }} className="mb-3" />
                <div className="text-lg font-semibold loading-dots">Đang xử lý, vui lòng chờ</div>
            </Modal>
            <div className={`transition-all duration-300 ${localLoading ? 'blur-sm ' : ''}`}>
                <div className='text-center px-7 py-8 rounded-lg'>
                    <div className='mb-3 text-colorOne font-bold text-[18px] lg:text-[25px]'>
                        <h1>Lựa chọn hình thức khám</h1>
                    </div>
                    <div className='flex justify-center'>
                        <div className='grid grid-cols-2 place-content-center w-full gap-4 sm:w-[80%] lg:w-[45vw]'>
                            {button.map((text, i) => (
                                <div key={i} className='flex h-full' onClick={() => handleChange(text)}>
                                    <div className='flex items-center justify-center w-full bg-linear-to-r from-green-400 to-emerald-500 text-white rounded-xl hover:from-green-500 hover:to-emerald-600 hover:scale-105 transition-all duration-500 ease-in-out'>
                                        <button className='cursor-pointer p-2 text-[14px] sm:text-[18px] font-semibold lg:text-[22px] '>{text}</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
export default HomePage;