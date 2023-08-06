from ekp_sdk.util.clean_null_terms import clean_null_terms


def Div(children=None, class_name=None, style=None, when=None, context=None, background_url=None):
    return {
        "_type": "Div",
        "props": clean_null_terms({
            "className": class_name,
            "children": children or [],
            "style": style,
            "when": when,
            "context": context,
            "backgroundUrl": background_url,
        })
    }