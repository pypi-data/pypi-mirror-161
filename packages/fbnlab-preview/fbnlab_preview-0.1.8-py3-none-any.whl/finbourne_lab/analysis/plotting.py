import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .linear import ScalingModel


def superimposed_difference(baseline: ScalingModel, *models: ScalingModel, **kwargs):
    """Produce a plot that shows the difference between a series of linear scaling models and a baseline model.

    Args:
        baseline (ScalingModel): the baseline model to subtract from the others.
        *models (ScalingModel): the other models.

    Keyword Args:
        figsize: the figure size tuple to pass to matplotlib (default = (14, 10))
        xlim: the x axis range to use in the plot (defaults to matplotlib default)
        xlabel: the x axis label to use in the plot (defaults to whatever the x column is in the baseline model)
        ylabel: the y axis label to use in the plot (defaults to whatever the y column is in the baseline model)
        title: title to put at the top of the plot (defaults to none)
        show_datapoints (bool): show the observed datapoints. Set to false if a comparison plot's getting too busy.
        ratio_plot (bool): whether to plot the ratio on the lower plot or the difference (defaults to False)

    Returns:
        Tuple: the figure, axes, and the delta models.

    """

    figsize = kwargs.get('figsize', (14, 10))
    xlim = kwargs.get('xlim', (None, None))
    xlabel = kwargs.get('xlabel', baseline.x)
    ylabel = kwargs.get('ylabel', baseline.y)
    title = kwargs.get('title', '')
    show_datapoints = kwargs.get('show_datapoints', True)
    ratio_plot = kwargs.get('ratio_plot', False)

    cmap_name = kwargs.get('cmap', 'plasma')
    cmap = matplotlib.cm.get_cmap(cmap_name)

    f, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

    baseline.add_plot(ax1, color_scheme='grey', show_datapoints=show_datapoints)

    deltas = []
    for i, model in enumerate(models):
        v = (i+0.5)/len(models)
        model.add_plot(ax1, color_scheme=cmap(v), show_datapoints=show_datapoints)
        if ratio_plot:
            deltas.append((model - baseline) / baseline)
        else:
            deltas.append(model - baseline)

    for i, delta in enumerate(deltas):
        v = (i+0.5)/len(models)
        delta.add_plot(ax2, color_scheme=cmap(v), show_datapoints=show_datapoints)
    ax2.axhline(0.0, color='black', ls='-', lw=2)

    ax1.legend(bbox_to_anchor=(1, 1))
    ax1.grid(True, ls=':', zorder=-99)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)

    ax2.legend(bbox_to_anchor=(1, 1))
    ax2.grid(True, ls=':', zorder=-99)
    ax2.set_xlim(*xlim)
    ax2.set_xlabel(xlabel)
    ax2.set_ylabel('Delta\n' + ylabel)

    plt.subplots_adjust(hspace=0.03)
    return f, (ax1, ax2), deltas


def pointwise_difference(*models, **kwargs):
    """Create a pointwise difference box and whiskers plot for a set of models. Plot shows the difference between the
    predictions of the first model and the rest evaluated at a given point or a set of points.

    Args:
        *models: the set of models to analyse.

    Keyword Args:
        x_pred: the value or values to evaluate the models at.
        figsize: the figure size tuple to pass to matplotlib. If not specified it will be computed from the number
        of models.
        x_label: the x axis label to use in the plot (defaults to whatever the x column is in the first model)
        title: title to put at the top of the plot (defaults to none)
        ratio_plot (bool): whether to plot the ratio or the difference (defaults to False)
        color (str): the color to use (defaults to red)

    Returns:
        Tuple: figure, axis, and dataframe of the model predictions.

    """

    title = kwargs.get('title', None)

    x_label = kwargs.get('x_label', models[0].x)
    x_units = kwargs.get('x_units', None)
    x_pred = kwargs.get('x_pred')
    ratio_plot = kwargs.get('ratio_plot', False)
    color = kwargs.get('color', 'red')
    figsize = kwargs.get('figsize', None)

    n_models = len(models)
    n_pred = len(x_pred) if hasattr(x_pred, '__len__') else 1
    n_pred_points = n_pred * n_models

    baseline_pred = models[0].predict(x_pred)

    if ratio_plot:
        base_median = baseline_pred[0.5].values
        shift = base_median
        scale = base_median*0.01

    else:
        shift = np.zeros(n_pred)
        scale = np.ones_like(n_pred)

    res_dfs = []

    def _add_points(ix):

        preds = models[ix].predict(x_pred)
        preds['name'] = models[ix].name
        res_dfs.append(preds)

        p005 = ((preds[0.05] - shift) / scale).values
        p025 = ((preds[0.25] - shift) / scale).values
        p050 = ((preds[0.5] - shift) / scale).values
        p075 = ((preds[0.75] - shift) / scale).values
        p095 = ((preds[0.95] - shift) / scale).values

        xerr = abs(np.hstack([p005.reshape(-1, 1), p095.reshape(-1, 1)]) - p050.reshape(-1, 1)).T

        _y = np.arange(n_pred) * n_models + ix

        plt.barh(_y, width=p075 - p025, left=p025, color=color, alpha=0.5, height=0.5, label='50% Range' if ix == 0 else None)
        plt.errorbar(p050, _y, xerr=xerr, color='black', ls='none', label='90% Range' if ix == 0 else None)
        plt.scatter(p050, _y, color='black', marker='.', label='Median' if ix == 0 else None)

    y = np.arange(n_pred_points)

    # The plotting
    figsize = (7, 0.667 * len(y)) if figsize is None else figsize
    f, ax = plt.subplots(figsize=figsize)

    for i in range(n_models):
        _add_points(i)

    y_labels = [models[i % n_models].name for i in y]
    plt.yticks(y, y_labels)

    axb = ax.twinx()
    axb.set_yticks(np.arange(n_pred) * n_models + n_models / 2 - 0.5)
    axb.set_ylim(-1, len(y))
    axb.set_yticklabels(map(lambda x: f'x = {x}', baseline_pred.reset_index().x.tolist()))

    for break_line in range(1, n_pred_points):
        ax.axhline(break_line * n_models - 0.5, color='black', ls=':')

    ax.grid(True, ls=':', zorder=-99)
    ax.set_ylim(-0.5, len(y) - 0.5)

    if ratio_plot:
        ax.axvline(0.0, color='black', ls='--')
        ax.set_xlabel(f'{x_label}\n% Difference')
    else:
        unit_str = '' if x_units is None else f' ({x_units})'
        ax.set_xlabel(f'{x_label}' + unit_str)

    if title is not None:
        ax.set_title(title)

    ax.legend()

    return f, ax, pd.concat(res_dfs)
