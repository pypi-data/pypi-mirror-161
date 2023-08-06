from ekp_sdk.util.clean_null_terms import clean_null_terms


def Image(src, style=None, class_name=None, when=None, tooltip=None, rounded=None):
    return {
        "_type": "Image",
        "props": clean_null_terms({
            "src": src,
            "style": style,
            "className": class_name,
            "rounded": rounded,
            "when": when,
            "tooltip": tooltip
        })
    }