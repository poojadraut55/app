# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
Unit tests for Notification Relay.
"""
import pytest
import os
from notification_relay import NotificationRelay

@pytest.fixture
def notification_relay():
    # Ensure dry-run mode for tests
    os.environ["NOTIFICATION_DRY_RUN"] = "true"
    return NotificationRelay()

@pytest.mark.asyncio
async def test_discord_notification_dry_run(notification_relay):
    """Test Discord notification in dry-run mode"""
    result = await notification_relay.dispatch(
        event_type="transfer",
        channels=["discord"],
        payload={"message": "Test transfer"},
        user_id="test_user"
    )
    
    assert result["status"] == "dispatched"
    assert result["dry_run"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["channel"] == "discord"
    assert result["results"][0]["status"] == "dry_run_logged"

@pytest.mark.asyncio
async def test_email_notification_dry_run(notification_relay):
    """Test email notification in dry-run mode"""
    result = await notification_relay.dispatch(
        event_type="staking",
        channels=["email"],
        payload={"message": "Staking reward"},
        user_id="test_user"
    )
    
    assert result["status"] == "dispatched"
    assert result["dry_run"] is True
    assert result["results"][0]["channel"] == "email"

@pytest.mark.asyncio
async def test_multiple_channels(notification_relay):
    """Test notification to multiple channels"""
    result = await notification_relay.dispatch(
        event_type="security_alert",
        channels=["discord", "email", "webhook"],
        payload={"message": "Security alert"},
        user_id="test_user"
    )
    
    assert result["status"] == "dispatched"
    assert len(result["results"]) == 3
    channels = [r["channel"] for r in result["results"]]
    assert "discord" in channels
    assert "email" in channels
    assert "webhook" in channels

@pytest.mark.asyncio
async def test_mobile_notification_not_implemented(notification_relay):
    """Test mobile push notification (not yet implemented)"""
    result = await notification_relay.dispatch(
        event_type="governance",
        channels=["mobile"],
        payload={"message": "Vote started"},
        user_id="test_user"
    )
    
    assert result["status"] == "dispatched"
    assert result["results"][0]["channel"] == "mobile"

@pytest.mark.asyncio
async def test_unsupported_channel(notification_relay):
    """Test unsupported channel"""
    result = await notification_relay.dispatch(
        event_type="transfer",
        channels=["sms"],  # Not supported
        payload={"message": "Test"},
        user_id="test_user"
    )
    
    assert result["results"][0]["status"] == "unsupported"
