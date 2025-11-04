import Footer from "@/components/footer";
import Header from "@/components/header";

const ClientLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="h-screen w-screen overflow-auto">
            <div className="mb-[68px]">
                <Header />
            </div>
            <main className="py-2">
                {children}
            </main>
            <Footer />
        </div>
    );
}

export default ClientLayout;