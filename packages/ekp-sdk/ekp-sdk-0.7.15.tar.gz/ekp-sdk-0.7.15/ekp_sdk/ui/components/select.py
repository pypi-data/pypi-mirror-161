from ekp_sdk.util.clean_null_terms import clean_null_terms


def Select(label, name, options, min_width=None, class_name=None):
    return {
        "_type": "Select",
        "props": clean_null_terms({
            "className": class_name,
            "label": label,
            "name": name,
            "options": options,
            "minWidth": min_width,
        })
    }