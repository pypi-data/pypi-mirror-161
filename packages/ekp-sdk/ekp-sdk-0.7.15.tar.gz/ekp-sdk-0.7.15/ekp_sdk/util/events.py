def client_currency(event):
    if (event is None):
        return None

    if ("state" not in event.keys()):
        return None

    if ("client" not in event["state"].keys()):
        return None

    if ("selectedCurrency" not in event["state"]["client"].keys()):
        return None

    return event["state"]["client"]["selectedCurrency"]

def client_is_subscribed(event):
    if (event is None):
        return False

    if ("state" not in event.keys()):
        return False

    if ("client" not in event["state"].keys()):
        return False

    if ("subscribed" not in event["state"]["client"].keys()):
        return False

    return event["state"]["client"]["subscribed"]

def client_path(event):
    if (event is None):
        return None

    if ("state" not in event.keys()):
        return None

    if ("client" not in event["state"].keys()):
        return None

    if ("path" not in event["state"]["client"].keys()):
        return None

    return event["state"]["client"]["path"]


def form_value(event, form_name, property_name):
    if (event is None):
        return None

    if ("state" not in event.keys()):
        return None

    if ("forms" not in event["state"].keys()):
        return None

    if (form_name not in event["state"]["forms"].keys()):
        return None

    if (property_name not in event["state"]["forms"][form_name].keys()):
        return None

    return event["state"]["forms"][form_name][property_name]


def form_values(event, form_name):
    if (event is None):
        return None

    if ("state" not in event.keys()):
        return None

    if ("forms" not in event["state"].keys()):
        return None

    if (form_name not in event["state"]["forms"].keys()):
        return None

    return event["state"]["forms"][form_name]


def client_query_param(event, key):
    if (event is None):
        return None

    if ("state" not in event.keys()):
        return None

    if ("client" not in event["state"].keys()):
        return None

    if ("queryParams" not in event["state"]["client"].keys()):
        return None

    if (key not in event["state"]["client"]["queryParams"].keys()):
        return None

    return event["state"]["client"]["queryParams"][key]
