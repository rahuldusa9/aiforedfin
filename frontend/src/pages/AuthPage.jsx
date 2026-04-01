import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { registerUser, loginUser } from '../api';
import { BookOpen, User, Mail, Lock, ArrowRight, Sparkles } from 'lucide-react';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
  });

  const updateField = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!form.username.trim() || !form.password.trim()) {
      toast.error('Username and password are required.');
      return;
    }
    if (!isLogin && !form.email.trim()) {
      toast.error('Email is required for registration.');
      return;
    }
    if (form.password.length < 4) {
      toast.error('Password must be at least 4 characters.');
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        const res = await loginUser({
          username: form.username,
          password: form.password,
        });
        login(res.data);
        toast.success(`Welcome back, ${res.data.full_name || res.data.username}!`);
      } else {
        const res = await registerUser({
          username: form.username,
          email: form.email,
          password: form.password,
          full_name: form.full_name,
        });
        login(res.data);
        toast.success('Account created! Welcome aboard.');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong. Try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-black" />
            </div>
            <div className="text-left">
              <h1 className="text-xl font-bold text-white tracking-tight">AI FOR EDUCATION</h1>
              <p className="text-xs text-gray-500 tracking-widest uppercase">Adaptive Learning System</p>
            </div>
          </div>
          <div className="flex items-center gap-2 justify-center text-gray-400 text-sm">
            <Sparkles className="w-4 h-4" />
            <span>Powered by AI & Machine Learning</span>
          </div>
        </div>

        {/* Card */}
        <div className="bg-gray-950 border border-gray-800 rounded-2xl p-8">
          {/* Tab Switch */}
          <div className="flex bg-gray-900 rounded-lg p-1 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2.5 text-sm font-medium rounded-md transition-all ${
                isLogin ? 'bg-white text-black' : 'text-gray-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2.5 text-sm font-medium rounded-md transition-all ${
                !isLogin ? 'bg-white text-black' : 'text-gray-400 hover:text-white'
              }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name (Register only) */}
            {!isLogin && (
              <div>
                <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={form.full_name}
                    onChange={(e) => updateField('full_name', e.target.value)}
                    placeholder="John Doe"
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white text-sm placeholder-gray-600 focus:border-white focus:outline-none transition-colors"
                  />
                </div>
              </div>
            )}

            {/* Username */}
            <div>
              <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  value={form.username}
                  onChange={(e) => updateField('username', e.target.value)}
                  placeholder="your_username"
                  required
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white text-sm placeholder-gray-600 focus:border-white focus:outline-none transition-colors"
                />
              </div>
            </div>

            {/* Email (Register only) */}
            {!isLogin && (
              <div>
                <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => updateField('email', e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white text-sm placeholder-gray-600 focus:border-white focus:outline-none transition-colors"
                  />
                </div>
              </div>
            )}

            {/* Password */}
            <div>
              <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="password"
                  value={form.password}
                  onChange={(e) => updateField('password', e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white text-sm placeholder-gray-600 focus:border-white focus:outline-none transition-colors"
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              ) : (
                <>
                  {isLogin ? 'Sign In' : 'Create Account'}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-gray-600 text-xs mt-6">
          AI For Education &copy; {new Date().getFullYear()} — Adaptive Intelligent Learning
        </p>
      </div>
    </div>
  );
}
