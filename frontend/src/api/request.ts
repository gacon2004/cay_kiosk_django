/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const checkInsuranceByCitizenID = async (citizenId: string) => {
    return await axios.post(`${API_URL}/patients/check_insurance`, { citizen_id: citizenId }, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
}

export const getPatientByCitizenID = async (citizenId: string) => {
    return await axios.get(`${API_URL}/patients/${citizenId}`, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
};

export const getServiceExams = async () => {
    return await axios.get(`${API_URL}/service-exams`, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
};

export const register = async (formData: any) => {
    return await axios.post(`${API_URL}/patients`, formData, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
}