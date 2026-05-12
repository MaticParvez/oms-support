# Getting Started with Open Money Stack (OMS)

## What is OMS?

Open Money Stack (OMS) by Polygon is a modular, open-source financial infrastructure stack that enables developers and enterprises to build payment rails, digital wallets, and DeFi products on Polygon's network.

## Key Components

### 1. Payment Rails
OMS provides programmable payment infrastructure for:
- Instant cross-border transfers
- Batch payment processing
- Recurring payments and subscriptions
- Fiat on/off ramp integrations

### 2. Wallet Infrastructure
- Non-custodial wallet creation and management
- Multi-sig support for enterprise accounts
- Transaction signing and broadcasting
- Gas abstraction (users don't need MATIC for fees)

### 3. Smart Contract Layer
- Pre-audited financial contract templates
- Token standards (ERC-20, ERC-4337 account abstraction)
- Escrow and settlement contracts
- Compliance hooks (KYC/AML integration points)

## Quick Start

### Prerequisites
- Node.js 18+ or Python 3.10+
- Polygon RPC endpoint (Polygon PoS or zkEVM)
- OMS API key (obtain from console.oms.polygon.technology)

### Installation

```bash
# Node.js
npm install @polygon/oms-sdk

# Python
pip install polygon-oms
```

### Initialize the Client

```javascript
import { OMSClient } from '@polygon/oms-sdk';

const client = new OMSClient({
  apiKey: process.env.OMS_API_KEY,
  network: 'polygon-mainnet', // or 'polygon-mumbai' for testnet
});
```

### Create a Wallet

```javascript
const wallet = await client.wallets.create({
  type: 'eoa',           // externally owned account
  label: 'User Wallet',
  metadata: { userId: 'usr_123' }
});

console.log(wallet.address); // 0x...
```

### Send a Payment

```javascript
const tx = await client.payments.send({
  from: wallet.id,
  to: '0xRecipientAddress',
  amount: '100',
  currency: 'USDC',
  memo: 'Invoice #1234'
});

console.log(tx.hash); // 0x...
```

## Networks Supported
- Polygon PoS Mainnet (chain ID: 137)
- Polygon zkEVM Mainnet (chain ID: 1101)
- Polygon Mumbai Testnet (chain ID: 80001)
- Polygon zkEVM Testnet (chain ID: 1442)

## Rate Limits
- Free tier: 100 requests/minute
- Pro tier: 1,000 requests/minute
- Enterprise: custom limits

## Support
- Documentation: docs.oms.polygon.technology
- Discord: discord.gg/polygon-oms
- Enterprise support: support@polygon.technology
