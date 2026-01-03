import AdminSidebar from './AdminSidebar';

const AdminLayout = ({ children }) => {
    return (
        <div className="min-h-screen bg-[#FAFAFA] flex">
            <div className="hidden lg:block">
                <AdminSidebar />
            </div>
            <div className="flex-1 flex flex-col min-w-0">
                <main className="flex-1 p-4 sm:p-6 lg:p-8">
                    <div className="max-w-7xl mx-auto">
                        <div className="space-y-6">
                            {children}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default AdminLayout;
