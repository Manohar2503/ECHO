import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, setToken } from '../api';

const tokenKey = 'echo_token';

export default function Login() {
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin123');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();
        setError('');

        try {
            const response = await authApi.post('/login', { username, password });
            const token = response.data.access_token;
            localStorage.setItem(tokenKey, token);
            setToken(token);
            navigate('/inventory');
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Login failed');
        }
    };

    return (
        <div className="auth-card">
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    Username
                    <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="admin" />
                </label>
                <label>
                    Password
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="admin123" />
                </label>
                <button type="submit">Sign in</button>
                {error ? <div className="error">{error}</div> : null}
            </form>
        </div>
    );
}
