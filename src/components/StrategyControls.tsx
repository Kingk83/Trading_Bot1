import { useEffect, useState } from 'react';
import { Play, Pause, Settings } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function StrategyControls() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [systemConfig, setSystemConfig] = useState<any>({});

  useEffect(() => {
    fetchStrategies();
    fetchSystemConfig();
  }, []);

  const fetchStrategies = async () => {
    const { data } = await supabase
      .from('strategies')
      .select('*')
      .order('name');

    if (data) {
      setStrategies(data);
    }
  };

  const fetchSystemConfig = async () => {
    const { data } = await supabase
      .from('system_config')
      .select('*');

    if (data) {
      const config: any = {};
      data.forEach(item => {
        config[item.key] = item.value;
      });
      setSystemConfig(config);
    }
  };

  const toggleStrategy = async (strategyId: string, currentEnabled: boolean) => {
    await supabase
      .from('strategies')
      .update({ enabled: !currentEnabled })
      .eq('id', strategyId);

    fetchStrategies();
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">System Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-600 mb-1">Trading Status</p>
            <p className="text-lg font-semibold text-slate-900">
              {systemConfig.trading_enabled ? 'Active' : 'Paused'}
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-600 mb-1">Mode</p>
            <p className="text-lg font-semibold text-slate-900">
              {systemConfig.paper_trading ? 'Paper Trading' : 'Live Trading'}
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-600 mb-1">Max Risk Per Trade</p>
            <p className="text-lg font-semibold text-slate-900">
              {(parseFloat(systemConfig.max_risk_per_trade || 0) * 100).toFixed(1)}%
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-600 mb-1">Max Open Positions</p>
            <p className="text-lg font-semibold text-slate-900">
              {systemConfig.max_open_positions || 0}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Active Strategies</h2>

        {strategies.length === 0 ? (
          <p className="text-slate-500 text-sm">No strategies configured</p>
        ) : (
          <div className="space-y-4">
            {strategies.map((strategy) => (
              <div
                key={strategy.id}
                className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:border-slate-300 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${strategy.enabled ? 'bg-green-500' : 'bg-slate-300'}`} />
                  <div>
                    <h3 className="font-semibold text-slate-900">{strategy.name}</h3>
                    <p className="text-sm text-slate-500 capitalize">{strategy.type.replace('_', ' ')}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => toggleStrategy(strategy.id, strategy.enabled)}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center space-x-2 ${
                      strategy.enabled
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {strategy.enabled ? (
                      <>
                        <Pause className="w-4 h-4" />
                        <span>Pause</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        <span>Activate</span>
                      </>
                    )}
                  </button>

                  <button className="p-2 text-slate-400 hover:text-slate-600 transition-colors">
                    <Settings className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
