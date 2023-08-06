from ekp_sdk.util.clean_null_terms import clean_null_terms


def Card(children=None, class_name=None):
    return {
        "_type": "Card",
        "props": clean_null_terms({
            "children": children,
            "className": class_name
        })
    }