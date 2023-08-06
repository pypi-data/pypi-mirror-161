from ekp_sdk.util.clean_null_terms import clean_null_terms


def Column(
    id,
    cell=None,
    format=None,
    grow=None,
    omit=None,
    min_width=None,
    right=None,
    searchable=None,
    sortable=None,
    title=None,
    value=None,
    width=None,
    compact=None
):
    return clean_null_terms({
        "cell": cell,
        "format": format,
        "grow": grow,
        "id": id,
        "minWidth": min_width,
        "omit": omit,
        "right": right,
        "searchable": searchable,
        "sortable": sortable,
        "title": title,
        "value": value,
        "width": width,
        "compact": compact
    })