import axios from 'axios';

const authApi = axios.create({
    baseURL: 'http://localhost:8001/auth',
    headers: { 'Content-Type': 'application/json' }
});

const inventoryApi = axios.create({
    baseURL: 'http://localhost:8002/inventory',
    headers: { 'Content-Type': 'application/json' }
});

const billingApi = axios.create({
    baseURL: 'http://localhost:8003/billing',
    headers: { 'Content-Type': 'application/json' }
});

const aiApi = axios.create({
    baseURL: 'http://localhost:8006/ai',
    headers: { 'Content-Type': 'application/json' }
});

export const setToken = (token: string) => {
    const authHeader = { Authorization: `Bearer ${token}` };
    inventoryApi.defaults.headers.common = authHeader;
    billingApi.defaults.headers.common = authHeader;
    aiApi.defaults.headers.common = authHeader;
};

export { authApi, inventoryApi, billingApi, aiApi };
