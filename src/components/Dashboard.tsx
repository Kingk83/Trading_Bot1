import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign, ServerCrash } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ReactNode;
}

function MetricCard({ title, value, change, trend, icon }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-slate-600">{title}</span>
        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600">
          {icon}
        </div>
      </div>
      <div className="space-y-1">
        <p className="text-3xl font-bold text-slate-900">{value}</p>
        <div className="flex items-center space-x-1">
          {trend === 'up' ? (
            <TrendingUp className="w-4 h-4 text-green-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
          <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
            {change}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    totalPnL: 0,
    dailyPnL: 0,
    winRate: 0,
    totalTrades: 0,
    openPositions: 0,
    sharpeRatio: 0
  });

  const [positions, setPositions] = useState<any[]>([]);
  const [recentTrades, setRecentTrades] = useState<any[]>([]);
  const [hasData, setHasData] = useState<boolean | null>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    const { data: trades } = await supabase
      .from('trades')
      .select('*')
      .order('entry_time', { ascending: false })
      .limit(10);

    const { data: positionsData } = await supabase
      .from('positions')
      .select('*');

    const { data: performanceData } = await supabase
      .from('performance_metrics')
      .select('*')
      .order('date', { ascending: false })
      .limit(1)
      .maybeSingle();

    const tradeCount = trades?.length ?? 0;
    const positionCount = positionsData?.length ?? 0;
    setHasData(tradeCount > 0 || positionCount > 0);

    if (trades) {
      const totalPnL = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
      const closedTrades = trades.filter(t => t.status === 'closed');
      const winningTrades = closedTrades.filter(t => t.pnl > 0);

      setMetrics({
        totalPnL,
        dailyPnL: performanceData?.total_pnl || 0,
        winRate: closedTrades.length > 0 ? (winningTrades.length / closedTrades.length) * 100 : 0,
        totalTrades: closedTrades.length,
        openPositions: positionsData?.length || 0,
        sharpeRatio: performanceData?.sharpe_ratio || 0
      });

      setRecentTrades(trades.slice(0, 5));
    }

    if (positionsData) {
      setPositions(positionsData);
    }
  };

  return (
    <div className="space-y-6">
      {hasData === false && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-5 flex items-start gap-4">
          <ServerCrash className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
          <div>
            <p className="font-semibold text-amber-800">Waiting for the trading bot</p>
            <p className="text-sm text-amber-700 mt-1">
              No trade data has been received yet. Make sure the bot is deployed on Railway with the
              correct environment variables: <code className="font-mono bg-amber-100 px-1 rounded">VITE_SUPABASE_URL</code> and{' '}
              <code className="font-mono bg-amber-100 px-1 rounded">VITE_SUPABASE_ANON_KEY</code>.
              The dashboard will update automatically once the bot starts trading.
            </p>
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total P&L"
          value={`$${metrics.totalPnL.toFixed(2)}`}
          change={`${metrics.totalPnL >= 0 ? '+' : ''}${metrics.totalPnL.toFixed(2)}`}
          trend={metrics.totalPnL >= 0 ? 'up' : 'down'}
          icon={<DollarSign className="w-5 h-5" />}
        />

        <MetricCard
          title="Win Rate"
          value={`${metrics.winRate.toFixed(1)}%`}
          change={`${metrics.totalTrades} trades`}
          trend={metrics.winRate >= 50 ? 'up' : 'down'}
          icon={<Activity className="w-5 h-5" />}
        />

        <MetricCard
          title="Open Positions"
          value={metrics.openPositions.toString()}
          change="Active"
          trend="up"
          icon={<TrendingUp className="w-5 h-5" />}
        />

        <MetricCard
          title="Sharpe Ratio"
          value={metrics.sharpeRatio.toFixed(2)}
          change="Risk-adjusted"
          trend={metrics.sharpeRatio >= 1 ? 'up' : 'down'}
          icon={<Activity className="w-5 h-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Open Positions</h3>
          {positions.length === 0 ? (
            <p className="text-slate-500 text-sm">No open positions</p>
          ) : (
            <div className="space-y-3">
              {positions.map((position) => (
                <div key={position.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div>
                    <p className="font-medium text-slate-900">{position.symbol}</p>
                    <p className="text-sm text-slate-500">
                      {position.side.toUpperCase()} | Entry: ${position.entry_price}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${position.unrealized_pnl?.toFixed(2) || '0.00'}
                    </p>
                    <p className="text-sm text-slate-500">Qty: {position.quantity}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Trades</h3>
          {recentTrades.length === 0 ? (
            <p className="text-slate-500 text-sm">No recent trades</p>
          ) : (
            <div className="space-y-3">
              {recentTrades.map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div>
                    <p className="font-medium text-slate-900">{trade.symbol}</p>
                    <p className="text-sm text-slate-500">{trade.side.toUpperCase()} | {trade.status}</p>
                  </div>
                  <div className="text-right">
                    {trade.pnl !== null && (
                      <p className={`font-semibold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${trade.pnl.toFixed(2)}
                      </p>
                    )}
                    <p className="text-xs text-slate-500">
                      {new Date(trade.entry_time).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
