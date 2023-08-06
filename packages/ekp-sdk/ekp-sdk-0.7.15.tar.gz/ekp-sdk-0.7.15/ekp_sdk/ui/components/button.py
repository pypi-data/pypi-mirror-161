from ekp_sdk.util.clean_null_terms import clean_null_terms


def Button(
    busy_when=None,
    class_name=None,
    color=None,
    icon=None,
    is_submit=None,
    label=None,
    on_click=None,
    size=None,
    tooltip=None
):
    return {
        "_type": "Button",
        "props": clean_null_terms({
            "busyWhen": busy_when,
            "className": class_name,
            "color": color,
            "icon": icon,
            "isSubmit": is_submit,
            "label": label,
            "onClick": on_click,
            "size": size,
            "tooltip": tooltip,
        })
    }