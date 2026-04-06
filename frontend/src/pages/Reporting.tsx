import { useEffect, useState } from 'react';
import { inventoryApi } from '../api';

const tokenKey = 'echo_token';

type ReportingData = {
    total_sales: number;
    transaction_count?: number;
};

export default function Reporting() {
    const [storeId, setStoreId] = useState(1);
    const [salesMetric, setSalesMetric] = useState<ReportingData | null>(null);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (localStorage.getItem(tokenKey)) {
            fetchReporting();
        }
    }, []);

    const fetchReporting = async () => {
        setMessage('');
        try {
            const response = await inventoryApi.get(`/alerts/low-stock/${storeId}`);
            setMessage(`Low-stock products: ${response.data.length}`);
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || 'Unable to load reporting');
        }
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <h2>Reporting</h2>
                <p>View alerts and store metrics.</p>
            </div>
            <div className="box full-width">
                <h3>Low Stock Alerts</h3>
                <label>
                    Store ID
                    <input type="number" value={storeId} onChange={(e) => setStoreId(Number(e.target.value))} min={1} />
                </label>
                <button onClick={fetchReporting}>Fetch Alerts</button>
                {message ? <div className="message">{message}</div> : null}
                {salesMetric ? (
                    <div className="metric-card">
                        <div>
                            <strong>Total Sales</strong>
                            <p>{salesMetric.total_sales}</p>
                        </div>
                        <div>
                            <strong>Transactions</strong>
                            <p>{salesMetric.transaction_count || 0}</p>
                        </div>
                    </div>
                ) : null}
            </div>
        </div>
    );
}
