import matplotlib.pyplot as plt

def subplots(rows, cols, plot_size=(6.4,4.8), keep_shape=False, **kwargs):
    fig, axes = plt.subplots(rows, cols, figsize=(plot_size[0]*cols, plot_size[1]*rows), **kwargs)
    if keep_shape:
        axes = axes.reshape((rows, cols))
    return fig, axes

def scaterr(x, y, yerr, ax=None, cap=False, **kwargs):
    if 'marker' not in kwargs:
        kwargs['marker'] = '.'
    if 'ls' not in kwargs and 'linestyle' not in kwargs:
        kwargs['ls'] = 'none'
    if 'capsize' not in kwargs and cap:
        kwargs['capsize'] = 2.0
    
    if ax is None:
        ax = plt.gca()
    
    return ax.errorbar(x.tolist(), y.tolist(), yerr=yerr.tolist(), **kwargs)

def hide_unused_axes(axes):
    for ax in axes.flat:
        if not ax.has_data():
            ax.set_axis_off()