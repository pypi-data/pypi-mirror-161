from ekp_sdk.util.clean_null_terms import clean_null_terms


def Timeline(events=None, title=None, content=None, style=None, class_name = None):
    return {
        "_type": "Timeline",
        "props": clean_null_terms({
            "className": class_name,
            "events": events or [],
            "title": title,
            "content": content,
            "style": style,
        })
    }