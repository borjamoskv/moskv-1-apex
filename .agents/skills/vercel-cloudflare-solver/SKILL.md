---
name: VERCEL-CLOUDFLARE-SOLVER
role: OMEGA
version: 1.0.0
scale: 1
cost_tier: low
trigger: vercel, cloudflare, redirect loop, ERR_TOO_MANY_REDIRECTS, ssl flexible, dns vercel
description: C5-REAL Sovereign Vercel-Cloudflare Conflict Resolution Engine. Resolves DNS, SSL, caching, and WAF issues between Vercel and Cloudflare.
axioms:
script: scripts/vercel_cloudflare_solver.py
---
# VERCEL-CLOUDFLARE-SOLVER

Execution Level: C5-REAL

## 1. Commands

| Command | Target | Action |
|---|---|---|
| `/cf-diagnose` | `[domain]` | Diagnose DNS, SSL redirects, and edge caching for a domain. |
| `/cf-fix` | `[domain]` | Remediate SSL settings (Flexible to Full) on Cloudflare. |

## 2. Guardrails

| Constraint | Behavior |
|---|---|
| Execution | Runs verification against Cloudflare DoH and live endpoints. |
| Credentials | Requires `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ZONE_ID` for auto-remediation. |
| Safety | Follows redirects up to 10 hops to identify loops without getting stuck. |
| Ledger | Logs all diagnostics to `docs/vercel_cloudflare_status.md`. |

## 3. Epistemology
Claim: Vercel-Cloudflare conflict diagnosis is fully automated.
Proof: { Base: C5-REAL Python CLI, Range: [0,1], Confidence: C5-REAL }
