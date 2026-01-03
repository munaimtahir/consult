import { useSearchParams } from 'react-router-dom';
import PlaceholderPage from '../../components/admin/PlaceholderPage';

const SearchPage = () => {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';

    return (
        <PlaceholderPage 
            title={`Search Results: ${query}`} 
            description={`Searching for: ${query}`}
        />
    );
};

export default SearchPage;
