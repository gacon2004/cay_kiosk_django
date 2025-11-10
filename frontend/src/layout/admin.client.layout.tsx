'use client'

const AdminClientLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="h-screen w-screen overflow-auto bg-gray-50">
            <main className="h-full">
                {children}
            </main>
        </div>
    );
}

export default AdminClientLayout;