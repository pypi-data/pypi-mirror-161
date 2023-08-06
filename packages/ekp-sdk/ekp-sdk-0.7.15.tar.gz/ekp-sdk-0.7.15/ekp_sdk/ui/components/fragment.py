from ekp_sdk.util.clean_null_terms import clean_null_terms


def Fragment(children, class_name=None):
    return {
        "_type": "Fragment",
        "props": clean_null_terms({
            "className": class_name,
            "children": children,
        })
    }