import RequestForm from '../components/RequestForm';
import { PackageSearch } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 py-4 px-6 shadow-sm">
        <div className="max-w-5xl mx-auto flex items-center gap-2">
          <PackageSearch className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold text-slate-800 tracking-tight">ConstructProcure AI</h1>
        </div>
      </header>
      
      <main className="flex-1 max-w-5xl mx-auto w-full p-6">
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
      </main>
    </div>
  );
}
