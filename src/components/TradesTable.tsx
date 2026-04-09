import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

export default function TradesTable() {
  const [trades, setTrades] = useState<any[]>([]);
  const [filter, setFilter] = useState<'all' | 'open' | 'closed'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrades();
  }, [filter]);

  const fetchTrades = async () => {
    setLoading(true);
    let query = supabase
      .from('trades')
      .select('*')
      .order('entry_time', { ascending: false })
      .limit(50);

    if (filter !== 'all') {
      query = query.eq('status', filter);
    }

    const { data } = await query;

    if (data) {
      setTrades(data);
    }
    setLoading(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Trade History</h2>
            <p className="text-sm text-slate-500 mt-1">{trades.length} trade(s)</p>
          </div>

          <div className="flex space-x-2">
            {(['all', 'open', 'closed'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  filter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center">
          <p className="text-slate-500">Loading trades...</p>
        </div>
      ) : trades.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-slate-500">No trades found</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Side</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Entry</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Exit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">P&L</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase">Entry Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {trades.map((trade) => (
                <tr key={trade.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium text-slate-900">{trade.symbol}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      trade.side === 'buy'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {trade.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    ${trade.entry_price}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    {trade.exit_price ? `$${trade.exit_price}` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    {trade.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {trade.pnl !== null ? (
                      <div>
                        <span className={`font-semibold ${
                          trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          ${trade.pnl.toFixed(2)}
                        </span>
                        <span className="text-xs text-slate-500 ml-1">
                          ({trade.pnl_percent?.toFixed(2)}%)
                        </span>
                      </div>
                    ) : (
                      <span className="text-slate-500">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      trade.status === 'open'
                        ? 'bg-blue-100 text-blue-800'
                        : trade.status === 'closed'
                        ? 'bg-slate-100 text-slate-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {trade.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {formatDate(trade.entry_time)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
