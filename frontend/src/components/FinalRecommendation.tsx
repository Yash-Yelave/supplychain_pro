import type { ProcurementResultsResponse } from '../api/client';
import { Award, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Props {
  results: ProcurementResultsResponse | null;
}

export default function FinalRecommendation({ results }: Props) {
  if (!results || (!results.final_recommendation_report && !results.analyst_summary)) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 mt-6">
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-5 h-5 text-amber-500" />
        <h2 className="text-xl font-semibold text-slate-800">Final Recommendation</h2>
      </div>

      {results.analyst_summary && (
        <div className="mb-6 bg-slate-50 p-4 rounded-md border border-slate-100">
          <h3 className="text-sm font-semibold text-slate-700 mb-2 uppercase tracking-wide flex items-center gap-2">
            <FileText className="w-4 h-4" /> Analyst Summary
          </h3>
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
            <ReactMarkdown>{results.analyst_summary}</ReactMarkdown>
          </div>
        </div>
      )}

      {results.final_recommendation_report && (
        <div className="bg-slate-50 p-4 rounded-md border border-slate-100">
          <h3 className="text-sm font-semibold text-slate-700 mb-2 uppercase tracking-wide flex items-center gap-2">
            <FileText className="w-4 h-4" /> Detailed Report
          </h3>
          <div className="text-sm text-slate-700 leading-relaxed prose prose-sm max-w-none">
            <ReactMarkdown>{results.final_recommendation_report}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
