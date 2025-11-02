'use client';

import PatientInfo from '@/app/components/PatientInfo';
import PrintTicket from '@/app/components/PrintTicket';
import ProgressBar from '@/app/components/ProgressBar';
import ServiceSelection from '@/app/components/ServiceSelection';
import { useAppContext } from '@/app/context/AppContext';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHouse } from '@fortawesome/free-solid-svg-icons';

const BHYTFlow = () => {
    const { currentStep, setCurrentStep } = useAppContext();
    const router = useRouter();

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    useEffect(() => {
        if (currentStep === 0) {
            router.push('/');
            setCurrentStep(1);
        }
    }, [currentStep]);

    const renderStep = () => {
        switch (currentStep) {
            case 1:
                return <PatientInfo />;
            case 2:
                return <ServiceSelection />;
            case 3:
                return <PrintTicket />;
            default:
                return <PatientInfo />;
        }
    };
    return (
        <div className="min-h-screen">
            {/* Header */}
            <div className="bg-background fixed w-full z-9999 shadow-sm border-b border-[#e4e6eb]">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => handleBack()}
                            className="flex items-center space-x-2 text-while hover:text-gray-900 transition-colors duration-200 cursor-pointer"
                        >
                            <ArrowLeft size={24} />
                            <span className="text-lg text-while">Quay lại</span>
                        </button>

                        <h1 className="text-2xl font-bold text-while">
                            Đăng Ký Khám Bệnh
                        </h1>
                        <div className="w-9 h-9 flex items-center justify-center">
                            <Link href="/" onClick={() => setCurrentStep(1)}>
                                <FontAwesomeIcon
                                    icon={faHouse}
                                    style={{
                                        color: '#ffffff',
                                        width: 30,
                                        height: 30,
                                    }}
                                />
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full">
                <ProgressBar />
            </div>

            {/* Main Content */}
            <div className="bg-[#e6ecff] min-h-[calc(100vh)]">
                <div className="max-w-6xl mx-auto px-6 pt-50 pb-20 ">
                    {renderStep()}
                </div>
            </div>

            {/* Footer */}
            <footer className="w-full p-5 bg-background text-center text-text fixed bottom-0">
                <div className="max-w-6xl mx-auto ">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="text-sm text-while">
                                Phiên bản: v1.0.0
                            </div>
                        </div>
                        <div className="text-sm text-while">
                            © 2025 Hệ Thống Y Tế
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default BHYTFlow;
