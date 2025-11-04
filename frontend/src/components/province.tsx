'use client';
import { Col, Row, Select, Spin } from "antd";
import { useState, useEffect } from "react";

interface Ward {
    name: string;
    mergedFrom?: string[];
}

interface ProvinceData {
    id: string;
    province: string;
    licensePlates: string[];
    wards: Ward[];
}

interface ApiResponseList {
    success: boolean;
    data: ProvinceData[];
}

interface ApiResponseSingle {
    success: boolean;
    data: ProvinceData;
    timestamp?: string;
}

interface ProvincesProps {
    onSelect?: (address: string) => void;
}

const Provinces = ({ onSelect }: ProvincesProps) => {
    const [provinces, setProvinces] = useState<string[]>([]);
    const [wards, setWards] = useState<Ward[]>([]);
    const [selectedProvince, setSelectedProvince] = useState('');
    const [selectedWard, setSelectedWard] = useState('');
    const [loadingProvinces, setLoadingProvinces] = useState(false);
    const [loadingWards, setLoadingWards] = useState(false);

    useEffect(() => {
        const fetchProvinces = async () => {
            setLoadingProvinces(true);
            try {
                const response = await fetch('/api/provinces');
                const result: ApiResponseList = await response.json();
                if (result.success && result.data.length > 0) {
                    setProvinces(result.data.map(item => item.province));
                }
            } catch (error) {
                console.error('Error fetching provinces:', error);
            } finally {
                setLoadingProvinces(false);
            }
        };
        fetchProvinces();
    }, []);

    useEffect(() => {
        const fetchWards = async () => {
            if (selectedProvince) {
                setLoadingWards(true);
                try {
                    const response = await fetch(`/api/provinces?province=${encodeURIComponent(selectedProvince)}`);
                    const result: ApiResponseSingle = await response.json();
                    
                    // API trả về object, không phải array
                    if (result.success && result.data) {
                        setWards(result.data.wards || []);
                    } else {
                        setWards([]);
                    }
                } catch (error) {
                    console.error("Error fetching wards:", error);
                    setWards([]);
                } finally {
                    setLoadingWards(false);
                }
            } else {
                setWards([]);
            }
        };
        fetchWards();
    }, [selectedProvince]);

    useEffect(() => {
        if (selectedProvince && selectedWard) {
            onSelect?.(`${selectedWard}, ${selectedProvince}`);
        }
    }, [selectedProvince, selectedWard, onSelect]);

    return (
        <Row gutter={[10, 10]}>
            <Col xs={24} md={12}>
                <Select
                    placeholder="Chọn tỉnh/thành phố"
                    allowClear
                    showSearch
                    value={selectedProvince || undefined}
                    onChange={(v) => { setSelectedProvince(v || ''); setSelectedWard(''); }}
                    options={provinces.map(p => ({ label: p, value: p }))}
                    loading={loadingProvinces}
                    notFoundContent={loadingProvinces ? <Spin size="small" /> : 'Không có dữ liệu'}
                    className="w-full"
                />
            </Col>
            <Col xs={24} md={12}>
                <Select
                    placeholder="Chọn phường/xã"
                    allowClear
                    showSearch
                    value={selectedWard || undefined}
                    onChange={(v) => setSelectedWard(v || '')}
                    options={wards.map((w, i) => ({ label: w.name, value: w.name, key: i }))}
                    disabled={!selectedProvince}
                    loading={loadingWards}
                    notFoundContent={loadingWards ? <Spin size="small" /> : 'Không có dữ liệu'}
                    className="w-full"
                />
            </Col>
        </Row>
    );
};

export default Provinces;
