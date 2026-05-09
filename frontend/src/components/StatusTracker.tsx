import type { ProcurementStatusResponse } from '../api/client';
import { CheckCircle2, Clock, PlayCircle } from 'lucide-react';

interface Props {
  status: ProcurementStatusResponse | null;
}

const PIPELINE_STAGES = [
  'request_received',
  'discovery',
  'extraction',
  'scoring',
  'analysis',
  'complete'
];

export default function StatusTracker({ status }: Props) {
  if (!status) return null;

  let currentStatusIndex = 0;
  if (status.pipeline_status === 'complete' || status.pipeline_status === 'completed') {
    currentStatusIndex = PIPELINE_STAGES.length - 1;
  } else if (status.pipeline_status === 'in_progress') {
    const agentIndex = PIPELINE_STAGES.indexOf(status.current_agent || '');
    currentStatusIndex = agentIndex !== -1 ? agentIndex : 1;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <h2 className="text-lg font-semibold mb-4 text-slate-800">Pipeline Status</h2>
      
      <div className="flex flex-col md:flex-row md:items-center gap-4 mb-6">
        <div className="flex-1 bg-slate-100 p-3 rounded text-sm">
          <span className="text-slate-500 block mb-1">Status</span>
          <span className="font-medium capitalize">{status.pipeline_status.replace('_', ' ')}</span>
        </div>
        <div className="flex-1 bg-slate-100 p-3 rounded text-sm">
          <span className="text-slate-500 block mb-1">Active Agent</span>
          <span className="font-medium">{status.current_agent || 'None'}</span>
        </div>
        <div className="flex-1 bg-slate-100 p-3 rounded text-sm">
          <span className="text-slate-500 block mb-1">Suppliers Found</span>
          <span className="font-medium">{status.supplier_count}</span>
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200 md:hidden"></div>
        <div className="flex flex-col md:flex-row justify-between relative z-10 space-y-4 md:space-y-0">
          {PIPELINE_STAGES.map((stage, index) => {
            const isCompleted = index < currentStatusIndex || status.pipeline_status === 'complete' || status.pipeline_status === 'completed';
            const isActive = index === currentStatusIndex && status.pipeline_status !== 'complete' && status.pipeline_status !== 'completed';
            const isPending = index > currentStatusIndex;

            return (
              <div key={stage} className="flex md:flex-col items-center gap-3 md:gap-2 relative z-10">
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center border-2 bg-white
                  ${isCompleted ? 'border-green-500 text-green-500' : ''}
                  ${isActive ? 'border-blue-500 text-blue-500 animate-pulse' : ''}
                  ${isPending ? 'border-slate-300 text-slate-300' : ''}
                `}>
                  {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : isActive ? <PlayCircle className="w-5 h-5" /> : <Clock className="w-4 h-4" />}
                </div>
                <span className={`text-xs font-medium capitalize ${isPending ? 'text-slate-400' : 'text-slate-700'}`}>
                  {stage.replace('_', ' ')}
                </span>
              </div>
            );
          })}
        </div>
        
        {/* Horizontal connecting line for desktop */}
        <div className="hidden md:block absolute top-4 left-0 right-0 h-0.5 bg-slate-200 -z-0">
          <div 
            className="h-full bg-green-500 transition-all duration-500 ease-in-out" 
            style={{ width: `${(currentStatusIndex / (PIPELINE_STAGES.length - 1)) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
