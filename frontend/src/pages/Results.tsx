import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { ProcurementStatusResponse, ProcurementResultsResponse } from '../api/client';
import { procurementApi } from '../api/client';
import StatusTracker from '../components/StatusTracker';
import SupplierTable from '../components/SupplierTable';
import FinalRecommendation from '../components/FinalRecommendation';
import { PackageSearch, ArrowLeft, Loader2, RefreshCw } from 'lucide-react';

export default function Results() {
  const { requestId } = useParams<{ requestId: string }>();
  const [status, setStatus] = useState<ProcurementStatusResponse | null>(null);
  const [results, setResults] = useState<ProcurementResultsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  const fetchStatusAndResults = async () => {
    if (!requestId) return;
    try {
      const statusData = await procurementApi.getStatus(requestId);
      setStatus(statusData);

      if (statusData.pipeline_status === 'completed' || statusData.pipeline_status === 'failed') {
        setIsPolling(false);
        const resultsData = await procurementApi.getResults(requestId);
        setResults(resultsData);
      }
    } catch (err: any) {
      console.error(err);
      setError('Failed to load status. The request ID might be invalid.');
      setIsPolling(false);
    }
  };

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    let mounted = true;

    const poll = async () => {
      if (!isPolling || !mounted) return;
      await fetchStatusAndResults();
      
      // If still polling after fetch, schedule next poll
      if (mounted && isPolling) {
        timeoutId = setTimeout(poll, 3000);
      }
    };

    poll();

    return () => {
      mounted = false;
      clearTimeout(timeoutId);
    };
  }, [requestId, isPolling]); // Note: isPolling changes will re-trigger and handle cleanup appropriately


  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 py-4 px-6 shadow-sm sticky top-0 z-50">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <PackageSearch className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold text-slate-800 tracking-tight">ConstructProcure AI</h1>
          </Link>
          <Link to="/" className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
            <ArrowLeft className="w-4 h-4" /> New Request
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-900">Procurement Dashboard</h2>
          {isPolling && (
            <div className="flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Processing Request...
            </div>
          )}
        </div>

        {error && (
          <div className="p-4 bg-red-50 text-red-700 rounded-md border border-red-200">
            {error}
          </div>
        )}

        {!status && !error && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin mb-4" />
            <p>Loading pipeline status...</p>
          </div>
        )}

        {status && <StatusTracker status={status} />}
        
        {results && <SupplierTable results={results} />}
        
        {results && <FinalRecommendation results={results} />}
        
        {!isPolling && !results && status?.pipeline_status !== 'failed' && !error && (
          <div className="p-4 bg-amber-50 text-amber-700 rounded-md border border-amber-200 text-sm">
            Could not retrieve final results. The pipeline may have encountered an issue or is still initializing.
          </div>
        )}
        
        {status?.pipeline_status === 'failed' && (
          <div className="p-4 bg-red-50 text-red-700 rounded-md border border-red-200 text-sm">
            The pipeline failed to complete successfully. Please review the backend logs.
          </div>
        )}
      </main>
    </div>
  );
}
