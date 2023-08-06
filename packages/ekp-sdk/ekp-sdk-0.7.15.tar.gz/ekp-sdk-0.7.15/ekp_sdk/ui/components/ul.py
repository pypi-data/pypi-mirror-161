from ekp_sdk.util.clean_null_terms import clean_null_terms


def Ul(items=None, style=None, class_name=None):
    return {
        "_type": "Ul",
        "props": clean_null_terms({
            "className": class_name,
            "style": style,
            "items": items or [],
        })
    }