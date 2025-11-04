'use client'
import { HomeOutlined, LoadingOutlined } from "@ant-design/icons";
import { Spin, Tooltip } from "antd";
import { useState } from "react";

function Header() {
    const [localLoading, setLocalLoading] = useState(false);
    const handleReturnHome = () => {
        setLocalLoading(true);
        window.location.href = "/";
    }
    return (
        <>
            <Spin spinning={localLoading} fullscreen indicator={<LoadingOutlined spin />} />
            <div className='fixed top-0 flex p-4 w-full bg-colorOne z-1000 bg-emerald-800 shadow-md shadow-emerald-900/50'>
                <h1 className='flex-1 flex items-center justify-center text-white font-extrabold sm:text-[18px] md:text-[21px] lg:text-[24px] xl:text-[28px] 2xl:text-[31px] '>BỆNH VIỆN TC</h1>
                <div className='flex items-center justify-end'>
                    <Tooltip placement="bottomLeft" mouseEnterDelay={0.2} title="Trang chủ">
                        <button onClick={handleReturnHome}
                            className='hover:scale-105 transition-all duration-500 ease-in-out hover:ring-2! hover:ring-white/40! px-2 py-1 bg-white rounded-lg text-colorOne hover:text-teal-800 hover:cursor-pointer'>
                            <HomeOutlined />
                        </button>
                    </Tooltip>
                </div>
            </div>
        </>
    )
}
export default Header;