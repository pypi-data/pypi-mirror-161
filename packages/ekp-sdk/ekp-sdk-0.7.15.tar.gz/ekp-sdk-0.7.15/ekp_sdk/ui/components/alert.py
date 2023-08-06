from ekp_sdk.util.clean_null_terms import clean_null_terms


def Alert(content, header=None, icon_name=None, class_name=None, style=None, when=None):
    return {
        "_type": "Alert",
        "props": clean_null_terms({
            "content": content,
            "header": header,
            "iconName": icon_name,
            "className": class_name,
            "style": style,
            "when": when,
        })
    }