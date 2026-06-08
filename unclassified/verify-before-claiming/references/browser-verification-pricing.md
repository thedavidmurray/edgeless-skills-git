# Verifying Pricing and Data Claims via Browser

## Pattern

When presenting pricing, statistics, or vendor-specific data in client-facing deliverables, always verify against the actual source before writing the number. Guessed pricing is the fastest way to destroy credibility.

## Workflow

1. **Identify all numbers in the deck that need verification**
   - Hardware prices (Apple Store, Amazon, vendor sites)
   - Software subscriptions (SaaS pricing pages)
   - Labor rates (market data, BLS, local rates)
   - Comparison figures (competitor pricing, industry benchmarks)

2. **Use browser tools to verify each source**
   - Navigate to the vendor's official pricing page
   - Read the actual price from the DOM
   - Note the date of verification
   - If the price has multiple tiers, document which tier you're using

3. **Document the verification in the deliverable**
   - Add a "Pricing verified against [source] on [date]" note
   - If an estimate, label it clearly as "Estimate" with the basis

4. **Maintain a reference file for reusable pricing**
   - Store verified prices in a reference file (e.g., `references/edgeless-pricing-verified.md`)
   - Update when re-verifying
   - Reuse for future decks without re-researching

## Example: Hardware Pricing

```
BEFORE (guessed):
"Mac mini M4 (16GB RAM) — $599"

AFTER (verified):
Navigate to https://www.apple.com/shop/buy-mac/mac-mini
Read from page: "$799" for M4 with 16GB (base config)
Corrected: "Mac mini M4, 16GB unified memory — $799.00"
Source: Apple Store, verified 2026-05-14
```

## Example: SaaS Pricing

```
BEFORE (guessed):
"Tailscale VPN + 1Password — $45"

AFTER (verified):
Navigate to https://tailscale.com/pricing
Read from page: "Personal — $0" (free forever, up to 6 users)
Navigate to https://1password.com/pricing
Read from page: "Teams Starter Pack — $19.95" (up to 10 users)
Corrected: "1Password Teams Starter — $19.95/mo. Tailscale Personal — $0/mo."
```

## Common Pitfalls

- **Stale memory prices** — Apple raised Mac mini prices. Your memory of "$599" is from M2 era.
- **Wrong tier** — Quoting Business tier when Starter tier suffices.
- **Per-user vs flat rate** — $7.99/user vs $19.95 flat for up to 10 users makes a huge difference.
- **Free tier oversight** — Many tools (Tailscale, GitHub basic, Telegram) are free for small use.
- **Estimate without label** — $80/month for "AI model access" is an estimate. Label it.

## Verification Log Format

When presenting itemized pricing, include:

```
| Item | Price | Source | Verified |
|------|-------|--------|----------|
| Mac mini M4 | $799.00 | Apple Store | 2026-05-14 |
| 1Password Teams | $19.95/mo | 1password.com | 2026-05-14 |
| AI model access | ~$80.00/mo | Estimate (moderate usage) | - |
```

This signals professionalism and allows future updates when prices change.
