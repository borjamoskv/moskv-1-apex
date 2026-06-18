#!/bin/bash
echo "[MOSKV-1] Initializing C5-REAL Enterprise Demo Environment..."
cd demo_env
docker-compose up -d --build
echo ""
echo "[MOSKV-1] Environment active."
echo "Python Kernel (Cortex-Persist) on http://localhost:8000"
echo "Node Gateway (ACP Payments) on http://localhost:4242"
echo ""
echo "Try running Act 1:"
echo "curl -X POST http://localhost:4242/stripe-webhook \\"
echo "  -H 'stripe-signature: mock_sig_c5_real' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"type\": \"checkout.session.completed\", \"data\": {\"object\": {\"amount_total\": 50000, \"currency\": \"eur\", \"payment_method_types\": [\"card\"]}}}'"
