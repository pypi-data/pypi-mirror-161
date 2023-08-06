def format_percent(value, showPlus=False, decimals=0):
    return {
        "method": "formatPercent",
        "params": [value, showPlus, decimals]
    }