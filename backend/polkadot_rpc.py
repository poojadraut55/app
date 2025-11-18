# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
Polkadot RPC Manager with multi-endpoint failover support.
Supports Polkadot, Kusama, and Westend networks.
"""
import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class PolkadotRPCManager:
    def __init__(self):
        self.endpoints = {
            "polkadot": [
                "https://rpc.polkadot.io",
                "https://polkadot-rpc.dwellir.com",
                "https://polkadot.api.onfinality.io/public"
            ],
            "kusama": [
                "https://kusama-rpc.polkadot.io",
                "https://kusama-rpc.dwellir.com",
                "https://kusama.api.onfinality.io/public"
            ],
            "westend": [
                "https://westend-rpc.polkadot.io",
                "https://westend-rpc.dwellir.com"
            ]
        }
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def _rpc_call(self, endpoint: str, method: str, params: List) -> Optional[Dict]:
        """Make RPC call with timeout and error handling"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(endpoint, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "result" in data:
                            return data["result"]
                        elif "error" in data:
                            logger.error(f"RPC error from {endpoint}: {data['error']}")
                    else:
                        logger.error(f"HTTP {resp.status} from {endpoint}")
        except asyncio.TimeoutError:
            logger.warning(f"Timeout calling {endpoint}")
        except Exception as e:
            logger.error(f"Error calling {endpoint}: {str(e)}")
        
        return None
    
    async def _call_with_failover(self, chain: str, method: str, params: List) -> Optional[Dict]:
        """Call RPC with automatic failover to backup endpoints"""
        endpoints = self.endpoints.get(chain, [])
        
        for endpoint in endpoints:
            logger.debug(f"Trying {chain} RPC: {endpoint}")
            result = await self._rpc_call(endpoint, method, params)
            if result is not None:
                logger.info(f"Successful RPC call to {endpoint}")
                return result
            logger.warning(f"Failed RPC call to {endpoint}, trying next...")
        
        logger.error(f"All RPC endpoints failed for {chain}")
        return None
    
    async def get_balance(self, chain: str, address: str) -> Optional[Dict]:
        """Get balance for an address on a specific chain"""
        # Using system_account method to get balance
        result = await self._call_with_failover(
            chain,
            "system_account",
            [address]
        )
        
        if result:
            # Extract balance data
            balance_data = result.get("data", {})
            free_balance = int(balance_data.get("free", 0))
            reserved = int(balance_data.get("reserved", 0))
            frozen = int(balance_data.get("frozen", 0))
            
            return {
                "chain": chain,
                "address": address,
                "free": free_balance,
                "reserved": reserved,
                "frozen": frozen,
                "total": free_balance + reserved,
                "transferable": max(0, free_balance - frozen),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "chain": chain,
            "address": address,
            "error": "Failed to fetch balance",
            "free": 0,
            "total": 0
        }
    
    async def get_multi_chain_balance(self, address: str, chains: List[str]) -> List[Dict]:
        """Get balances across multiple chains concurrently"""
        tasks = [self.get_balance(chain, address) for chain in chains]
        balances = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        result = []
        for i, balance in enumerate(balances):
            if isinstance(balance, Exception):
                logger.error(f"Error fetching balance for {chains[i]}: {balance}")
                result.append({
                    "chain": chains[i],
                    "address": address,
                    "error": str(balance),
                    "free": 0,
                    "total": 0
                })
            else:
                result.append(balance)
        
        return result
    
    async def get_chain_info(self, chain: str) -> Optional[Dict]:
        """Get basic chain information"""
        # Get chain name and properties
        properties = await self._call_with_failover(chain, "system_properties", [])
        chain_name = await self._call_with_failover(chain, "system_chain", [])
        
        if properties:
            return {
                "chain": chain,
                "name": chain_name,
                "properties": properties,
                "decimals": properties.get("tokenDecimals", [10])[0],
                "symbol": properties.get("tokenSymbol", ["DOT"])[0]
            }
        
        return None
