import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import RequestForm from '../components/RequestForm';
import { PackageSearch, Loader2, ListOrdered, Building2 } from 'lucide-react';
import { procurementApi, suppliersApi, type ActiveProcurementRequest, type SupplierDirectoryItem } from '../api/client';

export default function Home() {
  const [activeTab, setActiveTab] = useState('submit');
  const [dataSubView, setDataSubView] = useState<'requests' | 'directory'>('requests');

  const [activeRequests, setActiveRequests] = useState<ActiveProcurementRequest[]>([]);
  const [loadingActive, setLoadingActive] = useState(false);

  const [suppliers, setSuppliers] = useState<SupplierDirectoryItem[]>([]);
  const [loadingSuppliers, setLoadingSuppliers] = useState(false);

  useEffect(() => {
    if (activeTab === 'data' && dataSubView === 'requests') {
      setLoadingActive(true);
      procurementApi.getActive()
        .then(data => setActiveRequests(data))
        .catch(err => console.error(err))
        .finally(() => setLoadingActive(false));
    }
  }, [activeTab, dataSubView]);

  useEffect(() => {
    if (activeTab === 'data' && dataSubView === 'directory') {
      setLoadingSuppliers(true);
      suppliersApi.getAll()
        .then(data => setSuppliers(data))
        .catch(err => console.error(err))
        .finally(() => setLoadingSuppliers(false));
    }
  }, [activeTab, dataSubView]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 py-4 px-6 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center gap-2">
          <PackageSearch className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold text-slate-800 tracking-tight">ConstructProcure AI</h1>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full p-6">
        {/* Top-level tab nav */}
        <div className="mb-6 border-b border-slate-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('submit')}
              className={`${
                activeTab === 'submit'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Submit Request
            </button>
            <button
              onClick={() => setActiveTab('data')}
              className={`${
                activeTab === 'data'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Current Data
            </button>
          </nav>
        </div>

        {activeTab === 'submit' ? (
          <div className="grid md:grid-cols-2 gap-8 items-start">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-4">Autonomous Construction Procurement</h2>
              <p className="text-slate-600 leading-relaxed mb-6">
                Enter your material requirements below. Our multi-agent AI pipeline will automatically:
              </p>
              <ul className="space-y-3 text-slate-700">
                <li className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold">1</div>
                  Discover global suppliers
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold">2</div>
                  Extract detailed quotations
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold">3</div>
                  Score and rank suppliers on trust
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold">4</div>
                  Provide a final recommendation report
                </li>
              </ul>
            </div>
            <div>
              <RequestForm />
            </div>
          </div>
        ) : (
          <div>
            {/* Sub-navigation toggle */}
            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg w-fit mb-6">
              <button
                onClick={() => setDataSubView('requests')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  dataSubView === 'requests'
                    ? 'bg-white text-slate-800 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <ListOrdered className="w-4 h-4" />
                Active Requests
              </button>
              <button
                onClick={() => setDataSubView('directory')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  dataSubView === 'directory'
                    ? 'bg-white text-slate-800 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Building2 className="w-4 h-4" />
                Supplier Directory
              </button>
            </div>

            {/* Active Requests View */}
            {dataSubView === 'requests' && (
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-4 border-b border-slate-200 bg-slate-50">
                  <h2 className="text-lg font-semibold text-slate-800">Active Leads</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Material</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Qty/Unit</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Target Region</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Quality</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                      {loadingActive ? (
                        <tr>
                          <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                            <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                            <p>Loading active requests...</p>
                          </td>
                        </tr>
                      ) : activeRequests.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                            No active leads found.
                          </td>
                        </tr>
                      ) : (
                        activeRequests.map((req) => (
                          <tr key={req.id} className="hover:bg-slate-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                              {new Date(req.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 font-medium">
                              {req.material_type}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                              {req.quantity} {req.unit}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                              {req.target_country_code === 'GL' ? 'Global' : req.target_country_code}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                              {req.quality_grade}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                req.status === 'complete' ? 'bg-green-100 text-green-800' :
                                req.status === 'failed' ? 'bg-red-100 text-red-800' :
                                'bg-blue-100 text-blue-800'
                              }`}>
                                {req.status}
                              </span>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Supplier Directory View */}
            {dataSubView === 'directory' && (
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-800">Supplier Directory</h2>
                    <p className="text-xs text-slate-500 mt-0.5">Click a supplier name to view their full profile.</p>
                  </div>
                  {!loadingSuppliers && (
                    <span className="text-sm text-slate-500">{suppliers.length} suppliers registered</span>
                  )}
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Supplier Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Location</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Core Materials</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                      {loadingSuppliers ? (
                        <tr>
                          <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                            <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                            <p>Loading supplier directory...</p>
                          </td>
                        </tr>
                      ) : suppliers.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                            No suppliers found in the directory.
                          </td>
                        </tr>
                      ) : (
                        suppliers.map((supplier) => (
                          <tr key={supplier.id} className="hover:bg-slate-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Link
                                to={`/supplier/${supplier.id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                              >
                                {supplier.name}
                              </Link>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              {supplier.email}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                              <span>{supplier.city}</span>
                              <span className="ml-2 px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-xs font-mono font-semibold">
                                {supplier.country_code}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex flex-wrap gap-1.5">
                                {supplier.material_categories.map((mat) => (
                                  <span
                                    key={mat}
                                    className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full text-xs font-medium"
                                  >
                                    {mat}
                                  </span>
                                ))}
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
