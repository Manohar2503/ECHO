import { FormEvent, useEffect, useState } from 'react';
import { billingApi, setToken } from '../api';

type BillingItem = {
    id: number;
    store_id: number;
    user_id: number;
    total_amount: number;
    status: string;
    external_id: string;
    created_at: string;
};

const tokenKey = 'echo_token';

export default function Billing() {
    const [storeId, setStoreId] = useState(1);
    const [userId, setUserId] = useState(3);
    const [productId, setProductId] = useState(1);
    const [quantity, setQuantity] = useState(1);
    const [price, setPrice] = useState(10.5);
    const [externalId, setExternalId] = useState('txn_001');
    const [transactions, setTransactions] = useState<BillingItem[]>([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const token = localStorage.getItem(tokenKey);
        if (token) setToken(token);
        fetchTransactions();
    }, []);

    const fetchTransactions = async () => {
        try {
            const response = await billingApi.get(`/${storeId}`);
            setTransactions(response.data);
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || 'Unable to load transactions');
        }
    };

    const createTransaction = async (event: FormEvent) => {
        event.preventDefault();
        setMessage('');

        try {
            await billingApi.post('/', {
                store_id: storeId,
                user_id: userId,
                items: [{ product_id: productId, quantity, price }],
                external_id: externalId
            });
            setMessage('Transaction created successfully');
            fetchTransactions();
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || 'Billing failed');
        }
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <h2>Billing</h2>
                <p>Create transactions and monitor recent sales.</p>
            </div>
            <div className="grid-card">
                <div className="box">
                    <h3>Create Sale</h3>
                    <form onSubmit={createTransaction} className="form-grid">
                        <label>
                            Store ID
                            <input type="number" value={storeId} onChange={(e) => setStoreId(Number(e.target.value))} min={1} />
                        </label>
                        <label>
                            User ID
                            <input type="number" value={userId} onChange={(e) => setUserId(Number(e.target.value))} min={1} />
                        </label>
                        <label>
                            Product ID
                            <input type="number" value={productId} onChange={(e) => setProductId(Number(e.target.value))} min={1} />
                        </label>
                        <label>
                            Quantity
                            <input type="number" value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} min={1} />
                        </label>
                        <label>
                            Price
                            <input type="number" value={price} onChange={(e) => setPrice(Number(e.target.value))} step="0.01" min={0} />
                        </label>
                        <label>
                            External ID
                            <input value={externalId} onChange={(e) => setExternalId(e.target.value)} />
                        </label>
                        <button type="submit">Create</button>
                    </form>
                    {message ? <div className="message">{message}</div> : null}
                </div>
                <div className="box full-width">
                    <h3>Recent Transactions</h3>
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                    <th>External ID</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.id}</td>
                                        <td>{item.total_amount}</td>
                                        <td>{item.status}</td>
                                        <td>{item.external_id}</td>
                                        <td>{new Date(item.created_at).toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
