import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/layout/client.layout";
import { AppProvider } from "@/context/app_context";

const inter = Inter({
    subsets: ['latin'],
    display: 'swap', // Quan trọng!
    preload: true,
})

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "Kiosk TC",
    description: "Hệ thống kiosk thông minh cho bệnh viện và phòng khám. Quản lý hồ sơ sức khỏe một cách nhanh chóng và tiện lợi.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className={inter.className} suppressHydrationWarning>
            <body
                className={`${geistSans.variable} ${geistMono.variable} antialiased`}
            >
                <AppProvider>
                    {children}
                </AppProvider>
            </body>
        </html>
    );
}
