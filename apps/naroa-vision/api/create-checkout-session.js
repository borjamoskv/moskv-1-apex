const Stripe = require('stripe');

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method Not Allowed' });
    }

    try {
        const stripe = Stripe(process.env.STRIPE_SECRET_KEY);
        const { tier } = req.body;
        const hostOrigin = req.headers.origin || 'https://moskv1.naroa.ai';
        
        let priceData = {};
        if (tier === 'C4-SIM') {
            priceData = {
                currency: 'eur',
                product_data: { name: 'MOSKV-1 Conversational Cluster (C4-SIM)' },
                unit_amount: 4900, 
            };
        } else if (tier === 'C5-REAL') {
            priceData = {
                currency: 'eur',
                product_data: { name: 'MOSKV-1 APEX Kernel Execution (C5-REAL)' },
                unit_amount: 49900, 
            };
        } else {
            return res.status(400).json({ error: 'Invalid exergy tier requested.' });
        }

        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card', 'sepa_debit'],
            line_items: [{ price_data: priceData, quantity: 1 }],
            mode: 'payment',
            billing_address_collection: 'required',
            tax_id_collection: { enabled: true },
            metadata: { 
                tier: tier, 
                justification: "Rendimientos de Actividades Económicas (Bizkaia)" 
            },
            success_url: `${hostOrigin}/success.html?session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${hostOrigin}/pricing.html`,
        });

        res.status(200).json({ id: session.id, url: session.url });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
}
