# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
Unit tests for Polkadot RPC Manager.
"""
import pytest
from polkadot_rpc import PolkadotRPCManager

@pytest.fixture
def rpc_manager():
    return PolkadotRPCManager()

def test_rpc_manager_initialization(rpc_manager):
    """Test RPC manager initializes with correct endpoints"""
    assert "polkadot" in rpc_manager.endpoints
    assert "kusama" in rpc_manager.endpoints
    assert "westend" in rpc_manager.endpoints
    assert len(rpc_manager.endpoints["polkadot"]) > 0

@pytest.mark.asyncio
async def test_get_multi_chain_balance(rpc_manager):
    """Test fetching balances across multiple chains"""
    # Using a well-known address (may fail if RPC is down)
    address = "15oF4uVJwmo4TdGW7VfQxNLavjCXviqxT9S1MgbjMNHr6Sp5"
    chains = ["polkadot", "kusama"]
    
    balances = await rpc_manager.get_multi_chain_balance(address, chains)
    
    assert len(balances) == 2
    assert all("chain" in balance for balance in balances)
    assert all("address" in balance for balance in balances)

@pytest.mark.asyncio
async def test_get_balance_returns_structure(rpc_manager):
    """Test balance response structure"""
    address = "15oF4uVJwmo4TdGW7VfQxNLavjCXviqxT9S1MgbjMNHr6Sp5"
    
    balance = await rpc_manager.get_balance("polkadot", address)
    
    assert "chain" in balance
    assert "address" in balance
    assert "free" in balance or "error" in balance
    assert "total" in balance

@pytest.mark.asyncio
async def test_invalid_address_handling(rpc_manager):
    """Test handling of invalid address"""
    invalid_address = "invalid_address_format"
    
    balance = await rpc_manager.get_balance("polkadot", invalid_address)
    
    # Should return error structure, not crash
    assert "chain" in balance
    assert "address" in balance
