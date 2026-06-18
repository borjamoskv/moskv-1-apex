export default function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ message: 'Method Not Allowed' });
    }

    res.status(200).json({
        publishableKey: process.env.STRIPE_PUBLISHABLE_KEY || 'pk_test_mock_c5_real_publishable_key'
    });
}
