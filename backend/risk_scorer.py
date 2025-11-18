# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
Risk Scoring Service for SAFDO Crypto Shield.
Deterministic heuristic-based risk assessment for blockchain transactions.
"""
import json
import os
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class RiskScorer:
    def __init__(self):
        self.config = self._load_config()
        self.blacklist = self.config.get("blacklist_addresses", [])
        self.suspicious_methods = self.config.get("suspicious_methods", [])
        self.high_value_threshold = self.config.get("high_value_threshold", 1000000000000)
        
    def _load_config(self) -> Dict:
        """Load risk scoring configuration"""
        config_path = Path(__file__).parent / "risk_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default risk scoring configuration"""
        return {
            "blacklist_addresses": [
                "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",  # Example blacklist
            ],
            "suspicious_methods": [
                "proxy",
                "forceTransfer",
                "transferAll",
                "killAccount"
            ],
            "high_value_threshold": 1000000000000,  # 1000 DOT (in Planck)
            "risk_weights": {
                "blacklist": 50,
                "suspicious_method": 30,
                "high_value": 25,
                "contract_call": 15,
                "new_address": 10
            }
        }
    
    async def calculate_risk(self, transaction: Dict) -> Dict:
        """
        Calculate risk score for a transaction.
        Returns: {"score": int, "level": str, "reasons": List[str]}
        """
        score = 0
        reasons = []
        
        from_addr = transaction.get("from_address", "")
        to_addr = transaction.get("to_address", "")
        amount = int(transaction.get("amount", "0"))
        method = transaction.get("method", "")
        data = transaction.get("data", "")
        
        # Check blacklist
        if from_addr in self.blacklist or to_addr in self.blacklist:
            score += self.config["risk_weights"]["blacklist"]
            reasons.append("Address on blacklist")
            logger.warning(f"Blacklisted address detected: {from_addr} -> {to_addr}")
        
        # Check suspicious methods
        if method and any(sus in method.lower() for sus in self.suspicious_methods):
            score += self.config["risk_weights"]["suspicious_method"]
            reasons.append(f"Suspicious method: {method}")
            logger.warning(f"Suspicious method detected: {method}")
        
        # Check high value
        if amount > self.high_value_threshold:
            score += self.config["risk_weights"]["high_value"]
            value_in_dot = amount / 10**10
            reasons.append(f"High value transfer: {value_in_dot:.2f} DOT")
            logger.info(f"High value transaction: {value_in_dot} DOT")
        
        # Check contract call (has data field)
        if data and len(data) > 10:
            score += self.config["risk_weights"]["contract_call"]
            reasons.append("Contract interaction detected")
        
        # Determine risk level
        if score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"
            if not reasons:
                reasons.append("Transaction appears normal")
        
        logger.info(f"Risk assessment: score={score}, level={level}, tx={from_addr[:10]}...")
        
        return {
            "score": min(score, 100),  # Cap at 100
            "level": level,
            "reasons": reasons
        }
