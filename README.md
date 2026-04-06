# Retail Operations Platform

A comprehensive omnichannel convenience retail operations platform with offline synchronization, AI-powered insights, and event-sourced architecture for 86 stores.

## Overview

This platform provides a complete solution for retail operations including inventory management, billing, reporting, and AI-driven forecasting and anomaly detection. Built with a microservices architecture using FastAPI backend and React JS frontend, featuring event sourcing with vector clocks for robust offline sync.

## Features

- **Authentication & Authorization**: JWT-based secure login system
- **Inventory Management**: Real-time stock tracking and updates
- **Billing & Transactions**: Seamless transaction processing
- **Reporting & Analytics**: Comprehensive dashboards with charts
- **AI-Powered Insights**: Conversational AI for sales forecasting and anomaly detection
- **Offline Synchronization**: Event-sourced architecture with vector clocks for conflict resolution
- **Responsive UI**: Modern React JS frontend with mobile-friendly design

## Architecture

### Backend (FastAPI Microservices)
- **Auth Service** (Port 8001): User authentication and JWT token management
- **Inventory Service** (Port 8002): Product and stock management
- **Billing Service** (Port 8003): Transaction processing and payment handling
- **Reporting Service** (Port 8004): Analytics and report generation
- **AI Service** (Port 8005): Machine learning models for forecasting and NLP queries

### Frontend (React JS)
- Login page with JWT authentication
- Inventory dashboard for CRUD operations
- Billing interface for transaction creation
- Reporting page with interactive charts
- AI chat interface for querying insights

### Data Layer
- **Database**: SQLite for development (easily switchable to PostgreSQL)
- **Event Store**: Append-only event logs for offline sync
- **Caching**: Redis for performance optimization
- **AI Models**: NumPy/Pandas for data processing, custom NLP for queries

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), Uvicorn, Pydantic
- **Frontend**: React JS, Vite, Axios, React Router
- **Database**: SQLite (with async support via aiosqlite)
- **AI/ML**: NumPy, Pandas, Scikit-learn
- **Authentication**: Python-JOSE, PassLib
- **Caching**: Redis
- **Other**: Alembic (migrations), Structlog (logging)

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

### Backend Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd retail-ops-platform
   ```

2. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn[standard] sqlalchemy aiosqlite alembic python-jose[cryptography] passlib[bcrypt] redis pydantic httpx structlog prometheus-client numpy pandas scikit-learn
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` (if exists) or create `.env`
   - Configure database URL, JWT secrets, etc.

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start backend services (run each in separate terminals):
   ```bash
   # Auth Service
   uvicorn services.auth.main:app --reload --port 8001

   # Inventory Service
   uvicorn services.inventory.main:app --reload --port 8002

   # Billing Service
   uvicorn services.billing.main:app --reload --port 8003

   # Reporting Service
   uvicorn services.reporting.main:app --reload --port 8004

   # AI Service
   uvicorn services.ai.main:app --reload --port 8005
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open browser at `http://localhost:5173` (or the URL shown in terminal)

## API Documentation

Once services are running, access API docs at:
- Auth: http://localhost:8001/docs
- Inventory: http://localhost:8002/docs
- Billing: http://localhost:8003/docs
- Reporting: http://localhost:8004/docs
- AI: http://localhost:8005/docs

## Usage

1. **Login**: Use the frontend login page or API to authenticate
2. **Inventory**: Add/edit products, track stock levels
3. **Billing**: Create transactions and process payments
4. **Reporting**: View analytics and generate reports
5. **AI**: Ask questions like "forecast sales for next month" or "detect anomalies in inventory"

## Development

- Backend services are in `services/` directory
- Shared code in `shared/` directory
- Frontend code in `frontend/` directory
- Database files in `database/` directory
- Documentation in `docs/` directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

This project is licensed under the MIT License.
- AI: `/ai/forecast`, `/ai/query` (conversational)

## Key Features
- JWT RBAC, async I/O, PostgreSQL optimization.
- Offline sync with event replay.
- AI safety: Confidence scoring, human validation.
- Metrics: Sync rate, latency, uptime.

## Future Scope
IoT shelves, vision billing, advanced ML.

## Trade-offs
Eventual consistency prioritizes availability; vector clocks ensure accuracy.