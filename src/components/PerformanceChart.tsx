import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

export default function PerformanceChart() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  const fetchPerformanceData = async () => {
    const { data: trades } = await supabase
      .from('trades')
      .select('*')
      .eq('status', 'closed');

    if (trades) {
      const totalPnL = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
      const winningTrades = trades.filter(t => t.pnl > 0);
      const losingTrades = trades.filter(t => t.pnl < 0);

      const avgWin = winningTrades.length > 0
        ? winningTrades.reduce((sum, t) => sum + t.pnl, 0) / winningTrades.length
        : 0;

      const avgLoss = losingTrades.length > 0
        ? losingTrades.reduce((sum, t) => sum + t.pnl, 0) / losingTrades.length
        : 0;

      const profitFactor = Math.abs(avgLoss) > 0 ? avgWin / Math.abs(avgLoss) : 0;

      setSummary({
        totalTrades: trades.length,
        winningTrades: winningTrades.length,
        losingTrades: losingTrades.length,
        winRate: trades.length > 0 ? (winningTrades.length / trades.length) * 100 : 0,
        totalPnL,
        avgWin,
        avgLoss,
        profitFactor,
        largestWin: Math.max(...trades.map(t => t.pnl), 0),
        largestLoss: Math.min(...trades.map(t => t.pnl), 0)
      });
    }
  };

  return (
    <div className="space-y-6">
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <p className="text-sm text-slate-600 mb-2">Total P&L</p>
            <p className={`text-3xl font-bold ${summary.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${summary.totalPnL.toFixed(2)}
            </p>
          </div>

          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <p className="text-sm text-slate-600 mb-2">Win Rate</p>
            <p className="text-3xl font-bold text-slate-900">{summary.winRate.toFixed(1)}%</p>
            <p className="text-sm text-slate-500 mt-1">
              {summary.winningTrades}W / {summary.losingTrades}L
            </p>
          </div>

          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <p className="text-sm text-slate-600 mb-2">Profit Factor</p>
            <p className="text-3xl font-bold text-slate-900">{summary.profitFactor.toFixed(2)}</p>
          </div>

          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <p className="text-sm text-slate-600 mb-2">Total Trades</p>
            <p className="text-3xl font-bold text-slate-900">{summary.totalTrades}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">Performance Metrics</h2>

        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-slate-100">
                <span className="text-slate-600">Average Win</span>
                <span className="font-semibold text-green-600">${summary.avgWin.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-slate-100">
                <span className="text-slate-600">Average Loss</span>
                <span className="font-semibold text-red-600">${summary.avgLoss.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-slate-100">
                <span className="text-slate-600">Largest Win</span>
                <span className="font-semibold text-green-600">${summary.largestWin.toFixed(2)}</span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-slate-100">
                <span className="text-slate-600">Largest Loss</span>
                <span className="font-semibold text-red-600">${summary.largestLoss.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-slate-100">
                <span className="text-slate-600">Win/Loss Ratio</span>
                <span className="font-semibold text-slate-900">
                  {(Math.abs(summary.avgWin / summary.avgLoss)).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-slate-100">
                <span className="text-slate-600">Expectancy</span>
                <span className="font-semibold text-slate-900">
                  ${((summary.winRate/100 * summary.avgWin) + ((100-summary.winRate)/100 * summary.avgLoss)).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
