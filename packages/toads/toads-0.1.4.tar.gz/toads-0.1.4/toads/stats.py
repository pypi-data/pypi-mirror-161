from scipy.stats import mannwhitneyu

from .image import Img
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def hypo(test, alpha=0.05, oneside=False, verbose=True):
    """Сравнивает p-value с уровнем значимости. Проверяет гипотезу.

    alpha: уровень значимости

    oneside: делит p-value пополам

    verbose: печатает либо возвращает bool
    """
    if isinstance(test, tuple):
        pv = test[1]
    else:
        pv = test.pvalue if not oneside else test.pvalue / 2
    result = pv > alpha
    if verbose:
        print('p-value =', pv)
        print('p-value',
              '>' if result else '<',
              alpha
              )
    else:
        return result


def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    return pd.Series(np.arange(1, data.shape[0] + 1) / data.shape[0],
                     index=np.sort(data))


def dist_compare(true, preds, hypothesis=True, image='dist', **img_kws):
    """Рисует распределения ответов модели и реальных значений целевого признака.
    Проверяет сходство выборок критерием Манна-Уитни."""
    if image:
        with Img(legend='a' if image == 'dist' else None, **img_kws):
            if image == 'dist':
                sns.distplot(true, label='true')
                sns.distplot(preds, label='preds')
            if image == 'box':
                sns.boxplot(data=[true, preds], orient='h')
                plt.yticks([0, 1], ['true', 'preds'])
    if hypothesis:
        hypo(mannwhitneyu(true, preds))


__all__ = ['dist_compare', 'ecdf', 'hypo']
