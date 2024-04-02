import numpy as np
import plotly.graph_objects as go


def normalize_kpath(kpath):
    kpath = np.array(kpath)
    min_val = kpath.min()
    max_val = kpath.max()
    return (kpath - min_val) / (max_val - min_val)


def plain_bandplot(
    fig: go.Figure, kpath, bands, color, label=None, yrange=[-4, 4], **kwargs
):
    num_bands = bands.shape[1]

    for idx in range(num_bands):
        fig.add_trace(
            go.Scatter(
                x=kpath,
                y=bands[:, idx],
                mode="lines",
                # name=f"Trace{idx}",
                customdata=[f"{idx+1}"] * len(kpath),
                hovertemplate="band-index: %{customdata}<br>energy: %{y:.3f} eV<extra></extra>",
                line=dict(color=color, width=2),
                legendgroup=label,
                name=label,
                showlegend=(True if idx == 0 else False),
                **kwargs,
            )
        )

    return fig


def proj_bandplot(
    fig: go.Figure,
    kpath,
    bands,
    weights,
    normalize=False,
    cmap="jet",
    label=None,
    **kwargs,
):

    if normalize:
        weights = (weights - weights.min()) / (weights.max() - weights.min())
    for idx in range(weights.shape[-1]):
        fig.add_trace(
            go.Scatter(
                x=kpath,
                y=bands[:, idx],
                mode="markers",
                marker=dict(
                    size=5,
                    color=weights[:, idx],
                    colorscale=cmap,
                    colorbar_thickness=25,
                    cmin=weights.min(),
                    cmax=weights.max(),
                ),
                customdata=[f"{idx+1}"] * len(kpath),
                hovertemplate="band-index: %{customdata}<br>energy: %{y:.3f} eV<extra></extra>",
                legendgroup=label,
                name=label,
                showlegend=(True if idx == 0 else False),
                **kwargs,
            )
        )
    fig.update_layout(
        coloraxis_colorbar=dict(title="weight", len=0.5, y=0.5),
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig


def make_symm_lines(fig, ticks: dict, color, width=1, use_dash=True, style="dash"):
    for tick, label in zip(ticks["ticks"], ticks["ticklabels"]):
        fig.add_vline(
            x=tick,
            line_width=width,
            line_color=color,
            line_dash=style if use_dash else None,
        )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=ticks["ticks"],
            ticktext=ticks["ticklabels"],
        )
    )
