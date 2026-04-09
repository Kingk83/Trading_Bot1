import { useEffect, useState } from 'react';
import { LayoutDashboard, Briefcase, TrendingUp, BarChart2, Settings, Activity } from 'lucide-react';
import { supabase } from './lib/supabase';
import Dashboard from './components/Dashboard';
import PerformanceChart from './components/PerformanceChart';
import PositionsTable from './components/PositionsTable';
import TradesTable from './components/TradesTable';
import StrategyControls from './components/StrategyControls';

const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
  { id: 'positions', name: 'Positions', icon: Briefcase },
  { id: 'trades', name: 'Trades', icon: TrendingUp },
  { id: 'performance', name: 'Performance', icon: BarChart2 },
  { id: 'strategies', name: 'Strategies', icon: Settings },
];

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    const channel = supabase
      .channel('trading_updates')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'trades' }, () => {})
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">AlgoTrader Pro</h1>
                <p className="text-xs text-slate-500">Institutional-Grade Trading System</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-slate-600">Paper Trading</span>
            </div>
          </div>

          <nav className="flex space-x-1 -mb-px overflow-x-auto">
            {tabs.map(({ id, name, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`
                  flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
                  ${activeTab === id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span>{name}</span>
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'positions' && <PositionsTable />}
        {activeTab === 'trades' && <TradesTable />}
        {activeTab === 'performance' && <PerformanceChart />}
        {activeTab === 'strategies' && <StrategyControls />}
      </main>

      <footer className="bg-white border-t border-slate-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-2 text-sm text-slate-500">
            <p>AlgoTrader Pro - Professional Trading System</p>
            <p>Always trade responsibly. Past performance does not guarantee future results.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
