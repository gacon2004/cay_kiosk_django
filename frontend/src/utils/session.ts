// Utility functions for session storage management

export interface UserInfo {
    citizen_id: string;
    phone_number: string;
    fullname: string;
    address: string;
    occupation: string;
    dob: string;
    ethnicity: string;
    gender: 'male' | 'female';
}

export interface SelectedService {
    id: number;
    name: string;
    description: string;
    prices_non_insurance: number;
    prices_insurance: number;
    is_active: boolean;
}

// Save user info to session storage
export const saveUserInfo = (userInfo: UserInfo) => {
    sessionStorage.setItem('user_info', JSON.stringify(userInfo));
};

// Get user info from session storage
export const getUserInfo = (): UserInfo | null => {
    const data = sessionStorage.getItem('user_info');
    return data ? JSON.parse(data) : null;
};

// Save selected service to session storage
export const saveSelectedService = (service: SelectedService) => {
    sessionStorage.setItem('selected_service', JSON.stringify(service));
};

// Get selected service from session storage
export const getSelectedService = (): SelectedService | null => {
    const data = sessionStorage.getItem('selected_service');
    return data ? JSON.parse(data) : null;
};

// Save app mode to session storage
export const saveAppMode = (mode: string) => {
    sessionStorage.setItem('app_mode', mode);
};

// Get app mode from session storage
export const getAppMode = (): string => {
    return sessionStorage.getItem('app_mode') || '';
};

// Clear all session data
export const clearSessionData = () => {
    sessionStorage.removeItem('user_info');
    sessionStorage.removeItem('selected_service');
    sessionStorage.removeItem('app_mode');
};