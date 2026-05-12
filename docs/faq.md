# Frequently Asked Questions — OMS

## General

### What is OMS?
Open Money Stack (OMS) is Polygon's open-source financial infrastructure for building payment products, wallets, and DeFi applications. It abstracts away blockchain complexity so developers can focus on their product.

### Is OMS open source?
Yes. The core SDK and smart contracts are open source under the MIT license. Enterprise features (advanced analytics, dedicated RPC, SLAs) are commercial.

### Which networks does OMS support?
OMS supports Polygon PoS, Polygon zkEVM, and their respective testnets. Multi-chain expansion is on the roadmap.

## Developer Integration

### How do I get an API key?
Sign up at console.oms.polygon.technology. Free tier API keys are issued instantly. Enterprise keys require identity verification.

### What are the API rate limits?
- Free: 100 req/min, 10,000 req/day
- Pro: 1,000 req/min, 1M req/day
- Enterprise: custom — contact sales

### How do I handle transaction failures?
OMS returns error codes with retry guidance:
- `TX_UNDERPRICED`: Increase gas price and retry
- `NONCE_TOO_LOW`: Sync nonce with `client.wallet.syncNonce()`
- `INSUFFICIENT_FUNDS`: Check wallet balance before sending
- `REVERTED`: Check contract state and inputs

### Does OMS support EIP-4337 account abstraction?
Yes. Use `wallet.type = 'smart_account'` to create ERC-4337 smart wallets. This enables gas sponsorship and batch transactions.

### How does gas abstraction work?
OMS can sponsor gas fees for your users via the Paymaster service. Configure a gas policy in the dashboard to define which transactions to sponsor.

## Enterprise

### What SLAs are available?
- Pro: 99.9% uptime SLA
- Enterprise: 99.99% uptime SLA, dedicated support channel, 1-hour critical response

### Is OMS compliant with financial regulations?
OMS provides compliance hooks for KYC/AML integration. We are SOC 2 Type II certified. PCI-DSS compliance is available for card payment flows.

### How do we get dedicated infrastructure?
Contact enterprise@polygon.technology for dedicated RPC nodes, custom rate limits, and private blockchain networks.

## Wallets

### What wallet types are supported?
- `eoa`: Standard externally owned account
- `smart_account`: ERC-4337 smart wallet
- `multisig`: Gnosis Safe-compatible multi-signature wallet
- `mpc`: Multi-party computation wallet (enterprise only)

### How do I back up wallet keys?
OMS uses a non-custodial model — private keys are encrypted client-side. Use `wallet.exportEncryptedKey()` with your encryption key. Store backups securely.

### Can users recover wallets via social login?
Yes, with the Social Recovery module. Configure recovery guardians in the wallet settings.

## Payments

### What currencies are supported?
Native tokens (MATIC, ETH), ERC-20 tokens including USDC, USDT, DAI, WBTC. Custom token support available.

### How long do transactions take?
- Polygon PoS: ~2 seconds finality
- Polygon zkEVM: ~1 minute for L2 finality, ~30 minutes for L1 settlement

### Are there transaction fees?
OMS charges a 0.1% protocol fee on payment volume. Gas fees are separate and paid in MATIC (or sponsored via Paymaster).

## Security

### How do I report a security vulnerability?
Email security@polygon.technology with subject "OMS Security Disclosure". We follow responsible disclosure and offer a bug bounty program.

### Has OMS been audited?
Yes. Smart contracts are audited by Trail of Bits and Certik. Audit reports are available at docs.oms.polygon.technology/security.
