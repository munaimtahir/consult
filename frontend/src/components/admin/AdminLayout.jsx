import AdminSidebar from './AdminSidebar';

const AdminLayout = ({ children }) => {
    return (
        <div className="flex">
            <AdminSidebar />
            <main className="flex-1 p-8">{children}</main>
        </div>
    );
};

export default AdminLayout;
