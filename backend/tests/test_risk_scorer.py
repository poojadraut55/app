# © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
"""
Unit tests for Risk Scorer.
"""
import pytest
import asyncio
from risk_scorer import RiskScorer

@pytest.fixture
def risk_scorer():
    return RiskScorer()

@pytest.mark.asyncio
async def test_low_risk_transaction(risk_scorer):
    """Test normal transaction with low risk"""
    transaction = {
        "from_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "to_address": "5GNJqTPyNqANBkUVMN1LPPrxXnFouWXoe2wNSmmEoLctxiZY",
        "amount": "100000000000",  # 10 DOT
        "chain": "polkadot",
        "method": "transfer"
    }
    
    result = await risk_scorer.calculate_risk(transaction)
    
    assert result["score"] < 30
    assert result["level"] == "LOW"
    assert len(result["reasons"]) >= 1

@pytest.mark.asyncio
async def test_blacklisted_address(risk_scorer):
    """Test transaction with blacklisted address"""
    transaction = {
        "from_address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",  # Blacklisted
        "to_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "amount": "100000000000",
        "chain": "polkadot",
        "method": "transfer"
    }
    
    result = await risk_scorer.calculate_risk(transaction)
    
    assert result["score"] >= 50
    assert result["level"] in ["MEDIUM", "HIGH"]
    assert any("blacklist" in reason.lower() for reason in result["reasons"])

@pytest.mark.asyncio
async def test_high_value_transaction(risk_scorer):
    """Test high value transaction"""
    transaction = {
        "from_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "to_address": "5GNJqTPyNqANBkUVMN1LPPrxXnFouWXoe2wNSmmEoLctxiZY",
        "amount": "5000000000000",  # 500 DOT (high value)
        "chain": "polkadot",
        "method": "transfer"
    }
    
    result = await risk_scorer.calculate_risk(transaction)
    
    assert result["score"] >= 25
    assert any("high value" in reason.lower() for reason in result["reasons"])

@pytest.mark.asyncio
async def test_suspicious_method(risk_scorer):
    """Test transaction with suspicious method"""
    transaction = {
        "from_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "to_address": "5GNJqTPyNqANBkUVMN1LPPrxXnFouWXoe2wNSmmEoLctxiZY",
        "amount": "100000000000",
        "chain": "polkadot",
        "method": "proxy.transfer"  # Suspicious
    }
    
    result = await risk_scorer.calculate_risk(transaction)
    
    assert result["score"] >= 30
    assert result["level"] in ["MEDIUM", "HIGH"]
    assert any("suspicious method" in reason.lower() for reason in result["reasons"])

@pytest.mark.asyncio
async def test_contract_interaction(risk_scorer):
    """Test transaction with contract data"""
    transaction = {
        "from_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "to_address": "5GNJqTPyNqANBkUVMN1LPPrxXnFouWXoe2wNSmmEoLctxiZY",
        "amount": "100000000000",
        "chain": "polkadot",
        "method": "transfer",
        "data": "0x1234567890abcdef"  # Contract data
    }
    
    result = await risk_scorer.calculate_risk(transaction)
    
    assert result["score"] >= 15
    assert any("contract" in reason.lower() for reason in result["reasons"])

@pytest.mark.asyncio
async def test_multiple_risk_factors(risk_scorer):
    """Test transaction with multiple risk factors"""
    transaction = {
        "from_address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",  # Blacklisted
        "to_address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "amount": "10000000000000",  # Very high value
        "chain": "polkadot",
        "method": "forceTransfer"  # Suspicious
    }
    
    result = await risk_scorer.calculate_risk(transaction)
    
    assert result["score"] >= 80
    assert result["level"] == "HIGH"
    assert len(result["reasons"]) >= 2
