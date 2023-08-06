from ekp_sdk.util.clean_null_terms import clean_null_terms


def Span(content, class_name=None, when=None):
    return {
        "_type": "Span",
        "props": clean_null_terms({
            "className": class_name,
            "content": content,
            "when": when
        })
    }