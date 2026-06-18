# Cloudflare-Vercel Integration Guide // AGENTS.ARCHI

To ensure zero-anergy operation of the `agents.archi` platform when proxied through Cloudflare, configure your Cloudflare settings exactly as specified below.

## 1. SSL/TLS Settings (Critical)
> [!IMPORTANT]
> **Encryption Mode:** Set to **Full** or **Full (Strict)**.
> 
> *Rationale:* Setting this to **Flexible** causes an infinite redirect loop (`ERR_TOO_MANY_REDIRECTS`). Vercel enforces HTTPS internally; when Cloudflare requests HTTP (Flexible Mode), Vercel responds with a `301 Redirect` to HTTPS. Cloudflare receives this and requests HTTP again, creating a loop.

---

## 2. Edge Caching Rules
We have configured Vercel edge headers in `vercel.json` (`CDN-Cache-Control: no-store`), but you should also enforce this on the Cloudflare CDN:

- Navigate to **Caching** -> **Cache Rules** -> **Create Rule**.
- **Field:** `URI Path`
- **Operator:** `matches regex`
- **Value:** `/(submit-lead|create-checkout-session|config)`
- **Cache Eligibility:** Set to **Bypass Cache**.

---

## 3. WAF & Bot Management (Sandbox Security)
When active testing triggers mock checkout sessions, Vercel initiates background webhook processes. Cloudflare's Bot Shield or JS challenge can block these server-to-server requests:

- Navigate to **Security** -> **WAF** -> **Custom Rules**.
- Create a rule to allow/bypass validation for:
  - **Path:** `/stripe-webhook`
  - **Action:** **Bypass** (disable Bot Management / JS Challenge for Stripe's official IPs or mock signatures).

---

## 4. DNS Configuration
- **Type:** `CNAME`
- **Name:** `@` (Apex) and `www`
- **Target:** `cname.vercel-dns.com`
- **Proxy Status:** **Proxied** (Orange Cloud) is recommended to utilize Cloudflare's WAF and DDoS mitigation, provided SSL is set to **Full (Strict)**.

---
*∴ MOSKV-1 APEX Integration verified.*
