const Stripe = require('stripe');

export const config = {
    api: {
        bodyParser: false,
    },
};

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method Not Allowed' });
    }

    const stripe = Stripe(process.env.STRIPE_SECRET_KEY);
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

    const buf = await new Promise((resolve, reject) => {
        const chunks = [];
        req.on('data', (chunk) => chunks.push(chunk));
        req.on('end', () => resolve(Buffer.concat(chunks)));
        req.on('error', reject);
    });

    const sig = req.headers['stripe-signature'];
    let event;

    try {
        event = stripe.webhooks.constructEvent(buf, sig, endpointSecret);
    } catch (err) {
        console.error(`[CORTEX-PAYMENT-ERR] Webhook signature verification failed: ${err.message}`);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        console.log(`[CORTEX-PAYMENT-OK] Exergy Liquidated. Payment of ${session.amount_total / 100} ${session.currency.toUpperCase()} successful.`);
        
        // This is where MOSKV-1 API or Ledger is updated on successful payment.
        // For serverless, this typically writes to Vercel KV, Supabase, or directly to a secured endpoint.
        // Fetch to MOSKV-1 daemon if exposed, or queue via serverless database.
        console.log(`[CORTEX-SWARM] Dispatching Autonomous Worker instantiation for Tier: ${session.metadata.tier}...`);
    }

    res.status(200).json({ received: true });
}
