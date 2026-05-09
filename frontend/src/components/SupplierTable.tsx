import type { ProcurementResultsResponse } from '../api/client';

interface Props {
  results: ProcurementResultsResponse | null;
}

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
              <th className="px-4 py-3">Location</th>
              <th className="px-4 py-3">Unit Price</th>
              <th className="px-4 py-3">Score</th>
            </tr>
          </thead>
          <tbody>
            {results.ranked_suppliers.map((supplier) => {
              return (
                <tr key={supplier.supplier_id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold
                      ${supplier.rank === 1 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                      {supplier.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-800">{supplier.supplier_name}</td>
                  <td className="px-4 py-3">{supplier.location}</td>
                  <td className="px-4 py-3">
                    {supplier.unit_price ? `${supplier.currency || '$'} ${supplier.unit_price}` : 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${(supplier.scores.composite_score || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs">{((supplier.scores.composite_score || 0) * 100).toFixed(0)}%</span>
                    </div>
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
                    <td className="px-4 py-3">{quote.currency} {quote.unit_price}</td>
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
