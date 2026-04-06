import { useState } from 'react';
import { inventoryApi } from '../api';

export default function Reporting() {
    const [storeId, setStoreId] = useState(1);
    const [message, setMessage] = useState('');

    const fetchReporting = async () => {
        setMessage('');
        try {
            const response = await inventoryApi.get(`/alerts/low-stock/${storeId}`);
            setMessage(`Low-stock products: ${response.data.length}`);
        } catch (err) {
            setMessage(err?.response?.data?.detail || 'Unable to load reporting');
        }
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <h2>Reporting</h2>
                <p>View low-stock alerts and basic store metrics.</p>
            </div>
            <div className="box full-width">
                <h3>Low Stock Alerts</h3>
                <label>
                    Store ID
                    <input type="number" value={storeId} onChange={(e) => setStoreId(Number(e.target.value))} min={1} />
                </label>
                <button onClick={fetchReporting}>Fetch Alerts</button>
                {message ? <div className="message">{message}</div> : null}
            </div>
        </div>
    );
}
