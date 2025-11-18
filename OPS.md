# SAFDO Crypto Shield - Operations Guide

© 2025 Deepak Raghunath Raut — MIT Licensed

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Running Locally](#running-locally)
4. [Testing Guide](#testing-guide)
5. [Notification Configuration](#notification-configuration)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 5.0+
- Yarn package manager
- Polkadot.js browser extension

### Installation

```bash
# Clone repository
cd /app

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration

# Frontend setup
cd ../frontend
yarn install
cp .env.example .env
# Edit .env with your backend URL
```

---

## Environment Setup

### Backend Environment Variables

Create `/app/backend/.env` from the example:

```bash
cp /app/backend/.env.example /app/backend/.env
```

**Required Variables:**

- `MONGO_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `DB_NAME`: Database name (default: `safdo_crypto_shield`)
- `CORS_ORIGINS`: Allowed CORS origins (use `*` for development, specific domains for production)

**Optional Variables (for production notifications):**

- `NOTIFICATION_DRY_RUN`: Set to `false` to enable actual notification sending
- `DISCORD_WEBHOOK_URL`: Discord webhook for notifications
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Email notification settings
- `GENERIC_WEBHOOK_URL`: Custom webhook endpoint
- `WEB3_STORAGE_TOKEN`: IPFS upload token from https://web3.storage/
- `SENTRY_DSN`: Error tracking (optional)

### Frontend Environment Variables

Create `/app/frontend/.env`:

```bash
cp /app/frontend/.env.example /app/frontend/.env
```

**Required:**

- `REACT_APP_BACKEND_URL`: Backend API URL
  - Local: `http://localhost:8001`
  - Production: Your deployed backend URL

---

## Running Locally

### Start MongoDB

```bash
# If using system MongoDB
sudo systemctl start mongod

# Or with Docker
docker run -d -p 27017:27017 --name safdo-mongo mongo:5
```

### Start Backend (Development)

```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend will be available at: `http://localhost:8001`

API docs: `http://localhost:8001/docs`

### Start Frontend (Development)

```bash
cd /app/frontend
yarn start
```

Frontend will be available at: `http://localhost:3000`

### Using Supervisor (Production-like)

If supervisor is configured:

```bash
# Start all services
sudo supervisorctl start all

# Check status
sudo supervisorctl status

# Restart specific service
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# View logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

---

## Testing Guide

### Backend Unit Tests

```bash
cd /app/backend
pytest tests/ -v
```

### Backend API Testing (Manual)

#### 1. Health Check

```bash
curl http://localhost:8001/api/health
```

#### 2. Risk Scoring

```bash
curl -X POST http://localhost:8001/api/risk-score \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    "to_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
    "amount": "5000000000000",
    "chain": "polkadot",
    "method": "transfer"
  }'
```

#### 3. Chain Balance

```bash
curl -X POST http://localhost:8001/api/chain-balance \
  -H "Content-Type: application/json" \
  -d '{
    "address": "15oF4uVJwmo4TdGW7VfQxNLavjCXviqxT9S1MgbjMNHr6Sp5",
    "chains": ["polkadot", "kusama", "westend"]
  }'
```

#### 4. Notification Test (DRY-RUN)

```bash
curl -X POST http://localhost:8001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "security_alert",
    "channels": ["discord", "email"],
    "payload": {"message": "Test alert"},
    "user_id": "test_user"
  }'
```

Check backend logs to see dry-run output:

```bash
tail -f /var/log/supervisor/backend.*.log | grep "DRY-RUN"
```

### Frontend Testing

1. Install Polkadot.js extension: https://polkadot.js.org/extension/
2. Create test account in extension
3. Open app and connect wallet
4. Test each feature:
   - Dashboard: View balances across chains
   - Transactions: Analyze a test transaction
   - Notifications: Configure and test notifications

### Test Wallet Setup

**Westend Testnet (Recommended for testing):**

1. Create account in Polkadot.js extension
2. Get free WND tokens: https://faucet.polkadot.io/westend
3. Use this account to test all features

---

## Notification Configuration

### Current Mode: DRY-RUN

By default, notifications are in **dry-run mode**. They are logged but not actually sent.

To see what would be sent:

```bash
tail -f /var/log/supervisor/backend.*.log | grep "\[DRY-RUN\]"
```

### Enabling Real Notifications

#### 1. Discord Notifications

**Setup:**

1. Go to Discord Server Settings > Integrations > Webhooks
2. Create new webhook, copy URL
3. Add to `.env`:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
NOTIFICATION_DRY_RUN=false
```

4. Restart backend:

```bash
sudo supervisorctl restart backend
```

**Test:**

```bash
curl -X POST http://localhost:8001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "security_alert",
    "channels": ["discord"],
    "payload": {"message": "Real Discord test"},
    "user_id": "test_user"
  }'
```

You should receive a message in Discord!

#### 2. Email Notifications (SMTP)

**Setup:**

```bash
# Example with Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_DRY_RUN=false
```

**Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

#### 3. Generic Webhook

```bash
GENERIC_WEBHOOK_URL=https://your-service.com/webhook
NOTIFICATION_DRY_RUN=false
```

Payload format sent:

```json
{
  "event_type": "transfer",
  "user_id": "5Grw...",
  "payload": { /* event data */ },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Production Deployment

### Security Checklist

- [ ] Change `CORS_ORIGINS` from `*` to specific domain
- [ ] Use strong MongoDB credentials
- [ ] Enable HTTPS/TLS
- [ ] Set `NOTIFICATION_DRY_RUN=false` only after testing
- [ ] Configure Sentry for error tracking
- [ ] Set up log rotation
- [ ] Enable rate limiting (already configured)
- [ ] Review and update blacklist addresses in `risk_config.json`

### Environment Variables (Production)

**Never commit these to Git!** Use your deployment platform's secrets management.

**Backend:**

```bash
MONGO_URL=mongodb://user:password@production-host:27017/safdo
DB_NAME=safdo_crypto_shield
CORS_ORIGINS=https://your-domain.com
NOTIFICATION_DRY_RUN=false
DISCORD_WEBHOOK_URL=<your-webhook>
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=<your-smtp-user>
SMTP_PASSWORD=<your-smtp-password>
WEB3_STORAGE_TOKEN=<your-token>
SENTRY_DSN=<your-sentry-dsn>
```

**Frontend:**

```bash
REACT_APP_BACKEND_URL=https://api.your-domain.com
```

### Build Commands

**Frontend (Production Build):**

```bash
cd /app/frontend
yarn build
# Output in /app/frontend/build/
```

**Backend (Production Run):**

```bash
cd /app/backend
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Deployment Platforms

**Suggested Infrastructure (NOT auto-provisioned):**

1. **Backend**: Deploy to Cloud Run, ECS, or VM with gunicorn
2. **Frontend**: Deploy to Vercel, Netlify, or Cloudflare Pages
3. **Database**: MongoDB Atlas or self-hosted replica set
4. **CDN**: Cloudflare for frontend assets

**Example Dockerfile (Backend):**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["gunicorn", "server:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]
```

---

## Troubleshooting

### Backend won't start

**Check logs:**

```bash
tail -f /var/log/supervisor/backend.*.log
```

**Common issues:**

1. MongoDB not running:

```bash
sudo systemctl status mongod
sudo systemctl start mongod
```

2. Port 8001 already in use:

```bash
lsof -i :8001
# Kill process or change port
```

3. Missing dependencies:

```bash
cd /app/backend
pip install -r requirements.txt
```

### Frontend won't connect to backend

1. Check `REACT_APP_BACKEND_URL` in `/app/frontend/.env`
2. Verify backend is running: `curl http://localhost:8001/api/health`
3. Check CORS settings in backend `.env`

### Polkadot.js extension not detected

1. Install: https://polkadot.js.org/extension/
2. Refresh page after installation
3. Check browser console for errors
4. Grant extension permissions when prompted

### RPC endpoints failing

**Polkadot RPC endpoints can be rate-limited or down.**

To add/change endpoints, edit `/app/backend/polkadot_rpc.py`:

```python
self.endpoints = {
    "polkadot": [
        "https://rpc.polkadot.io",
        "https://your-custom-rpc.com",  # Add custom RPC
    ],
    # ...
}
```

### Notifications not sending (even with DRY_RUN=false)

1. Check credentials are correct
2. Test webhook URL manually:

```bash
curl -X POST https://discord.com/api/webhooks/YOUR_WEBHOOK \
  -H "Content-Type: application/json" \
  -d '{"content": "Test"}'
```

3. Check backend logs for error details

---

## Support

For issues, questions, or contributions:

- GitHub: https://github.com/rauttech/safdo-crypto-shield
- Email: [Contact details]

---

© 2025 Deepak Raghunath Raut — SAFDO Crypto Shield — MIT Licensed
