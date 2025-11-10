// frontend/src/app/(admin)/layout.tsx
import AuthWrapper from "@/components/auth_wrapper";
import AdminClientLayout from "@/layout/admin.client.layout";

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <AdminClientLayout>
        <AuthWrapper>
            {children}
        </AuthWrapper>
    </AdminClientLayout>;
}