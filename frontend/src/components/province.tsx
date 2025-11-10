'use client';
import { Col, Row, Select, Spin } from "antd";
import { useState, useEffect } from "react";
import type { Province, Ward } from "@/api/provinces/request";
import { getProvinces, getProvinceDetail } from "@/api/provinces/request";

interface ProvincesProps {
    value?: { province: Province | null; ward: Ward | null };
    onChange?: (value: { province: Province | null; ward: Ward | null }) => void;
    onSelect?: (address: string) => void;
}

const Provinces = ({ value, onChange, onSelect }: ProvincesProps) => {
    const [provinces, setProvinces] = useState<Province[]>([]);
    const [wards, setWards] = useState<Ward[]>([]);
    const [selectedProvince, setSelectedProvince] = useState<Province | null>(value?.province || null);
    const [selectedWard, setSelectedWard] = useState<Ward | null>(value?.ward || null);
    const [loadingProvinces, setLoadingProvinces] = useState(false);
    const [loadingWards, setLoadingWards] = useState(false);

    // Sync with external value
    useEffect(() => {
        setSelectedProvince(value?.province || null);
        setSelectedWard(value?.ward || null);
    }, [value]);

    // Update external value when internal state changes
    useEffect(() => {
        onChange?.({ 
            province: selectedProvince, 
            ward: selectedWard 
        });
    }, [selectedProvince, selectedWard, onChange]);

    useEffect(() => {
        const fetchProvinces = async () => {
            setLoadingProvinces(true);
            try {
                const data = await getProvinces();
                setProvinces(data);
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
                    const detail = await getProvinceDetail(selectedProvince.code);
                    setWards(detail.wards || []);
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
            onSelect?.(`${selectedWard.name}, ${selectedProvince.name}`);
        }
    }, [selectedProvince, selectedWard, onSelect]);

    return (
        <Row gutter={[10, 10]}>
            <Col xs={24} md={12}>
                <Select
                    placeholder="Chọn tỉnh/thành phố"
                    allowClear
                    showSearch
                    value={selectedProvince?.code}
                    onChange={(v) => {
                        const p = provinces.find(p => p.code === v);
                        setSelectedProvince(p || null);
                        setSelectedWard(null);
                    }}
                    options={provinces.map(p => ({ label: p.name, value: p.code }))}
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
                    value={selectedWard?.code}
                    onChange={(v) => setSelectedWard(wards.find(w => w.code === v) || null)}
                    options={wards.map((w) => ({ label: w.name, value: w.code, key: w.code }))}
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
