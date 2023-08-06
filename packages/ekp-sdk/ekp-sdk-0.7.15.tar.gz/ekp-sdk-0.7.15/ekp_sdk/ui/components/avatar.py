from ekp_sdk.util.clean_null_terms import clean_null_terms


def Avatar(icon, size=None, color=None):
    return {
        "_type": "Avatar",
        "props": clean_null_terms({
            "color": color,
            "icon": icon,
            "size": size
        })
    }