import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { suppliersApi, type SupplierDirectoryItem } from '../api/client';
import { ArrowLeft, Mail, MapPin, Layers, PackageSearch, Loader2, AlertCircle } from 'lucide-react';

export default function SupplierProfile() {
  const { id } = useParams<{ id: string }>();
  const [supplier, setSupplier] = useState<SupplierDirectoryItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    suppliersApi.getById(id)
      .then(data => setSupplier(data))
      .catch(() => setError('Supplier not found or an error occurred.'))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-700/60 py-4 px-6 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PackageSearch className="w-5 h-5 text-blue-400" />
            <span className="text-sm font-semibold text-slate-300 tracking-tight">ConstructProcure AI</span>
          </div>
          <Link
            to="/"
            className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-100 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-6 py-10">
        {loading && (
          <div className="flex flex-col items-center justify-center py-32 text-slate-400">
            <Loader2 className="w-10 h-10 animate-spin mb-4 text-blue-400" />
            <p className="text-sm">Loading supplier profile...</p>
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center justify-center py-32 text-slate-400">
            <AlertCircle className="w-10 h-10 mb-4 text-red-400" />
            <p className="text-base font-medium text-slate-300">{error}</p>
            <Link to="/" className="mt-4 text-sm text-blue-400 hover:underline">← Return to Dashboard</Link>
          </div>
        )}

        {supplier && !loading && (
          <div className="space-y-8">
            {/* Profile Header */}
            <div className="pb-6 border-b border-slate-700/60">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
                      {supplier.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-white tracking-tight">{supplier.name}</h1>
                      <p className="text-sm text-slate-400">{supplier.city}</p>
                    </div>
                  </div>
                </div>
                <span className="mt-1 px-3 py-1 bg-slate-700 border border-slate-600 rounded-full text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">
                  {supplier.country_code}
                </span>
              </div>
            </div>

            {/* Info Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Email */}
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 flex items-start gap-4">
                <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                  <Mail className="w-4 h-4 text-blue-400" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider font-medium">Email</p>
                  <p className="text-sm text-slate-200 font-medium truncate">{supplier.email}</p>
                </div>
              </div>

              {/* Location */}
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 flex items-start gap-4">
                <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-4 h-4 text-emerald-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider font-medium">Location</p>
                  <p className="text-sm text-slate-200 font-medium">{supplier.city}</p>
                  <p className="text-xs text-slate-400 font-mono">{supplier.country_code}</p>
                </div>
              </div>

              {/* Category Count */}
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 flex items-start gap-4">
                <div className="w-9 h-9 rounded-lg bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                  <Layers className="w-4 h-4 text-violet-400" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider font-medium">Material Categories</p>
                  <p className="text-2xl font-bold text-white">{supplier.material_categories.length}</p>
                  <p className="text-xs text-slate-400">categories offered</p>
                </div>
              </div>
            </div>

            {/* Materials Section */}
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-6">
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Core Materials</h2>
              <div className="flex flex-wrap gap-2">
                {supplier.material_categories.map((mat) => (
                  <span
                    key={mat}
                    className="px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 text-blue-300 rounded-full text-sm font-medium"
                  >
                    {mat}
                  </span>
                ))}
              </div>
            </div>

            {/* =====================================================
                PLACEHOLDER: Procurement History & Trust Metrics
                To be implemented once scoring history API is ready.
                
                Will include:
                  - Historical composite score trend chart
                  - Past procurement requests involving this supplier
                  - Price competitiveness vs market average
                  - Quote completeness rate over time
            ====================================================== */}

          </div>
        )}
      </main>
    </div>
  );
}
