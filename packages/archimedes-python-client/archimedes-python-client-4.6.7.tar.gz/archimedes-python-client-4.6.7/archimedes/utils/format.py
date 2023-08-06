from pprint import pprint

import pandas as pd

_letters = list("abcdefghijklmnopqrstuvw")
_lst = list("abcdefghijklmnopqrstuvw")

for letter1 in _letters:
    for letter2 in _letters:
        _lst.append(letter1 + letter2)

for letter1 in _letters[0:8]:
    for letter2 in _letters:
        for letter3 in _letters:
            _lst.append(letter1 + letter2 + letter3)


REPLACEMENT_NAMES = _lst


def full_print(df: pd.DataFrame) -> None:
    """Prints the full DataFrame

    Example:
        >>> df = archimedes.load_data("fmri")
        >>> arhcimedes.full_print(df)
            subject  timepoint event    region    signal
        0        s13         18  stim  parietal -0.017552
        1         s5         14  stim  parietal -0.080883
        2        s12         18  stim  parietal -0.081033
        3        s11         18  stim  parietal -0.046134
        4        s10         18  stim  parietal -0.037970
        5         s9         18  stim  parietal -0.103513
        6         s8         18  stim  parietal -0.064408
        7         s7         18  stim  parietal -0.060526
        ...

    Args:
        df (pd.DataFrame): The dataframe that you want to print
    """
    pd.set_option("display.max_rows", None)
    print(df)
    # print(df.tail(1))
    pd.set_option("display.max_rows", 10)


def compact_print(
    df: pd.DataFrame, show_mapping: bool = False, all_rows: bool = False
) -> None:
    """Prints a compact version of the DataFrame

    Example:
        >>> df = archimedes.load_data("fmri")
        >>> arhcimedes.compact_print(df, True, False)
                a   b     c         d         e
        0     s13  18  stim  parietal -0.017552
        1      s5  14  stim  parietal -0.080883
        ...   ...  ..   ...       ...       ...
        1062  s11   7   cue   frontal -0.025367
        1063   s0   0   cue  parietal -0.006899
        ...
        [1064 rows x 5 columns]
        This is a compact version of the dataframe, with columns:
        {'a': 'subject', 'b': 'timepoint', 'c': 'event', 'd': 'region', 'e': 'signal'}

    Args:
        df (pd.DataFrame): The dataframe that you want to print
        show_mapping (bool, optional):
            Set to True to print the column name mapping.
            Defaults to False.
        all_rows (bool, optional):
            Set to True if you want to print all rows.
            Defaults to False.
    """
    df_ = df.copy()
    num_columns = len(df_.columns)
    actual_columns = df_.columns
    compact_columns = REPLACEMENT_NAMES[0:num_columns]
    mapping = dict(zip(compact_columns, actual_columns))
    df_.columns = compact_columns
    if all_rows:
        pd.set_option("display.max_rows", None)
        print(df_)
        pd.set_option("display.max_rows", 10)
    else:
        print(df_)
    if show_mapping:
        print("This is a compact version of the dataframe, with columns:")
        pprint(mapping)
