"""
Extract useful information from parsed SQL.
"""
from dslibrary.sql.compiled import Node_Field


def find_referenced_fields(node, adder=None):
    """
    Find all fields referenced in a given expression (node).
    :param node:    Expression to search.
    :param adder:   Method which will be called with each fieldName tuple.
    :return:    A set of unique fields if adder is not given, or None.
    """
    if adder is None:
        out = set()
        find_referenced_fields(node, out.add)
        return out
    if not node:
        return
    if isinstance(node, Node_Field):
        adder(node.fieldName)
        return
    if hasattr(node, "children"):
        for sub in node.children:
            find_referenced_fields(sub, adder)


def find_groupby_fields(group_by):
    """
    Find all fields used in a GROUP BY expression.
    """
    out = set()
    if group_by:
        for lvl in group_by.levels:
            out |= find_referenced_fields(lvl[0])
    return out


def find_orderby_fields(order_by):
    return find_groupby_fields(order_by)


def find_select_fields_pre_post(fields):
    """
    For 'Select.fields', which describes what calculations to make on input fields, return:
      (0) the set of input fields used
      (1) the set of output fields produced, in the form of a mapping from output field name to input field name
        when there is a 1:1 mapping, or to None when there is not.

    A+1 as A, B, A+B as C
    input fields used: A, B
    output fields: A -> None, B -> B, C -> C
    """
    f_in = set()
    f_out = {}
    for expr, alias in (fields or []):
        f_in |= find_referenced_fields(expr)
        if isinstance(expr, Node_Field):
            f_out[(alias,) if alias else expr.fieldName] = expr.fieldName
        elif alias:
            f_out[(alias,)] = None
    return f_in, f_out


def is_wildcard_all(fields):
    """
    Test for a wildcard indicating all fields are selected.
    """
    for expr, alias in (fields or []):
        if isinstance(expr, Node_Field) and expr.fieldName[-1] == "*":
            return True
    return False
