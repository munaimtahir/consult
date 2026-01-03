const PlaceholderPage = ({ title, description }) => {
    return (
        <div className="bg-white rounded-2xl shadow-md border border-gray-200 transition-all duration-150 p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
            {description && (
                <p className="text-gray-600 mb-4">{description}</p>
            )}
            <div className="mt-8 p-8 bg-gray-50 rounded-lg text-center">
                <p className="text-gray-500">This page is under development.</p>
            </div>
        </div>
    );
};

export default PlaceholderPage;
