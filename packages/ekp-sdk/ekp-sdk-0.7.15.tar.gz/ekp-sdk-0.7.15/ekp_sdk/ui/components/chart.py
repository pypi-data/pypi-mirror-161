from ekp_sdk.util.clean_null_terms import clean_null_terms


def Chart(
        type,
        busy_when=None,
        card=None,
        class_name=None,
        data=None,
        height=400,
        name=None,
        options=None,
        period_days_select=None,
        series=None,
        style=None,
        title=None,
):
    return {
        "_type": "Chart",
        "props": clean_null_terms({
            "busyWhen": busy_when,
            "card": card,
            "className": class_name,
            "data": data,
            "height": height,
            "name": name,
            "options": options,
            "periodDaysSelect": period_days_select,
            "series": series,
            "style": style,
            "title": title,
            "type": type,
        })
    }