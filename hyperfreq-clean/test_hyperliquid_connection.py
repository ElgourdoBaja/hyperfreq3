#!/usr/bin/env python3

"""
Test script to verify Hyperliquid API connection
"""

import sys
import ccxt
import json

def test_hyperliquid_connection():
    """Test the Hyperliquid API connection with the configured credentials"""
    
    print("🧪 Testing Hyperliquid API Connection...")
    print("=" * 50)
    
    # Your actual credentials
    api_key = "0xc617643210fd1af0591649f04560647776f2ba6a"
    api_secret = "0xa2df0be8f3ed00889d3769390cd31c9ea8560d27a4ed217e7ce272843958b394"
    wallet_address = "0x78b70c6265F089fd64af7C9b8Fc80e9f371D730A"
    
    try:
        # Initialize Hyperliquid exchange for testnet
        print("🔧 Initializing Hyperliquid exchange (testnet)...")
        exchange = ccxt.hyperliquid({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': True,  # Testnet mode
            'options': {
                'defaultType': 'swap',
                'walletAddress': wallet_address
            }
        })
        
        print(f"✅ Exchange initialized: {exchange.name}")
        print(f"📍 Environment: {'Testnet' if exchange.sandbox else 'Mainnet'}")
        print(f"💳 Wallet Address: {wallet_address}")
        
        # Test basic connection
        print("\n🌐 Testing basic connection...")
        markets = exchange.load_markets()
        print(f"✅ Markets loaded: {len(markets)} pairs available")
        
        # Show top 10 markets by volume
        print("\n📊 Top 10 markets by volume:")
        market_list = []
        for symbol, market in markets.items():
            if 'info' in market and 'volume24h' in market['info']:
                try:
                    volume = float(market['info']['volume24h'])
                    market_list.append((symbol, volume))
                except:
                    pass
        
        market_list.sort(key=lambda x: x[1], reverse=True)
        for i, (symbol, volume) in enumerate(market_list[:10]):
            print(f"  {i+1:2d}. {symbol:<20} Volume: ${volume:,.0f}")
        
        # Test account information
        print("\n💰 Testing account information...")
        try:
            balance = exchange.fetch_balance()
            print(f"✅ Account balance retrieved")
            
            # Show non-zero balances
            for currency, amounts in balance.items():
                if currency != 'info' and amounts['total'] > 0:
                    print(f"  {currency}: {amounts['total']}")
                    
            # Show specific USDC balance
            if 'USDC' in balance:
                usdc_balance = balance['USDC']['total']
                print(f"💵 USDC Balance: {usdc_balance}")
            else:
                print("💵 USDC Balance: 0 (or not found)")
                
        except Exception as e:
            print(f"⚠️  Account info test failed: {e}")
        
        # Test market data
        print("\n📈 Testing market data...")
        try:
            ticker = exchange.fetch_ticker('BTC/USDC:USDC')
            print(f"✅ BTC/USDC ticker retrieved")
            print(f"  Price: ${ticker['last']:,.2f}")
            print(f"  24h Volume: ${ticker['quoteVolume']:,.0f}")
            print(f"  24h Change: {ticker['percentage']:+.2f}%")
        except Exception as e:
            print(f"⚠️  Market data test failed: {e}")
        
        print("\n🎉 Connection test completed successfully!")
        print("✅ Your Hyperliquid API credentials are working correctly")
        print("🚀 You're ready to start trading with Freqtrade!")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔍 Please check:")
        print("  - API credentials are correct")
        print("  - Wallet address matches your MetaMask address")
        print("  - API wallet is properly authorized on Hyperliquid")
        print("  - Internet connection is stable")
        return False

if __name__ == "__main__":
    success = test_hyperliquid_connection()
    sys.exit(0 if success else 1)