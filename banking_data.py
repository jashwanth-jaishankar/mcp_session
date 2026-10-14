TRADES = [
    {
        "trade_id": "FX101",
        "pair": "EUR/USD",
        "amount": 100000,
        "status": "UNSETTLED"
    },
    {
        "trade_id": "FX102",
        "pair": "USD/INR",
        "amount": 50000,
        "status": "SETTLED"
    }
]

PAYMENTS = {
    "PAY101": {
        "payment_id": "PAY101",
        "status": "PROCESSING",
        "currency": "EUR",
        "amount": 100000
    }
}


def get_unsettled_trades():
    return [
        trade for trade in TRADES
        if trade["status"] == "UNSETTLED"
    ]


def get_payment_status(payment_id: str):
    return PAYMENTS.get(
        payment_id.upper(),
        {"error": "Payment not found"}
    )