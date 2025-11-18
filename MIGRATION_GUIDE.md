# SAFDO Crypto Shield - Production Migration Guide

© 2025 Deepak Raghunath Raut — MIT Licensed

## Migrating from DRY-RUN to Production Notifications

This guide walks you through enabling real notifications after testing in dry-run mode.

---

## Phase 1: Testing in DRY-RUN Mode (Current State)

**Status:** ✅ Complete

Your application is currently running in **DRY-RUN mode**. All notification requests are:
- Logged to backend console
- Validated and dispatched
- NOT actually sent to channels

**Verification:**

```bash
# Check dry-run logs
tail -f /var/log/supervisor/backend.*.log | grep "\[DRY-RUN\]"
```

You should see logs like:
```
[DRY-RUN] Discord notification for user_123: security_alert
[DRY-RUN] Discord webhook URL: NOT_CONFIGURED
[DRY-RUN] Would send security_alert notification
```

---

## Phase 2: Enable Production Notifications

### Prerequisites Checklist

- [ ] All features tested in dry-run mode
- [ ] Obtained API credentials for desired channels
- [ ] Reviewed and updated blacklist in `risk_config.json`
- [ ] Backup current `.env` files
- [ ] Set up monitoring/logging for production

### Step 1: Discord Webhook Setup

**Get Discord Webhook:**

1. Go to your Discord server
2. Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Choose channel (e.g., #safdo-alerts)
5. Copy webhook URL

**Update Backend `.env`:**

```bash
cd /app/backend
nano .env
```

Add/update:
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**Test (still in dry-run):**

```bash
curl -X POST http://localhost:8001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "security_alert",
    "channels": ["discord"],
    "payload": {"message": "Test Discord webhook"},
    "user_id": "test"
  }'
```

Check logs - should show: `configured: true`

### Step 2: SMTP Email Setup

**Get SMTP Credentials:**

**Gmail Example:**
1. Enable 2FA on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Copy the password

**Update Backend `.env`:**

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

**Other Providers:**

| Provider | SMTP Host | Port | Notes |
|----------|-----------|------|-------|
| Gmail | smtp.gmail.com | 587 | Requires app password |
| Outlook | smtp-mail.outlook.com | 587 | Use account password |
| SendGrid | smtp.sendgrid.net | 587 | API key as password |
| AWS SES | email-smtp.region.amazonaws.com | 587 | SMTP credentials from console |

### Step 3: Generic Webhook Setup

**For custom integrations:**

```bash
GENERIC_WEBHOOK_URL=https://your-service.com/webhook
```

**Payload sent:**

```json
{
  "event_type": "transfer",
  "user_id": "5Grw...",
  "payload": { /* event data */ },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

Your webhook should respond with HTTP 200.

### Step 4: Enable Production Mode

**Critical Step:**

```bash
cd /app/backend
nano .env
```

Change:
```bash
NOTIFICATION_DRY_RUN=false
```

**Restart backend:**

```bash
sudo supervisorctl restart backend
```

**Verify:**

```bash
tail -f /var/log/supervisor/backend.*.log | grep "NotificationRelay initialized"
```

Should show: `(DRY_RUN: False)`

---

## Phase 3: Production Testing

### Test 1: Discord Notification

```bash
curl -X POST http://localhost:8001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "security_alert",
    "channels": ["discord"],
    "payload": {
      "message": "🚨 Production Test Alert",
      "risk_level": "HIGH",
      "amount": "1000 DOT"
    },
    "user_id": "production_test"
  }'
```

**Expected:** Message appears in your Discord channel!

### Test 2: Email Notification

**Note:** Email implementation requires completing SMTP handler. Currently returns `not_implemented_yet`.

To implement:
1. Install `aiosmtplib`: `pip install aiosmtplib`
2. Update `notification_relay.py` `_dispatch_email` method
3. Example implementation:

```python
import aiosmtplib
from email.mime.text import MIMEText

async def _dispatch_email(self, event_type, payload, user_id):
    if self.dry_run:
        # ... existing dry-run code
    
    if not (self.smtp_host and self.smtp_user):
        return {"channel": "email", "status": "not_configured"}
    
    # Create email
    msg = MIMEText(self._format_email_body(event_type, payload))
    msg['Subject'] = f"SAFDO Alert: {event_type}"
    msg['From'] = self.smtp_user
    msg['To'] = payload.get('email', 'user@example.com')
    
    try:
        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            start_tls=True
        )
        return {"channel": "email", "status": "sent"}
    except Exception as e:
        return {"channel": "email", "status": "error", "error": str(e)}
```

### Test 3: Multiple Channels

```bash
curl -X POST http://localhost:8001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "security_alert",
    "channels": ["discord", "webhook"],
    "payload": {
      "message": "Multi-channel test"
    },
    "user_id": "production_test"
  }'
```

**Expected:** Notifications sent to all configured channels.

---

## Phase 4: Monitoring & Maintenance

### Set Up Logging

**Production logging config:**

```bash
# In backend/.env
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

**Monitor logs:**

```bash
# Real-time monitoring
tail -f /var/log/supervisor/backend.*.log

# Filter for errors
tail -f /var/log/supervisor/backend.*.log | grep ERROR

# Filter for notification dispatches
tail -f /var/log/supervisor/backend.*.log | grep "notification"
```

### Rate Limiting

Current limits (per IP):
- `/api/notify`: 10 requests/minute
- `/api/risk-score`: 30 requests/minute
- `/api/chain-balance`: 20 requests/minute

To adjust, edit `server.py`:

```python
@api_router.post("/notify")
@limiter.limit("20/minute")  # Increase to 20
async def send_notification(request: Request, notif_req: NotificationRequest):
    # ...
```

### Database Monitoring

```bash
# Check notification logs in MongoDB
mongo
use safdo_crypto_shield
db.notifications.find().sort({timestamp: -1}).limit(10)
```

### Webhook Health Checks

**Discord:**

```bash
curl -X POST "https://discord.com/api/webhooks/YOUR_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"content": "Health check from SAFDO"}'
```

Should respond with HTTP 204.

---

## Phase 5: Rollback Plan

If issues occur, immediately rollback:

```bash
# Stop services
sudo supervisorctl stop backend

# Restore dry-run mode
cd /app/backend
sed -i 's/NOTIFICATION_DRY_RUN=false/NOTIFICATION_DRY_RUN=true/' .env

# Restart
sudo supervisorctl start backend
```

**Verify rollback:**

```bash
curl -X POST http://localhost:8001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "test",
    "channels": ["discord"],
    "payload": {},
    "user_id": "test"
  }' | grep '"dry_run": true'
```

---

## Additional Production Considerations

### Security Hardening

1. **Restrict CORS:**
```bash
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

2. **Enable HTTPS:**
- Use nginx/Caddy as reverse proxy
- Obtain SSL certificate (Let's Encrypt)

3. **Environment Secrets:**
- Never commit `.env` to git
- Use cloud provider secrets (AWS Secrets Manager, etc.)
- Rotate credentials regularly

### Scalability

**Horizontal Scaling:**

```bash
# Use gunicorn with multiple workers
gunicorn server:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --max-requests 1000 \
  --max-requests-jitter 50
```

**Database:**
- Use MongoDB replica set for HA
- Enable indexes on frequently queried fields
- Set up backup automation

### Cost Optimization

**Discord:** Free for webhooks

**Email (estimated monthly costs):**
- SendGrid: Free tier (100 emails/day)
- AWS SES: $0.10 per 1000 emails
- Mailgun: Free tier (5000 emails/month)

**Polkadot RPC:**
- Public endpoints: Free (rate-limited)
- Dedicated node: $50-200/month
- OnFinality: Free tier available

---

## Troubleshooting Production Issues

### Notifications Not Sending

**1. Check dry-run status:**
```bash
grep NOTIFICATION_DRY_RUN /app/backend/.env
# Should show: NOTIFICATION_DRY_RUN=false
```

**2. Check credentials:**
```bash
grep DISCORD_WEBHOOK_URL /app/backend/.env
# Should have actual URL, not empty
```

**3. Check logs:**
```bash
tail -f /var/log/supervisor/backend.*.log | grep -i "notif"
```

**4. Test webhook manually:**
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Manual test"}'
```

### Rate Limit Errors

**Symptom:** HTTP 429 responses

**Solution:**
1. Adjust rate limits in `server.py`
2. Implement request queuing
3. Use Redis for distributed rate limiting

### Database Connection Issues

**Check MongoDB:**
```bash
sudo systemctl status mongod
mongo --eval "db.adminCommand('ping')"
```

**Connection string:**
```bash
# In .env
MONGO_URL=mongodb://username:password@host:27017/database?authSource=admin
```

---

## Next Steps

After successful production migration:

1. **Monitoring:**
   - Set up Grafana/Prometheus for metrics
   - Configure Sentry for error tracking
   - Create alert rules for critical failures

2. **User Onboarding:**
   - Create user documentation
   - Add in-app tooltips and guides
   - Set up support channel

3. **Feature Expansion:**
   - Implement email SMTP handler
   - Add mobile push notifications (Firebase)
   - Create notification history UI
   - Add notification preferences per event type

4. **Performance:**
   - Enable Redis caching for RPC responses
   - Implement WebSocket for real-time updates
   - Add CDN for frontend assets

---

## Support

For production issues:
- GitHub Issues: https://github.com/rauttech/safdo-crypto-shield/issues
- Email: [your-support-email]
- Discord: [your-discord-server]

---

© 2025 Deepak Raghunath Raut — SAFDO Crypto Shield — MIT Licensed
