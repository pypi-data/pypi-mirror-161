from ekp_sdk.util.clean_null_terms import clean_null_terms


def Row(children, class_name=None):
    return {
        "_type": "Row",
        "props": clean_null_terms({
            "className": class_name,
            "children": children
        })
    }