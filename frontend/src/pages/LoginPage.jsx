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
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-50 via-indigo-50 to-blue-100">
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_25%,rgba(59,130,246,0.07),transparent_35%),radial-gradient(circle_at_82%_30%,rgba(79,70,229,0.08),transparent_32%),radial-gradient(circle_at_50%_80%,rgba(99,102,241,0.05),transparent_32%)]" />
                <div className="absolute inset-6 rounded-[2.75rem] border border-white/70 bg-white/35 shadow-[0_25px_80px_rgba(79,70,229,0.08)] backdrop-blur" />
                <div className="absolute -left-24 bottom-6 h-64 w-72 rotate-6 rounded-3xl bg-gradient-to-br from-blue-500/18 via-indigo-400/10 to-white/0 blur-3xl" />
                <div className="absolute right-0 -top-10 h-56 w-56 -rotate-6 rounded-full bg-gradient-to-br from-indigo-500/18 via-blue-400/10 to-white/0 blur-3xl" />
                <div className="absolute inset-x-12 top-10 h-20 rounded-3xl border border-white/60 bg-white/35 shadow-[0_16px_50px_rgba(15,23,42,0.06)]" />
            </div>

            <div className="relative max-w-2xl w-full px-4">
                <div className="flex flex-col gap-3 mb-10 text-center">
                    <div className="mx-auto inline-flex items-center gap-3 rounded-full bg-white/85 px-4 py-2 shadow-lg shadow-blue-200/50 backdrop-blur">
                        <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white font-semibold tracking-tight shadow-inner shadow-blue-900/20 ring-2 ring-white/70">
                            <span>AHF</span>
                            <span className="absolute inset-0 rounded-2xl border border-white/60" />
                        </div>
                        <div className="text-left">
                            <p className="text-[11px] uppercase tracking-[0.22em] text-blue-800">Intradepartmental Consults</p>
                            <p className="text-sm font-semibold text-gray-800">Allied Hospital Faisalabad · FMU Affiliated</p>
                        </div>
                    </div>
                    <p className="text-sm text-gray-600">Official portal for coordinated consultations and referral follow-up.</p>
                </div>

                <div className="grid gap-6 rounded-3xl bg-white/95 p-8 shadow-2xl shadow-blue-200/60 backdrop-blur-lg border border-white/70">
                    <div className="text-center space-y-1">
                        <h1 className="text-3xl font-bold text-gray-900">Consultation Access</h1>
                        <p className="text-gray-600">Sign in to continue your Allied Hospital workflow</p>
                    </div>

                    {error && (
                        <div className="mb-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700" role="alert" aria-live="polite">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid gap-2">
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                Email Address
                            </label>
                            <input
                                id="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="your.email@fmu.edu.pk"
                            />
                        </div>

                        <div className="grid gap-2">
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                autoComplete="current-password"
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

                    <div className="grid gap-3 rounded-2xl border border-dashed border-blue-100 bg-blue-50/70 p-4 text-sm text-gray-700">
                        <div className="flex items-center gap-2 font-semibold text-blue-900">
                            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 ring-1 ring-blue-200">i</span>
                            Secure portal for Allied Hospital teams
                        </div>
                        <div className="grid gap-2 text-gray-600">
                            <p>Optimized for intradepartmental referrals and follow-up across Allied Hospital Faisalabad and Faisalabad Medical University.</p>
                            <p className="text-blue-800 font-medium">For access issues, contact the FMU IT cell to confirm your credentials.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
