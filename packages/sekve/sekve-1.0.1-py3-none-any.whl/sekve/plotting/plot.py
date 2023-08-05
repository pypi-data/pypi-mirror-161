from matplotlib import pyplot as plt
from cycler import cycler


PLOT_STYLE = {
    "figure.figsize": [3, 2],
    'figure.autolayout': True,
    'figure.constrained_layout.use': False,
    "figure.dpi": 200,
    'figure.facecolor': 'white',
    'savefig.dpi': 1200,
    'lines.markersize': 3,
    "lines.marker": '',
    "lines.markerfacecolor": "none",
    "lines.linestyle": "-",
    "lines.linewidth": 1,
    "lines.color": "k",
    'axes.labelsize': 10,
    'axes.linewidth': 1,
    'axes.autolimit_mode': "round_numbers",
    'axes.xmargin': 0.,
    'axes.ymargin': .0,
    'axes.formatter.limits': (-3, 3),
    'axes.prop_cycle': cycler(markevery=[0.05], color=['k']),
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'xtick.direction': "in",
    'ytick.direction': "in",
    'font.size': 8,
    'font.family': 'Arial',
    'legend.fontsize': 8,
    'legend.frameon': False,
    'svg.fonttype': 'none',
    'pdf.fonttype': 42,
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic',
    'mathtext.bf': 'Arial:bold',
    "grid.color": 'gray',
    "grid.linestyle": '-',
    "grid.linewidth": 0.25,
    "grid.alpha": 1.,
    "legend.framealpha": 1.0,
    "legend.edgecolor": "inherit"
}


def update_rcParams():
    """Update the Matplotlib style."""
    plt.rcParams.update(PLOT_STYLE)
