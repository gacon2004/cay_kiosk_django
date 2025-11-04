'use client'

import { createContext, useContext, useState } from "react";

// Define the type for the context value
type AppContextType = {
    mode: string;
    setMode: (mode: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export const useGlobalContext = () => {
    const context = useContext(AppContext)
    if (!context) {
        throw new Error('useGlobalContext must be used within AppProvider')
    }
    return context
}


export const AppProvider = ({ children }: { children: React.ReactNode }) => {
    const [mode, setMode] = useState<string>('')
    return (
        <AppContext.Provider value={{ mode, setMode }}>
            {children}
        </AppContext.Provider>
    )
}