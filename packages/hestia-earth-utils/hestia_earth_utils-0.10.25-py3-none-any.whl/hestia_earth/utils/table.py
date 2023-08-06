import re
from functools import reduce
import numpy as np
from hestia_earth.schema import NodeType

from .tools import flatten

PIVOT_FIELD_1 = 'depthUpper'
PIVOT_FIELD_2 = 'depthLower'
PIVOT_FIELD_DEFAULT = 'depthUnspecified'


def _drop_col_list(df, names: list):
    """
    Drop all columns of df which match the strings of the names parameter.

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe which columns are supposed to be dropped
    names : list
        list of columns with partial match to drop

    Returns
    -------
    df : pandas.DataFrame
        return the dataframe without the columns
    """
    return df.drop(reduce(lambda prev, name: prev + [x for x in list(df.columns) if name in x], names, []), axis=1)


def _name_to_id(name: str):
    """
    Strip all special characters and spaces from name-string.

    Parameters
    ----------
    name : string
        name of the field, which will be altered

    Returns
    -------
    name : string
        name of field which is now in the form of id
    """
    name = str(name).title()
    name = name[0].lower() + name[1:]
    name = name.replace(" ", "")
    name = re.sub(r"[^a-zA-Z0-9. ]", "", name)
    return name


def _identify_dict(df, columns: list, pivot_field: str):
    """
    Identifies the naming of the column header the column value belongs to.

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe from which the naes are extracted
    columns : list
        column names from which the names of values are extracted
    pivot_field : string
        name of pivot_field to determine the naming of the new fields

    Returns
    -------
    output_dict : dictionary
        primary output, dictionary with the names of the terms as keys and their abbreviated column header as key
    name_to_id_dict : dictionary
        dictionary with term name as key and new column name as value
    """
    def map_column(prev: dict, curr: dict):
        name = re.match(r"^.*\.[a-zA-Z]+\.[\d]", curr)
        prev[name[0][:-2]] = prev.get(name[0][:-2], []) + list(df[curr].values)
        return prev

    prelim_dict = reduce(map_column, columns, {})

    output_dict = {}
    name_to_id_dict = {}
    for key, vals in prelim_dict.items():
        for val in vals:
            if pivot_field == "@id":
                output_dict[val] = key
                name_to_id_dict[val] = val
            else:
                new_name = _name_to_id(str(val))
                output_dict[new_name] = key
                name_to_id_dict[val] = new_name
    return output_dict, name_to_id_dict


def _is_int(*values): return all([re.match(r"^[0-9]", str(v)) is not None for v in values])


def _map_identification_values_depth_true(val, name: str, pivot_field: str, name_to_id_dict: dict, prelim_dict: dict):
    # TODO: refactor to return value instead of modifying the inputs
    val_h = val[0]
    val[0] = val[0] if pivot_field == "@id" else _name_to_id(val[0])
    name_to_id_dict[val_h] = val[0]
    val_name = f"{val[0]}.{int(val[1])}-{int(val[2])}cm" if _is_int(val[1], val[2]) \
        else f"{val[0]}.{PIVOT_FIELD_DEFAULT}"
    prelim_dict[name[0][:-2]] = prelim_dict.get(name[0][:-2], []) + [val_name]


def _map_identification_values_depth_false(val, name, pivot_field, name_to_id_dict, prelim_dict):
    # TODO: refactor to return value instead of modifying the inputs
    val_name = val if pivot_field == "@id" else _name_to_id(val)
    prelim_dict[name[0][:-2]] = prelim_dict.get(name[0][:-2], []) + [val_name]
    name_to_id_dict[val] = val_name


def _map_identification_columns(col: str, df, pivot_field: str, name_to_id_dict: dict, prelim_dict: dict):
    cols = [
        col,
        col.replace(f"term.{pivot_field}", PIVOT_FIELD_1),
        col.replace(f"term.{pivot_field}", PIVOT_FIELD_2)
    ]
    name = re.match(r"^.*\.[a-zA-Z]+\.[\d]", col)
    has_all_cols = all([c in df.columns for c in cols])
    cols = cols if has_all_cols else col
    map_function = _map_identification_values_depth_true if has_all_cols else _map_identification_values_depth_false

    list(map(lambda v: map_function(v, name, pivot_field, name_to_id_dict, prelim_dict), df[cols].values))

    return name_to_id_dict


def _identify_dict_depth(df, columns: list, pivot_field: str):
    """
    Identifies the naming of the column header the column value belongs to.
    Additionally, it also adds the depth interval values to the column value.

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe from which the names are extracted
    columns : list
        column names from which the names of values are extracted
    pivot_field : string
        name of pivot_field to determine the naming of the new fields

    Returns
    -------
    output_dict : dictionary
        primary output, dictionary with the names of the terms as keys and their abbreviated column header as key
    name_to_id_dict : dictionary
        dictionary with term name as key and new column name as value
    """
    prelim_dict = {}
    name_to_id_dict = {}

    list(map(lambda v: _map_identification_columns(v, df, pivot_field, name_to_id_dict, prelim_dict), columns))

    output_dict = {}
    for key, vals in prelim_dict.items():
        for val in vals:
            output_dict[val] = key

    return output_dict, name_to_id_dict


def _pivot_field_name(
    data, pivot_field_1: str, pivot_field_2: str, identification_dict: dict, name_to_id_dict: dict, name: str
):
    val_pivot_1 = data[pivot_field_1]
    val_pivot_2 = data[pivot_field_2]
    val_pivot_1 = str(int(val_pivot_1)) if _is_int(val_pivot_1) else str(val_pivot_1)
    val_pivot_2 = str(int(val_pivot_2)) if _is_int(val_pivot_2) else str(val_pivot_2)
    name = name_to_id_dict[data[name]] + "." + val_pivot_1 + "-" + val_pivot_2 + "cm"
    name = name if name in identification_dict else name[:name.find(".")] + "." + PIVOT_FIELD_DEFAULT
    return f"{identification_dict[name]}.{name}.value"


def _format_dict_name(
    df, pivot_field: str, data, identification_dict: dict, name_to_id_dict: dict, depth: bool, name: str
):
    pivot_field_1 = name.replace(f"term.{pivot_field}", PIVOT_FIELD_1)
    pivot_field_2 = name.replace(f"term.{pivot_field}", PIVOT_FIELD_2)
    should_pivot = all([
        pivot_field_1 in df.columns,
        pivot_field_2 in df.columns,
        depth
    ])
    return _pivot_field_name(
        data, pivot_field_1, pivot_field_2, identification_dict, name_to_id_dict, name
    ) if should_pivot else f"{identification_dict[name_to_id_dict[data[name]]]}.{name_to_id_dict[data[name]]}.value"


def _map_columns(
    df, data, pivot_field: str,
    identification_dict: dict, name_to_id_dict: dict, depth: bool
):
    def exec(group: dict, input: tuple):
        name, val = input
        dict_name = _format_dict_name(
            df,
            pivot_field,
            data,
            identification_dict,
            name_to_id_dict,
            depth,
            name
        )
        return {**group, dict_name: data[val]}
    return exec


def pivot_csv(filepath: str, exclude_columns=[], pivot_field="@id", pivot_depth=False):
    """
    Pivot the values of term.@id columns, forming new columns with values taken from the respective .value columns.

    Note that this function requires pandas, which is not included in the package requirements by default due to size.

    Parameters
    ----------
    filepath : str
        Path to the CSV to be pivoted.

    exclude_columns : list
        Which columns to exclude.

    pivot_field : str
        The name to which columns should be pivoted.
        Examples: "@id", "name"

    Returns
    -------
    pandas.DataFrame
        Pivoted pandas dataframe
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Run `pip install pandas~=1.2.0` to use this functionality")

    df = pd.read_csv(filepath, index_col=None)

    df.dropna(how='all', axis=1, inplace=True)

    term_columns_to_pivot = df.filter(regex=fr'^.*\.[a-zA-Z]+\.[\d]+\.term\.{pivot_field}$')
    term_columns_to_pivot = list(filter(lambda x: x not in exclude_columns, term_columns_to_pivot))

    if not term_columns_to_pivot:
        raise Exception(f"No columns to pivot with {pivot_field} found in the file")

    df_out = df.copy()

    # drop all columns for pivot
    term_columns_no_pivot = list(df.filter(regex=r'^.*\.[a-zA-Z]+\.[\d]').columns.values)
    df_out.drop(term_columns_no_pivot, axis=1, inplace=True)

    # identify terms to pivot + create dict
    identify_func = _identify_dict_depth if pivot_depth else _identify_dict
    identification_dict, name_to_id_dict = identify_func(df, term_columns_to_pivot, pivot_field)

    # go over rows adding terms to their appropriate column
    term_columns_to_pivot = [
        val for val in term_columns_to_pivot if val.replace("term." + pivot_field, "value") in df.columns
    ]
    term_columns_to_pivot_values = [
        val.replace("term." + pivot_field, "value") for val in term_columns_to_pivot
    ]

    dict_out = {}
    for row in df.index:
        col_dict = reduce(
            _map_columns(df, df.loc[row], pivot_field, identification_dict, name_to_id_dict, pivot_depth),
            zip(term_columns_to_pivot, term_columns_to_pivot_values),
            {}
        )
        dict_out[row] = dict(sorted(col_dict.items()))

    # merge dfs
    df_vals = pd.DataFrame.from_dict(dict_out, orient='index')
    df_vals = df_vals[sorted(df_vals.columns)]
    return_df = df_out.join(df_vals)
    return_df = _drop_col_list(return_df, [".-.", ".nan.", ".."])
    # drop empty columns
    return_df.dropna(how='all', axis=1, inplace=True)
    return return_df


def _replace_ids(df):
    # in columns, first letter is always lower case
    node_types = [e.value[0].lower() + e.value[1:] for e in NodeType]
    # add extra subvalues
    subvalues = ['source', 'defaultSource', 'site', 'organisation', 'cycle']
    node_types = node_types + flatten([v + '.' + value for v in node_types] for value in subvalues)
    columns = reduce(lambda prev, curr: {**prev, curr + '.@id': curr + '.id'}, node_types, {})
    return df.rename(columns=columns)


def _clean_term_columns(df):
    columns = ['name', 'termType', 'units']
    cols = [c for c in df.columns if all([not c.endswith('.' + v) for v in columns])]
    return df[cols]


def _replace_nan_values(df, col: str, columns: list):
    for index, row in df.iterrows():
        try:
            value = row[col]
            if np.isnan(value):
                for empty_col in columns:
                    df.loc[index, empty_col] = np.nan
        except TypeError:
            continue
    return df


def _empty_impact_na_values(df):
    impacts_columns = [c for c in df.columns if '.impacts.']
    impacts_values_columns = [c for c in impacts_columns if c.endswith('.value')]
    for col in impacts_values_columns:
        col_prefix = col.replace('.value', '')
        same_col = [c for c in impacts_columns if c.startswith(col_prefix) and c != col]
        _replace_nan_values(df, col, same_col)
    return df


def format_for_upload(filepath: str):
    """
    Format downloaded file for upload on Hestia platform.
    Will replace all instances of `@id` to `id`, and drop the columns ending by `name`, `termType` or `units`.

    Parameters
    ----------
    filepath : str
        Path to the CSV to be formatted.

    Returns
    -------
    pandas.DataFrame
        Formatted pandas dataframe
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Run `pip install pandas~=1.2.0` to use this functionality")

    df = pd.read_csv(filepath, index_col=None, na_values='')

    # replace @id with id for top-level Node
    df = _replace_ids(df)

    # drop all term columns that are not needed
    df = _clean_term_columns(df)

    # empty values for impacts which value are empty
    df = _empty_impact_na_values(df)

    return df
