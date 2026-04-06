import { FormEvent, useEffect, useState } from 'react';
import { inventoryApi, setToken } from '../api';

const tokenKey = 'echo_token';

type InventoryItem = {
    id: number;
    store_id: number;
    product_id: number;
    quantity: number;
    min_stock_level: number;
    last_updated: string;
    version: number;
};

export default function Inventory() {
    const [items, setItems] = useState<InventoryItem[]>([]);
    const [storeId, setStoreId] = useState(1);
    const [productId, setProductId] = useState(1);
    const [quantity, setQuantity] = useState(100);
    const [minStock, setMinStock] = useState(10);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const token = localStorage.getItem(tokenKey);
        if (token) setToken(token);
        fetchInventory();
    }, []);

    const fetchInventory = async () => {
        try {
            const response = await inventoryApi.get(`/${storeId}`);
            setItems(response.data);
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || 'Unable to load inventory');
        }
    };

    const createInventory = async (event: FormEvent) => {
        event.preventDefault();
        setMessage('');

        try {
            await inventoryApi.post('/', { store_id: storeId, product_id: productId, quantity, min_stock_level: minStock });
            setMessage('Inventory created successfully');
            fetchInventory();
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || 'Failed to create inventory');
        }
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <h2>Inventory</h2>
                <p>View stock and add inventory for store {storeId}.</p>
            </div>
            <div className="grid-card">
                <div className="box">
                    <h3>Add Inventory</h3>
                    <form onSubmit={createInventory} className="form-grid">
                        <label>
                            Store ID
                            <input type="number" value={storeId} onChange={(e) => setStoreId(Number(e.target.value))} min={1} />
                        </label>
                        <label>
                            Product ID
                            <input type="number" value={productId} onChange={(e) => setProductId(Number(e.target.value))} min={1} />
                        </label>
                        <label>
                            Quantity
                            <input type="number" value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} min={0} />
                        </label>
                        <label>
                            Min Stock
                            <input type="number" value={minStock} onChange={(e) => setMinStock(Number(e.target.value))} min={0} />
                        </label>
                        <button type="submit">Create</button>
                    </form>
                    {message ? <div className="message">{message}</div> : null}
                </div>
                <div className="box full-width">
                    <h3>Current Inventory</h3>
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Min Stock</th>
                                    <th>Last Updated</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.id}</td>
                                        <td>{item.product_id}</td>
                                        <td>{item.quantity}</td>
                                        <td>{item.min_stock_level}</td>
                                        <td>{new Date(item.last_updated).toLocaleString()}</td>
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
