from ekp_sdk.util.clean_null_terms import clean_null_terms


def Datatable(
    data,
    columns,
    alert_config=None,
    busy_when=None,
    class_name=None,
    default_sort_asc=None,
    default_sort_field_id=None,
    default_view=None,
    disable_list_view=None,
    filters=None,
    grid_view=None,
    on_row_clicked=None,
    pagination=None,
    pagination_per_page=None,
    search_hint=None,
    show_export=None,
    show_last_updated=None,
    card=None,
    row_height=None
):
    return {
        "_type": "Datatable",
        "props": clean_null_terms({
            "alertConfig": alert_config,
            "busyWhen": busy_when,
            "card": card,
            "className": class_name,
            "columns": columns,
            "data": data,
            "defaultSortAsc": default_sort_asc,
            "defaultSortFieldId": default_sort_field_id,
            "defaultView": default_view,
            "disableListView": disable_list_view,
            "filters": filters,
            "gridView": grid_view,
            "onRowClicked": on_row_clicked,
            "pagination": pagination,
            "paginationPerPage": pagination_per_page,
            "searchHint": search_hint,
            "showExport": show_export,
            "showLastUpdated": show_last_updated,
            "rowHeight": row_height
        })
    }