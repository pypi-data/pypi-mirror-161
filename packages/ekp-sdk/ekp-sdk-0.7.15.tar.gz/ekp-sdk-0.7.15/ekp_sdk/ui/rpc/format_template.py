def format_template(template, values):
    return {
        "method": "formatTemplate",
        "params": [template, values]
    }