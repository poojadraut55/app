# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
IPFS Upload Proxy for web3.storage.
Mock implementation with security validations.
"""
import os
import logging
from typing import Dict
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class IPFSProxy:
    def __init__(self):
        self.web3_storage_token = os.getenv("WEB3_STORAGE_TOKEN", "")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
        self.allowed_extensions = [
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".pdf", ".txt", ".json", ".csv",
            ".mp4", ".webm"
        ]
        self.blocked_extensions = [
            ".exe", ".dll", ".so", ".sh", ".bat", ".cmd",
            ".js", ".py", ".rb", ".php"
        ]
        
        logger.info(f"IPFSProxy initialized (token configured: {bool(self.web3_storage_token)})")
    
    async def upload_mock(self) -> Dict:
        """
        Mock IPFS upload for demo/testing.
        In production, this would handle actual file upload with validation.
        """
        # Generate mock CID
        timestamp = datetime.utcnow().isoformat()
        mock_cid = hashlib.sha256(timestamp.encode()).hexdigest()[:46]
        
        logger.info(f"[MOCK] IPFS upload - CID: {mock_cid}")
        
        return {
            "cid": f"bafybeif{mock_cid}",
            "url": f"https://ipfs.io/ipfs/bafybeif{mock_cid}",
            "size": 12345,
            "timestamp": timestamp,
            "mock": True
        }
    
    def validate_file(self, filename: str, size: int) -> Dict:
        """
        Validate file for upload.
        Returns: {"valid": bool, "reason": str}
        """
        # Check size
        if size > self.max_file_size:
            return {
                "valid": False,
                "reason": f"File too large (max {self.max_file_size // 1024 // 1024}MB)"
            }
        
        # Check extension
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in self.blocked_extensions:
            return {
                "valid": False,
                "reason": f"Blocked file type: {ext}"
            }
        
        if ext not in self.allowed_extensions:
            return {
                "valid": False,
                "reason": f"File type not allowed: {ext}"
            }
        
        return {"valid": True, "reason": "File validation passed"}
