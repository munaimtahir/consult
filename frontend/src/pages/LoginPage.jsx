import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Renders the login page.
 *
 * This component provides a form for users to enter their email and
 * password to authenticate. It handles the form submission, calls the
 * login function from the `AuthContext`, and navigates to the dashboard
 * on successful login.
 *
 * @returns {React.ReactElement} The rendered login page component.
 */
export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute -left-32 -top-32 h-80 w-80 rounded-full bg-blue-200 opacity-40 blur-3xl" />
                <div className="absolute right-0 bottom-0 h-72 w-72 rounded-full bg-indigo-200 opacity-40 blur-3xl" />
                <div className="absolute inset-10 rounded-3xl border border-white/50 bg-gradient-to-br from-white/40 to-white/10 shadow-inner" />
            </div>

            <div className="relative max-w-2xl w-full px-4">
                <div className="mb-6 text-center">
                    <div className="inline-flex items-center gap-3 rounded-full bg-white/80 px-4 py-2 shadow-md backdrop-blur">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-500 text-white font-semibold tracking-tight">
                            AHF
                        </div>
                        <div className="text-left">
                            <p className="text-xs uppercase tracking-[0.2em] text-blue-700">Intradepartmental Consultations</p>
                            <p className="text-sm font-medium text-gray-700">Allied Hospital Faisalabad · FMU Affiliated</p>
                        </div>
                    </div>
                </div>

                <div className="grid gap-6 rounded-3xl bg-white/90 p-8 shadow-2xl backdrop-blur">
                    <div className="text-center">
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Hospital Consult System</h1>
                        <p className="text-gray-600">Sign in to continue your clinical workflow</p>
                    </div>

                    {error && (
                        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="your.email@pmc.edu.pk"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-semibold shadow-lg shadow-blue-200 hover:from-blue-700 hover:to-indigo-700 transition-colors disabled:from-blue-300 disabled:to-blue-300 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                        </button>
                    </form>

                    <div className="grid gap-2 rounded-2xl border border-dashed border-blue-100 bg-blue-50/60 p-4 text-sm text-gray-700">
                        <div className="flex items-center gap-2 font-semibold text-blue-800">
                            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">i</span>
                            Secure portal for Allied Hospital teams
                        </div>
                        <p className="text-gray-600">
                            Optimized for intradepartmental referrals and follow-up across Allied Hospital Faisalabad and Faisalabad Medical University.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
