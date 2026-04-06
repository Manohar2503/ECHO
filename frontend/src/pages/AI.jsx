import { useEffect, useState } from 'react';
import { aiApi, setToken } from '../api';

const tokenKey = 'echo_token';

export default function AI() {
    const [storeId, setStoreId] = useState(1);
    const [productId, setProductId] = useState(1);
    const [forecast, setForecast] = useState([]);
    const [anomalies, setAnomalies] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [query, setQuery] = useState('forecast product 1');
    const [conversation, setConversation] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        const token = localStorage.getItem(tokenKey);
        if (token) setToken(token);
    }, []);

    const fetchForecast = async () => {
        setMessage('');
        try {
            const response = await aiApi.get(`/forecast/${storeId}/${productId}`);
            setForecast(response.data.forecast);
        } catch (err) {
            setMessage(err?.response?.data?.detail || 'Forecast failed');
        }
    };

    const fetchAnomalies = async () => {
        setMessage('');
        try {
            const response = await aiApi.get(`/anomalies/${storeId}`);
            setAnomalies(response.data.anomalies);
        } catch (err) {
            setMessage(err?.response?.data?.detail || 'Anomaly detection failed');
        }
    };

    const fetchRecommendations = async () => {
        setMessage('');
        try {
            const response = await aiApi.get(`/recommendations/${storeId}`);
            setRecommendations(response.data.recommendations);
        } catch (err) {
            setMessage(err?.response?.data?.detail || 'Recommendations failed');
        }
    };

    const runConversation = async () => {
        setMessage('');
        try {
            const response = await aiApi.post('/query', { query });
            setConversation(JSON.stringify(response.data, null, 2));
        } catch (err) {
            setMessage(err?.response?.data?.detail || 'Conversation failed');
        }
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <h2>AI Studio</h2>
                <p>Forecast demand, detect anomalies, and get restock recommendations.</p>
            </div>
            <div className="grid-card">
                <div className="box">
                    <h3>Demand Forecast</h3>
                    <label>
                        Store ID
                        <input type="number" value={storeId} onChange={(e) => setStoreId(Number(e.target.value))} min={1} />
                    </label>
                    <label>
                        Product ID
                        <input type="number" value={productId} onChange={(e) => setProductId(Number(e.target.value))} min={1} />
                    </label>
                    <button onClick={fetchForecast}>Get Forecast</button>
                    {forecast.length > 0 && (
                        <div className="chart-box">
                            <strong>Forecast</strong>
                            <p>{forecast.join(', ')}</p>
                        </div>
                    )}
                </div>
                <div className="box">
                    <h3>Anomaly Detection</h3>
                    <button onClick={fetchAnomalies}>Detect</button>
                    {anomalies.length > 0 ? (
                        <ul className="summary-list">
                            {anomalies.map((item, index) => (
                                <li key={index}>{item.date}: {item.amount} ({item.severity})</li>
                            ))}
                        </ul>
                    ) : null}
                </div>
                <div className="box full-width">
                    <h3>Recommendations</h3>
                    <button onClick={fetchRecommendations}>Load Recommendations</button>
                    {recommendations.length > 0 ? (
                        <div className="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Current</th>
                                        <th>Recommended</th>
                                        <th>Confidence</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {recommendations.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item.product_id}</td>
                                            <td>{item.current_quantity}</td>
                                            <td>{item.recommended_quantity}</td>
                                            <td>{item.confidence}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : null}
                </div>
            </div>
            <div className="box full-width">
                <h3>Conversational Query</h3>
                <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={3} />
                <button onClick={runConversation}>Ask AI</button>
                {conversation ? <pre className="code-block">{conversation}</pre> : null}
            </div>
            {message ? <div className="message">{message}</div> : null}
        </div>
    );
}
