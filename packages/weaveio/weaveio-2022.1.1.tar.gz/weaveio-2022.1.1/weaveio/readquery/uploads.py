from astropy.table import Table
from typing import Tuple, Union

from weaveio.readquery.objects import ObjectQuery, AttributeQuery, TableVariableQuery


def join(table: Table, index_column: str,
         object_query: ObjectQuery, join_query: Union[AttributeQuery, str] = None,
         join_type: str = 'left') -> Tuple[TableVariableQuery, ObjectQuery]:
    """
    Add each row of an astropy table to a query object.
    The columns of each row will be accessible to all subsequent queries that fork from `object_query`.
    This would traditionally be called a "left join" since only all rows in the table will be returned
    even if there is no match to a weaveio object (null).
    Furthermore, weaveio objects that are not matched will not be returned.

    :param table: Astropy Table containing all data that you want to be accessible to the query
    :param index_column: Column in the table that will be used to join the table to the query object
    :param object_query: Query object that will be joined to the table
    :param join_query: Query object that will be used to join the table to the query object.
                       This can be any attribute query as long as it is singular wrt to `object_query`
                       Leave as None if you want to join the table to the query object using the index_column name as the attribute.
    :param join_type: Type of join to use. "left" is per row in table, "right" is per object in query.
    :return: A tuple of the table variable query and the query object

    Examples:
        Join a table where each row corresponds to a weave_target cname
        >>> table, weave_targets = join(table, 'cname', data.weave_targets, 'cname')
        `weave_targets` is the subset of `data.weave_targets` that is matched to the table
        `table` is the entire table

        Join a table where each row corresponds to a weave_target cname but is matched to a specific spectrum
        >>> query = data.runs[1234].l1single_spectra  # get all spectra belonging to this run
        >>> table, query = join(table, 'cname', query, query.weave_target.cname)
        `query` is the subset of `data.runs[1234].l1single_spectra` that is matched to the table
        `table` is the entire table

        Join a table where each row corresponds to an ob and matched based on the first mjd of that OB
        >>> table, query = join(table, 'mjd', data.obs, min(data.obs.exposures.mjd, wrt=data.obs))
        `query` is the subset of `data.obs` that is matched to the table
        `table` is the entire table
    """
    if join_query is None:
        join_query = index_column
    if isinstance(join_query, str):
        join_query = object_query[join_query]
    if not isinstance(join_query, AttributeQuery):
        raise TypeError(f"join_query must be an AttributeQuery or str, not {type(join_query)}")
    G = object_query._G
    param = G.add_parameter(table)
    row = G.add_unwind_parameter(object_query._node, param)
    index = G.add_getitem(row, index_column)
    eq, _ = G.add_combining_operation('{0} = {1}', 'ids', index, join_query._node)
    if join_type == 'left':  # per row in table, keep table, filter object
        reference = G.add_previous_reference(row, object_query._node)
        obj_node = G.add_filter(reference, eq, direct=False)
    elif join_type == 'right':  # per object in query, keep object, filter table
        row = G.add_filter(row, eq, direct=False)
        obj_node = G.add_previous_reference(row, object_query._node)
    else:
        raise ValueError(f"join_type must be 'left' or 'right', not {join_type}")
    return TableVariableQuery._spawn(object_query, row, '_row', single=True, table=table),\
           ObjectQuery._spawn(object_query, obj_node, object_query._obj, single=True)