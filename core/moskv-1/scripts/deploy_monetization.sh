#!/bin/zsh
# Execution Level: C5-REAL
# ZEO-GTM Monetization Deployment Script

echo "========================================================="
echo "   MOSKV-1 ZEO-GTM DEPLOYMENT PIPELINE (C5-REAL FIAT)    "
echo "========================================================="

if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "[!] STRIPE_SECRET_KEY environment variable is not set."
    echo "    For Vercel, this will be pushed securely. Are you running local daemon?"
fi

# 1. Deploy Frontend & API to Vercel
echo "[+] Deploying Naroa-Vision (Pricing Matrix) to Vercel..."
cd apps/naroa-vision || exit 1

# Auto-confirm deployment to production
npx vercel --prod --yes

echo "[+] Vercel deployment completed."
echo "[+] To configure Stripe Live Keys on Vercel Edge, run:"
echo "    npx vercel env add STRIPE_SECRET_KEY production"
echo "    npx vercel env add STRIPE_WEBHOOK_SECRET production"
echo "    npx vercel env add STRIPE_PUBLISHABLE_KEY production"

echo "========================================================="
echo " ZEO-GTM ACTIVE. Awaiting fiat liquidation via SEPA/IBAN "
echo "========================================================="
