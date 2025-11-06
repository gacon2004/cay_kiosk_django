import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const checkInsuranceByCitizenID = async (citizenId: string) => {
    return await axios.get(`${API_URL}/insurance/${citizenId}`, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
}