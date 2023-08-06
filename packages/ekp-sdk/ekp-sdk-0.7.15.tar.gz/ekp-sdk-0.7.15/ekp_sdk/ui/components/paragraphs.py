from ekp_sdk.util.clean_null_terms import clean_null_terms


def Paragraphs(children, class_name=None):
    return {
        "_type": "Paragraphs",
        "props": clean_null_terms({
            "class_name": class_name,
            "children": children,
        })
    }
