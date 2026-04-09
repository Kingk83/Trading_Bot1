import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function RiskMetrics() {
  const [riskEvents, setRiskEvents] = useState<any[]>([]);

  useEffect(() => {
    fetchRiskEvents();
    const interval = setInterval(fetchRiskEvents, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchRiskEvents = async () => {
    const { data } = await supabase
      .from('risk_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10);

    if (data) {
      setRiskEvents(data);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Risk Events</h2>

      {riskEvents.length === 0 ? (
        <div className="flex items-center space-x-2 text-green-600 p-4 bg-green-50 rounded-lg">
          <CheckCircle className="w-5 h-5" />
          <p>No risk events detected</p>
        </div>
      ) : (
        <div className="space-y-3">
          {riskEvents.map((event) => (
            <div
              key={event.id}
              className={`p-4 rounded-lg border ${getSeverityClass(event.severity)}`}
            >
              <div className="flex items-start space-x-3">
                {getSeverityIcon(event.severity)}
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-slate-900">{event.event_type}</p>
                      <p className="text-sm text-slate-600 mt-1">{event.message}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      event.resolved
                        ? 'bg-green-100 text-green-800'
                        : 'bg-slate-100 text-slate-800'
                    }`}>
                      {event.resolved ? 'Resolved' : 'Active'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    {new Date(event.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
