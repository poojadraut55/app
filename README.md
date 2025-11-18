# SAFDO Crypto Shield

© 2025 Deepak Raghunath Raut — MIT Licensed

**Securing the Polkadot Ecosystem**

SAFDO (Security Alert Framework for Decentralized Operations) is a comprehensive security platform for Polkadot, Kusama, and Westend networks. It provides real-time risk scoring, multi-chain balance monitoring, and intelligent notification system to protect your crypto assets.

---

## 🚀 Features

### 🔒 Core Security

- **Risk Scoring Engine**: Heuristic-based transaction risk analysis (0-100 score)
- **Blacklist Detection**: Automatic flagging of known malicious addresses
- **Suspicious Method Detection**: Identifies high-risk transaction methods
- **High-Value Alert**: Warns on transfers exceeding thresholds
- **Contract Interaction Analysis**: Detects potentially dangerous smart contract calls

### 🌐 Multi-Chain Support

- **Polkadot** (DOT)
- **Kusama** (KSM)
- **Westend** (WND) - Testnet

Supports balance queries with automatic RPC failover across multiple endpoints.

### 🔔 Notification System

- **Discord** webhooks
- **Email** (SMTP)
- **Generic Webhooks** for custom integrations
- **Mobile Push** (planned)

**Current Mode:** DRY-RUN (logs dispatch without sending - perfect for staging)

### 📊 Dashboard Features

- **Wallet Connection**: Polkadot.js extension integration
- **Multi-Chain Balances**: View free, reserved, and transferable balances
- **Transaction Risk Analyzer**: Test transactions before sending
- **Notification Preferences**: Granular control over alert channels
- **Real-time Updates**: Automatic balance refresh

---

## 🛠️ Tech Stack

### Backend

- **FastAPI** (Python 3.11+)
- **MongoDB** with Motor (async driver)
- **substrate-interface** for Polkadot RPC
- **slowapi** for rate limiting
- **aiohttp** for async HTTP requests

### Frontend

- **React 19** with hooks
- **@polkadot/extension-dapp** for wallet integration
- **@polkadot/api** for chain interaction
- **Tailwind CSS** for styling
- **Axios** for API calls
- **Lucide React** for icons

---

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py                 # Main FastAPI application
│   ├── risk_scorer.py            # Risk scoring logic
│   ├── polkadot_rpc.py           # Polkadot RPC manager with failover
│   ├── notification_relay.py     # Notification dispatcher (dry-run mode)
│   ├── ipfs_proxy.py             # IPFS upload proxy (mock)
│   ├── risk_config.json          # Risk scoring configuration
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   └── .env                      # Your environment config (not in git)
│
├── frontend/
│   ├── src/
│   │   ├── App.js                # Main React component
│   │   ├── components/
│   │   │   ├── Header.js         # Navigation header
│   │   │   ├── WalletConnect.js  # Wallet connection UI
│   │   │   ├── Dashboard.js      # Multi-chain balance dashboard
│   │   │   ├── TransactionFeed.js # Risk analyzer
│   │   │   └── NotificationSettings.js # Notification preferences
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   ├── .env.example
│   └── .env                      # Your frontend config (not in git)
│
├── tests/                        # Unit and integration tests
├── OPS.md                        # Detailed operations guide
└── README.md                     # This file
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and Yarn
- MongoDB 5.0+
- Polkadot.js browser extension

### Installation

```bash
# Backend
cd /app/backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URL

# Frontend
cd /app/frontend
#mac use brew install yarn
yarn install
cp .env.example .env
#mac use brew install node 
# Edit .env with your backend URL
STEP 1 — Fix your Xcode Command Line Tools (required by Node & Brew)

Run:

xcode-select --install


If it says they are already installed but outdated, update them:

Option A — Check for macOS updates:

System Settings → General → Software Update
→ Install Command Line Tools if shown.

Option B — If no update shown, run:
sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select --install


This forces a clean reinstall.

✅ STEP 2 — Make sure Homebrew is healthy

Run:

brew update
brew doctor


If doctor says “Your system is ready to brew.” → Good.

If it shows warnings, paste them here.

✅ STEP 3 — Install Node properly

Once Xcode tools are installed correctly:

brew install node


Test:

node -v
npm -v

```

### Run (Development)

**Terminal 1 - Backend:**

```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**

```bash
cd /app/frontend
yarn start
```

Open http://localhost:3000 in your browser.

### Run (Production-like with Supervisor)

```bash
sudo supervisorctl start all
sudo supervisorctl status
```

See `OPS.md` for detailed instructions.

---

## 📡 API Endpoints

### Risk Scoring

```bash
POST /api/risk-score
```

Analyzes transaction risk. Returns score 0-100 with reasons.

**Example:**

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

### Multi-Chain Balance

```bash
POST /api/chain-balance
```

Fetches balances across multiple chains.

### Notifications

```bash
POST /api/notify                              # Send notification
POST /api/notifications/preferences           # Save preferences
GET  /api/notifications/preferences/{user_id} # Get preferences
```

### Health Check

```bash
GET /api/health
```

Full API documentation: http://localhost:8001/docs

---

## 🛡️ Security Features

### Rate Limiting

- **General endpoints**: 20-100 requests/minute per IP
- **Risk scoring**: 30 requests/minute
- **Notifications**: 10 requests/minute
- **IPFS uploads**: 5 requests/minute

### Input Validation

- Pydantic models for all API inputs
- Address format validation
- Amount range checks
- File type and size validation for uploads

### Non-Custodial

- All wallet signing happens client-side
- Backend never has access to private keys
- Uses Polkadot.js injector for transactions

---

## 🧪 Testing

### Backend Tests

```bash
cd /app/backend
pytest tests/ -v
```

### Manual API Testing

See `OPS.md` for comprehensive curl examples.

### Frontend Testing

1. Install Polkadot.js extension
2. Create test account
3. Get testnet tokens: https://faucet.polkadot.io/westend
4. Connect and test all features

---

## 📦 Notification Setup

### DRY-RUN Mode (Default)

Notifications are logged but not sent. Perfect for staging!

```bash
# View dry-run logs
tail -f /var/log/supervisor/backend.*.log | grep "\[DRY-RUN\]"
```

### Production Mode

**Enable real notifications:**

1. Set `NOTIFICATION_DRY_RUN=false` in backend `.env`
2. Configure channel credentials (Discord webhook, SMTP, etc.)
3. Restart backend

**Discord Example:**

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK
NOTIFICATION_DRY_RUN=false
```

See `OPS.md` for detailed setup instructions for each channel.

---

## 🚀 Deployment

### Build Frontend

```bash
cd /app/frontend
yarn build
# Output in build/
```

### Run Backend (Production)

```bash
cd /app/backend
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Docker (Optional)

Example Dockerfile provided in `OPS.md`.

### Deployment Platforms

- **Backend**: Cloud Run, ECS, VPS with gunicorn
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: MongoDB Atlas

See `OPS.md` for production checklist and security considerations.

---

## 🔧 Configuration

### Risk Scoring Tuning

Edit `/app/backend/risk_config.json`:

```json
{
  "blacklist_addresses": [
    "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
  ],
  "suspicious_methods": [
    "proxy",
    "forceTransfer",
    "transferAll"
  ],
  "high_value_threshold": 1000000000000,
  "risk_weights": {
    "blacklist": 50,
    "suspicious_method": 30,
    "high_value": 25,
    "contract_call": 15
  }
}
```

### RPC Endpoints

Edit `/app/backend/polkadot_rpc.py` to add/change RPC endpoints:

```python
self.endpoints = {
    "polkadot": [
        "https://rpc.polkadot.io",
        "https://your-custom-rpc.com",
    ],
    # ...
}
```

---

## 📚 Documentation

- **OPS.md**: Complete operations guide (deployment, testing, troubleshooting)
- **API Docs**: http://localhost:8001/docs (interactive Swagger UI)
- **Code Comments**: All modules have detailed docstrings

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit with clear messages
4. Open PR with description

Ensure:

- Code follows project style
- Tests pass
- Documentation updated

---

## 📜 License

MIT License

Copyright © 2025 Deepak Raghunath Raut

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 📧 Contact

For questions, issues, or collaboration:

- GitHub: https://github.com/rauttech/safdo-crypto-shield
- Issues: https://github.com/rauttech/safdo-crypto-shield/issues

---

**Built with ❤️ for the Polkadot ecosystem**
