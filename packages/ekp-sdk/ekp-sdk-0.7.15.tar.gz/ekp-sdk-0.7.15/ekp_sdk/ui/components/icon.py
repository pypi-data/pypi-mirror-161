from ekp_sdk.util.clean_null_terms import clean_null_terms


def Icon(name, class_name=None, size=None, on_click=None, style=None):
    return {
        "_type": "Icon",
        "props": clean_null_terms({
            "className": class_name,
            "name": name,
            "size": size,
            "onClick": on_click,
            "style": style
        })
    }