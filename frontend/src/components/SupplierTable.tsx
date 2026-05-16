import { Link } from 'react-router-dom';
import type { ProcurementResultsResponse } from '../api/client';

interface Props {
  results: ProcurementResultsResponse | null;
}

const Tooltip = ({ children, content }: { children: React.ReactNode, content: string | undefined }) => {
  if (!content) return <>{children}</>;
  return (
    <div className="group relative inline-flex items-center cursor-help">
      {children}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 p-2 bg-slate-900 text-slate-100 text-xs rounded shadow-lg z-50 whitespace-normal">
        {content}
        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900"></div>
      </div>
    </div>
  );
};

export default function SupplierTable({ results }: Props) {
  if (!results || !results.ranked_suppliers || results.ranked_suppliers.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <h2 className="text-lg font-semibold text-slate-800">Supplier Comparison</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-50 text-slate-700 uppercase font-medium border-b border-slate-200">
            <tr>
              <th className="px-4 py-3">Rank</th>
              <th className="px-4 py-3">Supplier</th>
              <th className="px-4 py-3 text-center">Price Score</th>
              <th className="px-4 py-3 text-center">Speed Score</th>
              <th className="px-4 py-3 text-center">Quality Score</th>
              <th className="px-4 py-3 text-center">Trust Score</th>
              <th className="px-4 py-3">Final Score</th>
            </tr>
          </thead>
          <tbody>
            {results.ranked_suppliers.map((supplier) => {
              const sa = supplier.score_analysis || {};
              const s = supplier.scores || {};
              
              return (
                <tr key={supplier.supplier_id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold
                      ${supplier.rank === 1 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                      {supplier.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/supplier/${supplier.supplier_id}`}
                      className="font-semibold text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                    >
                      {supplier.supplier_name}
                    </Link>
                    <div className="text-xs text-slate-400 font-normal mt-0.5">{supplier.location}</div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Tooltip content={sa.price_logic}>
                      <span className="border-b border-dotted border-slate-400">{((s.price_competitiveness || 0) * 100).toFixed(0)}%</span>
                    </Tooltip>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Tooltip content={sa.speed_logic}>
                      <span className="border-b border-dotted border-slate-400">{((s.response_speed || 0) * 100).toFixed(0)}%</span>
                    </Tooltip>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Tooltip content={sa.quality_logic}>
                      <span className="border-b border-dotted border-slate-400">{((s.quote_completeness || 0) * 100).toFixed(0)}%</span>
                    </Tooltip>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Tooltip content={sa.trust_logic}>
                      <span className="border-b border-dotted border-slate-400">{((s.referral || 0) * 100).toFixed(0)}%</span>
                    </Tooltip>
                  </td>
                  <td className="px-4 py-3">
                    <Tooltip content={sa.final_logic}>
                      <div className="flex items-center gap-2 border-b border-dotted border-slate-400 pb-0.5 inline-flex">
                        <div className="w-16 bg-slate-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${(s.composite || 0) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs font-semibold">{((s.composite || 0) * 100).toFixed(0)}%</span>
                      </div>
                    </Tooltip>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      {results.extracted_quotations.length > 0 && (
        <div className="mt-6 border-t border-slate-200">
          <div className="p-4 border-b border-slate-200 bg-slate-50">
            <h3 className="text-md font-semibold text-slate-800">Detailed Quotes</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-slate-700 uppercase font-medium border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Supplier</th>
                  <th className="px-4 py-3">Price</th>
                  <th className="px-4 py-3">MOQ</th>
                  <th className="px-4 py-3">Delivery (Days)</th>
                  <th className="px-4 py-3">Payment Terms</th>
                  <th className="px-4 py-3">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {results.extracted_quotations.map((quote) => (
                  <tr key={quote.quotation_id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-800">{quote.supplier_name}</td>
                    <td className="px-4 py-3">{quote.currency === 'INR' ? 'AED' : quote.currency} {quote.unit_price}</td>
                    <td className="px-4 py-3">{quote.moq || '-'}</td>
                    <td className="px-4 py-3">{quote.delivery_days || '-'}</td>
                    <td className="px-4 py-3 truncate max-w-xs">{quote.payment_terms || '-'}</td>
                    <td className="px-4 py-3">
                      {quote.extraction_confidence ? `${(Number(quote.extraction_confidence) * 100).toFixed(0)}%` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
