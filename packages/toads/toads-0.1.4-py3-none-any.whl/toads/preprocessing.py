import numpy as np
import pandas as pd


def categorize_dict(text, cat_dict):
    """Присваивает категории в соответствии со словарём, если в тексте содержится ключ."""
    for key, value in cat_dict.items():
        if key in text:
            return value
    return text


def fill_from(row, by, what, source):
    """Возвращает значение из таблицы-источника.
    row - строка
    by - по какому признаку искать
    what - столбец, который заполняем
    source - таблица-источник
    """
    try:
        return source.at[row[by], what]
    # Если индекса нет
    except KeyError:
        return row[what]


def ci_strip(data, ci=0.95, subset: 'list[str]' = None):
    """Strips dataframe, leaving values inside of confidence interval.

    data: {pd.DataFrame, array-like}
    subset: [str] = columns to consider while removing out-of-CI values."""

    # Set quantiles
    lower = (1 - ci) / 2
    upper = 1 - lower

    def ci_index(array):
        """Return bool array with values inside CI"""
        return (np.quantile(array, lower) <= array) & (array <= np.quantile(array, upper))

    if isinstance(data, pd.DataFrame):
        # All rows in subset must be in CI to stay
        normal_index = np.all(                                     # Only all-True will remain True
            [ci_index(data[column])                                # Get in-CI indexes
             for column in (subset if subset else data.columns)],  # From each column
            axis=0
        )
        return data[normal_index]
    else:
        return data[ci_index(data)]


__all__ = ['ci_strip', 'fill_from', 'agg_fill_by_cat']
