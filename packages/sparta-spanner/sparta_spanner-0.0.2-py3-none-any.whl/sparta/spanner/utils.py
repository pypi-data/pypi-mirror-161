import typing

from google.cloud.spanner_v1.streamed import StreamedResultSet


def zip_results(result_set: StreamedResultSet, field_names: typing.List[str] = None):
    """
    :param result_set: the results
    :param field_names: list of field names. If none is provided, then we use the column names.
    :return: a list of dict(s) zipped with {field_name/column_name: column_value}
    """
    _results = []
    for row in result_set:
        if field_names is None:
            field_names = [field.name for field in result_set.fields]
        _results.append(dict(zip(field_names, row)))
    return _results
