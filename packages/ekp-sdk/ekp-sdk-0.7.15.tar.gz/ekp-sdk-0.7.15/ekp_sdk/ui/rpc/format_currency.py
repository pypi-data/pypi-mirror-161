def format_currency(rpc, symbol=None, round=True):
    return {
        "method": "formatCurrency",
        "params": [rpc, symbol, round]
    }
