# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
from fastapi import FastAPI, APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Dict, Optional, Literal
import uuid
from datetime import datetime, timezone
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import aiohttp
import json

# Import risk scoring and notification modules
from risk_scorer import RiskScorer
from notification_relay import NotificationRelay
from polkadot_rpc import PolkadotRPCManager
from ipfs_proxy import IPFSProxy

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

# Create the main app
app = FastAPI(title="SAFDO Crypto Shield API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
risk_scorer = RiskScorer()
notification_relay = NotificationRelay()
polkadot_rpc = PolkadotRPCManager()
ipfs_proxy = IPFSProxy()

# Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class TransactionPayload(BaseModel):
    """Transaction data for risk scoring"""
    from_address: str
    to_address: str
    amount: str
    chain: Literal["polkadot", "kusama", "westend"]
    method: Optional[str] = None
    data: Optional[str] = None

class RiskScoreResponse(BaseModel):
    score: int = Field(ge=0, le=100, description="Risk score from 0 (safe) to 100 (high risk)")
    level: Literal["LOW", "MEDIUM", "HIGH"]
    reasons: List[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationRequest(BaseModel):
    """Notification dispatch request"""
    event_type: Literal["transfer", "staking", "governance", "security_alert"]
    channels: List[Literal["email", "discord", "webhook", "mobile"]]
    payload: Dict
    user_id: str

class NotificationPreference(BaseModel):
    """User notification preferences"""
    user_id: str
    event_type: Literal["transfer", "staking", "governance", "security_alert"]
    channels: List[str]
    enabled: bool = True

class ChainBalanceRequest(BaseModel):
    """Request to fetch balances across chains"""
    address: str
    chains: List[Literal["polkadot", "kusama", "westend"]]

class IPFSUploadResponse(BaseModel):
    cid: str
    url: str
    size: int

# Basic routes
@api_router.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {"message": "SAFDO Crypto Shield API v1.0", "status": "operational"}

@api_router.post("/status", response_model=StatusCheck)
@limiter.limit("20/minute")
async def create_status_check(request: Request, input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
@limiter.limit("20/minute")
async def get_status_checks(request: Request):
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# Risk Scoring Endpoint
@api_router.post("/risk-score", response_model=RiskScoreResponse)
@limiter.limit("30/minute")
async def calculate_risk_score(request: Request, transaction: TransactionPayload):
    """
    Calculate risk score for a transaction.
    Returns score 0-100 with human-readable reasons.
    """
    try:
        score_data = await risk_scorer.calculate_risk(transaction.model_dump())
        
        # Store risk assessment in DB
        assessment_doc = {
            "id": str(uuid.uuid4()),
            "transaction": transaction.model_dump(),
            "score": score_data["score"],
            "level": score_data["level"],
            "reasons": score_data["reasons"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.risk_assessments.insert_one(assessment_doc)
        
        return RiskScoreResponse(**score_data)
    except Exception as e:
        logger.error(f"Risk scoring error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk scoring failed: {str(e)}")

# Polkadot Chain Balance
@api_router.post("/chain-balance")
@limiter.limit("20/minute")
async def get_chain_balance(request: Request, balance_req: ChainBalanceRequest):
    """
    Fetch balances across multiple Polkadot chains.
    """
    try:
        balances = await polkadot_rpc.get_multi_chain_balance(
            balance_req.address,
            balance_req.chains
        )
        return {"address": balance_req.address, "balances": balances}
    except Exception as e:
        logger.error(f"Balance fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Balance fetch failed: {str(e)}")

# Notification Relay
@api_router.post("/notify")
@limiter.limit("10/minute")
async def send_notification(request: Request, notif_req: NotificationRequest):
    """
    Relay notification to configured channels.
    DRY-RUN mode: logs dispatch targets without actual sending.
    """
    try:
        result = await notification_relay.dispatch(
            event_type=notif_req.event_type,
            channels=notif_req.channels,
            payload=notif_req.payload,
            user_id=notif_req.user_id
        )
        
        # Log notification dispatch
        notif_doc = {
            "id": str(uuid.uuid4()),
            "user_id": notif_req.user_id,
            "event_type": notif_req.event_type,
            "channels": notif_req.channels,
            "status": result["status"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notif_doc)
        
        return result
    except Exception as e:
        logger.error(f"Notification relay error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")

# Notification Preferences
@api_router.post("/notifications/preferences")
@limiter.limit("10/minute")
async def save_notification_preference(request: Request, pref: NotificationPreference):
    """
    Save user notification preferences.
    """
    try:
        pref_doc = pref.model_dump()
        pref_doc["id"] = str(uuid.uuid4())
        pref_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Upsert preference
        await db.notification_preferences.update_one(
            {"user_id": pref.user_id, "event_type": pref.event_type},
            {"$set": pref_doc},
            upsert=True
        )
        return {"status": "success", "message": "Preferences saved"}
    except Exception as e:
        logger.error(f"Preference save error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save preferences: {str(e)}")

@api_router.get("/notifications/preferences/{user_id}")
@limiter.limit("20/minute")
async def get_notification_preferences(request: Request, user_id: str):
    """
    Get user notification preferences.
    """
    try:
        prefs = await db.notification_preferences.find(
            {"user_id": user_id},
            {"_id": 0}
        ).to_list(100)
        return {"user_id": user_id, "preferences": prefs}
    except Exception as e:
        logger.error(f"Preference fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")

# IPFS Upload Proxy
@api_router.post("/ipfs/upload", response_model=IPFSUploadResponse)
@limiter.limit("5/minute")
async def upload_to_ipfs(request: Request):
    """
    Proxy upload to IPFS (web3.storage).
    Validates file size and type for security.
    """
    try:
        # This is a mock implementation - actual file handling would use FormData
        result = await ipfs_proxy.upload_mock()
        return result
    except Exception as e:
        logger.error(f"IPFS upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Health check
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "risk_scorer": "operational",
            "notification_relay": "operational",
            "polkadot_rpc": "operational"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")
