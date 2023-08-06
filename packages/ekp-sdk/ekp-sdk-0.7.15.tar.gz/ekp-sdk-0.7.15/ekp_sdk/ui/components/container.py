from ekp_sdk.util.clean_null_terms import clean_null_terms


def Container(children, class_name=None, context=None):
    return {
        "_type": "Container",
        "props": clean_null_terms({
            "className": class_name,
            "children": children,
            "context": context
        })
    }