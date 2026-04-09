import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

export default function PositionsTable() {
  const [positions, setPositions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPositions();
    const interval = setInterval(fetchPositions, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchPositions = async () => {
    setLoading(true);
    const { data } = await supabase
      .from('positions')
      .select('*')
      .order('opened_at', { ascending: false });

    if (data) {
      setPositions(data);
    }
    setLoading(false);
  };

  if (loading && positions.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
        <p className="text-slate-500">Loading positions...</p>
      </div>
    );
  }

  if (positions.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
        <p className="text-slate-500">No open positions</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900">Open Positions</h2>
        <p className="text-sm text-slate-500 mt-1">{positions.length} active position(s)</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Side
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Entry Price
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Current Price
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Unrealized P&L
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Stop Loss
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                Take Profit
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {positions.map((position) => (
              <tr key={position.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-medium text-slate-900">{position.symbol}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    position.side === 'long'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {position.side.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                  ${position.entry_price}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                  ${position.current_price}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                  {position.quantity}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`font-semibold ${
                    position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${position.unrealized_pnl?.toFixed(2) || '0.00'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                  ${position.stop_loss}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                  ${position.take_profit}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
