import axios from "axios";

export interface Province {
  name: string;
  code: number;
  division_type: string;
  codename: string;
  phone_code: number;
  wards: Ward[];
}

export interface Ward {
  name: string;
  code: number;
  division_type: string;
  codename: string;
}

// Lấy danh sách tỉnh/thành phố
export const getProvinces = async (): Promise<Province[]> => {
  const res = await axios.get<Province[]>("https://provinces.open-api.vn/api/v2/p/");
  return res.data;
};

// Lấy chi tiết tỉnh/thành phố theo mã code (bao gồm danh sách quận/huyện, phường/xã)
export const getProvinceDetail = async (code: number): Promise<Province> => {
  const res = await axios.get<Province>(`https://provinces.open-api.vn/api/v2/p/${code}?depth=2`);
  return res.data;
};
