from ekp_sdk.util.clean_null_terms import clean_null_terms


def Col(class_name=None, children=None, when=None):
    return {
        "_type": "Col",
        "props": clean_null_terms({
            "className": class_name,
            "children": children or [],
            "when": when
        })
    }