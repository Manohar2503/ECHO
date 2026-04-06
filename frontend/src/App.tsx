import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import Login from './pages/Login';
import Inventory from './pages/Inventory';
import Billing from './pages/Billing';
import Reporting from './pages/Reporting';
import AI from './pages/AI';

const tokenKey = 'echo_token';

function App() {
    const navigate = useNavigate();
    const token = localStorage.getItem(tokenKey);

    return (
        <div className="app-shell">
            <header className="topbar">
                <div className="brand">ECHO Retail Dashboard</div>
                {token ? (
                    <div className="nav-actions">
                        <Link to="/inventory">Inventory</Link>
                        <Link to="/billing">Billing</Link>
                        <Link to="/reporting">Reporting</Link>
                        <Link to="/ai">AI</Link>
                        <button
                            className="secondary"
                            onClick={() => {
                                localStorage.removeItem(tokenKey);
                                navigate('/login');
                            }}
                        >
                            Logout
                        </button>
                    </div>
                ) : null}
            </header>
            <main className="content">
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/inventory" element={token ? <Inventory /> : <Navigate to="/login" />} />
                    <Route path="/billing" element={token ? <Billing /> : <Navigate to="/login" />} />
                    <Route path="/reporting" element={token ? <Reporting /> : <Navigate to="/login" />} />
                    <Route path="/ai" element={token ? <AI /> : <Navigate to="/login" />} />
                    <Route path="/*" element={<Navigate to={token ? '/inventory' : '/login'} />} />
                </Routes>
            </main>
        </div>
    );
}

export default App;
