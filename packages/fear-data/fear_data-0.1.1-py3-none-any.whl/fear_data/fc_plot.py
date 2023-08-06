"""Script used to visualize our fear conditioning data."""
import matplotlib.pyplot as plt
import seaborn as sns
from .fc_plot_utils import savefig, style_plot, _make_ax
from .fc_data import get_phase_data


@savefig
@style_plot
def plot_fc_bins(
    df,
    session,
    xvar="Component",
    yvar="PctFreeze",
    ax=None,
    fig_size=(16, 10),
    **kwargs
):
    """
    Create a pointplot of VideoFreeze Components.
    Use the session arg to modify what is drawn on the plots:
    - 'train': adds rectangles over each tone bin and adds vline to indicate shock.
    - 'tone': adds rectangle over each tone bin in session.
    - 'context': does not add any additional plot aesthetics

    Args:
        df (DataFrame): DataFrame to plot.
        session (str): Name of session.
            Used for plot aesthetics. Must be in ['train', 'tone', 'context']
        xvar (str, optional): Specify x-axis variable. Defaults to "Component".
        yvar (str, optional): Specify dependent variable. Defaults to "PctFreeze".
        ax (matplotlib.Axes, optional): Axes to plot on (calls `_make_ax`). Defaults to None.
        fig_size (tuple, optional): Size of figure object. Defaults to (16, 10).

    Notes:
        There are optional keyword args for saving the figure:
            save_fig (bool, optional): Speicfy whether to save figure object. Defaults to False.
            fig_name (str, optional): Name of figure file. Defaults to 'timestamp-NewFig'
            fig_path (str, path object): Path to save figure. Defaults to '~/Desktop'.

    """

    assert session.lower() in [
        "train",
        "tone",
        "context",
    ], "Session must be in ['train', 'tone', 'context']"
    ax = _make_ax(ax, figsize=fig_size)
    bins_list = list(df["Component"].unique())  # get bins for tone and trace interval
    # draw grey rectangle around tone bin
    if session.lower() != "context":
        tone_list = [
            i - 0.5 for i in range(len(bins_list)) if "tone-" in bins_list[i].lower()
        ]
        for tone in tone_list:
            ax.axvspan(tone, tone + 1, facecolor="grey", alpha=0.15)
    # draw line to indicate shock
    if session.lower() == "train":
        trace_list = [
            i - 0.5 for i in range(len(bins_list)) if "trace-" in bins_list[i].lower()
        ]
        for trace in trace_list:
            ax.axvspan(trace + 1, trace + 1.15, facecolor="#ffb200")

    sns.pointplot(
        x=xvar,
        y=yvar,
        data=df,
        ci=68,
        ax=ax,
        scale=2.25,
        errwidth=6,
        capsize=0.05,
        **kwargs
    )

    if session.lower() == "context":
        plt.setp(ax.collections, sizes=[1000])
    ax.set_ylabel("Freezing (%)")
    ax.set_xlabel("Time (mins)")
    # replace with x-labels with mins if using Component
    if session != "context":
        min_bins = [i for i in range(len(df["Component"].unique())) if (i + 1) % 3 == 0]
        min_labs = [i + 1 for i in range(len(min_bins))]
        ax.set_xticks(min_bins)
        ax.set_xticklabels(min_labs)
    # if "hue" in kwargs.keys():
    #     leg = ax.legend()
    #     leg.set_title(None)
    sns.despine()


@savefig
@style_plot
def plot_fc_phase(
    df,
    kind="point",
    xvar="Phase",
    yvar="PctFreeze",
    pts=True,
    ax=None,
    fig_size=(16, 9),
    **kwargs
):
    """
    Create a pointplot of VideoFreeze Components.
    Use the `kind` arg to specify the plot type:
    - 'point': Creates a pointplot of the data.
    - 'bar': Creates a barplot of the data.

    Args:
        df (DataFrame): DataFrame to plot.
        kind (str): Style of plot to generate. Must be 'point' or 'bar'.
        xvar (str, optional): Specify x-axis variable. Defaults to "Component".
        yvar (str, optional): Specify dependent variable. Defaults to "PctFreeze".
        pts (bool, optional): Add individual data points to bar style plot.
        ax (matplotlib.Axes, optional): Axes to plot on (calls `_make_ax`). Defaults to None.
        fig_size (tuple, optional): Size of figure object. Defaults to (16, 10).

    Notes:
        There are optional keyword args for saving the figure:
            save_fig (bool, optional): Speicfy whether to save figure object. Defaults to False.
            fig_name (str, optional): Name of figure file. Defaults to 'timestamp-NewFig'
            fig_path (str, path object): Path to save figure. Defaults to '~/Desktop'.

    """

    assert kind in ["point", "bar"], "`kind` arg must be 'point' or 'bar'"

    df = get_phase_data(df, hue=kwargs.get("hue") if "hue" in kwargs.keys() else None)
    ax = _make_ax(ax, figsize=fig_size)  # create figure
    if kind == "point":
        kwargs["scale"] = 4
        pts = False
    else:
        kwargs["edgecolor"] = "black"
        kwargs["linewidth"] = 4
    if "tone" not in df.Phase.unique():
        plt.tick_params(labelbottom=False)
    # Determine the plotting function
    if "title" in kwargs:
        kwargs.pop("title")
    plot_func = getattr(sns, kind + "plot")
    plot_func(x=xvar, y=yvar, data=df, ax=ax, ci=68, errwidth=8, capsize=0.05, **kwargs)
    plt.setp(ax.collections, sizes=[1000])
    if pts:
        hue = kwargs.pop("hue") if "hue" in kwargs.keys() else None
        hue_order = kwargs["order"] if "order" in kwargs.keys() else None
        sns.stripplot(
            x=xvar,
            y=yvar,
            data=df,
            hue=hue,
            order=hue_order,
            color="black",
            alpha=0.7,
            dodge=True,
            size=18,
            ax=ax,
            linewidth=0,
        )
    ax.set_ylabel("Freezing (%)")
    ax.set_xlabel("")
    # replace with x-labels with mins if using Component
    if xvar == "Component":
        min_bins = [i for i in range(len(df["Component"].unique())) if (i + 1) % 3 == 0]
        min_labs = [i + 1 for i in range(len(min_bins))]
        ax.set_xticks(min_bins)
        ax.set_xticklabels(min_labs)
    if "hue" in kwargs.keys():
        leg = ax.legend()
        leg.set_title(None)
    sns.despine()


@savefig
@style_plot
def context_barplot(
    df, xvar="Group", yvar="PctFreeze", pts=True, ax=None, fig_size=(8, 8), **kwargs
):

    df_context = df.groupby(["Animal", "Group"]).mean().reset_index()
    ax = _make_ax(ax, figsize=fig_size)  # create figure
    # plot aesthetics
    kwargs["edgecolor"] = "black"
    kwargs["linewidth"] = 4
    sns.despine()

    if pts:
        sns.stripplot(
            x=xvar,
            y=yvar,
            data=df_context,
            color="black",
            alpha=0.7,
            dodge=False,
            size=18,
            ax=ax,
            linewidth=0,
        )
    sns.barplot(
        x="Group",
        y="PctFreeze",
        data=df_context,
        ci=68,
        ax=ax,
        dodge=False,
        errwidth=8,
        capsize=0.1,
        **kwargs
    )
    # adjust axis labels
    ax.set_ylabel("Freezing (%)")
    ax.set_xlabel("")
