# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
Notification Relay Service - DRY RUN MODE
Supports Discord, Email (SMTP), Webhook, and Mobile Push (planned).
Currently logs dispatch targets without actual sending.
"""
import os
import logging
from typing import Dict, List
import aiohttp
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationRelay:
    def __init__(self):
        self.dry_run = os.getenv("NOTIFICATION_DRY_RUN", "true").lower() == "true"
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL", "")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.webhook_url = os.getenv("GENERIC_WEBHOOK_URL", "")
        
        logger.info(f"NotificationRelay initialized (DRY_RUN: {self.dry_run})")
    
    async def dispatch(self, event_type: str, channels: List[str], payload: Dict, user_id: str) -> Dict:
        """
        Dispatch notification to specified channels.
        In DRY_RUN mode, only logs the dispatch targets.
        """
        results = []
        
        for channel in channels:
            if channel == "discord":
                result = await self._dispatch_discord(event_type, payload, user_id)
            elif channel == "email":
                result = await self._dispatch_email(event_type, payload, user_id)
            elif channel == "webhook":
                result = await self._dispatch_webhook(event_type, payload, user_id)
            elif channel == "mobile":
                result = await self._dispatch_mobile(event_type, payload, user_id)
            else:
                result = {"channel": channel, "status": "unsupported"}
            
            results.append(result)
        
        return {
            "status": "dispatched" if self.dry_run else "sent",
            "dry_run": self.dry_run,
            "event_type": event_type,
            "user_id": user_id,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _dispatch_discord(self, event_type: str, payload: Dict, user_id: str) -> Dict:
        """Dispatch to Discord webhook"""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Discord notification for {user_id}: {event_type}")
            logger.info(f"[DRY-RUN] Discord webhook URL: {self.discord_webhook or 'NOT_CONFIGURED'}")
            logger.info(f"[DRY-RUN] Payload: {payload}")
            return {
                "channel": "discord",
                "status": "dry_run_logged",
                "configured": bool(self.discord_webhook),
                "message": f"Would send {event_type} notification"
            }
        
        if not self.discord_webhook:
            logger.warning("Discord webhook not configured")
            return {"channel": "discord", "status": "not_configured"}
        
        # Actual Discord dispatch (when not in dry-run)
        try:
            message = self._format_discord_message(event_type, payload)
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook, json={"content": message}) as resp:
                    if resp.status == 204:
                        logger.info(f"Discord notification sent for {user_id}")
                        return {"channel": "discord", "status": "sent"}
                    else:
                        logger.error(f"Discord webhook error: {resp.status}")
                        return {"channel": "discord", "status": "failed", "error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"Discord dispatch error: {str(e)}")
            return {"channel": "discord", "status": "error", "error": str(e)}
    
    async def _dispatch_email(self, event_type: str, payload: Dict, user_id: str) -> Dict:
        """Dispatch via SMTP email"""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Email notification for {user_id}: {event_type}")
            logger.info(f"[DRY-RUN] SMTP configured: {bool(self.smtp_host and self.smtp_user)}")
            logger.info(f"[DRY-RUN] Would send to: {payload.get('email', 'user@example.com')}")
            return {
                "channel": "email",
                "status": "dry_run_logged",
                "configured": bool(self.smtp_host and self.smtp_user),
                "message": f"Would send {event_type} email"
            }
        
        if not (self.smtp_host and self.smtp_user):
            logger.warning("SMTP not configured")
            return {"channel": "email", "status": "not_configured"}
        
        # Actual SMTP dispatch would go here
        logger.info("Email dispatch (actual implementation pending)")
        return {"channel": "email", "status": "not_implemented_yet"}
    
    async def _dispatch_webhook(self, event_type: str, payload: Dict, user_id: str) -> Dict:
        """Dispatch to generic webhook"""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Webhook notification for {user_id}: {event_type}")
            logger.info(f"[DRY-RUN] Webhook URL: {self.webhook_url or 'NOT_CONFIGURED'}")
            logger.info(f"[DRY-RUN] Payload: {payload}")
            return {
                "channel": "webhook",
                "status": "dry_run_logged",
                "configured": bool(self.webhook_url),
                "message": f"Would POST {event_type} to webhook"
            }
        
        if not self.webhook_url:
            logger.warning("Webhook URL not configured")
            return {"channel": "webhook", "status": "not_configured"}
        
        # Actual webhook dispatch
        try:
            webhook_payload = {
                "event_type": event_type,
                "user_id": user_id,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=webhook_payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        logger.info(f"Webhook notification sent for {user_id}")
                        return {"channel": "webhook", "status": "sent"}
                    else:
                        logger.error(f"Webhook error: {resp.status}")
                        return {"channel": "webhook", "status": "failed", "error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"Webhook dispatch error: {str(e)}")
            return {"channel": "webhook", "status": "error", "error": str(e)}
    
    async def _dispatch_mobile(self, event_type: str, payload: Dict, user_id: str) -> Dict:
        """Dispatch mobile push notification (planned)"""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Mobile push for {user_id}: {event_type}")
            logger.info(f"[DRY-RUN] Would send push notification")
            return {
                "channel": "mobile",
                "status": "dry_run_logged",
                "configured": False,
                "message": f"Would send {event_type} push notification"
            }
        
        logger.info("Mobile push (implementation planned)")
        return {"channel": "mobile", "status": "not_implemented_yet"}
    
    def _format_discord_message(self, event_type: str, payload: Dict) -> str:
        """Format payload into Discord message"""
        title = f"🔔 SAFDO Alert: {event_type.upper()}"
        lines = [title, ""]
        for key, value in payload.items():
            lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
        return "\n".join(lines)
