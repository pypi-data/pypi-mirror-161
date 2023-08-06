from ekp_sdk.util.clean_null_terms import clean_null_terms


def Badge(color, children, class_name=None):
    return {
        "_type": "Badge",
        "props": clean_null_terms({
            "children": children,
            "className": class_name,
            "color": color,
        })
    }
