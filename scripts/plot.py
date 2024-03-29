import plotly.graph_objects as go


def plain_bandplot(fig: go.Figure, kpath, bands, **kwargs):
    num_bands = bands.shape[1]
    # yrange = kwargs.get("yrange", [-4, 4])
    color = kwargs.get("color", "blue")
    label = kwargs.get("name", None)
    # lineplot_layout = dict(
    #    yaxis=dict(range=yrange, showgrid=False),
    #    xaxis=dict(showgrid=False),
    #    #width=800,
    #    height=600,
    # )

    for idx in range(1, num_bands + 1):
        fig.add_trace(
            go.Scatter(
                x=kpath,
                y=bands[idx],
                mode="lines",
                # name=f"Trace{idx}",
                customdata=[f"{idx}"] * len(kpath),
                hovertemplate="band-index: %{customdata}<br>energy: %{y:.3f} eV<extra></extra>",
                line=dict(color=color, width=2),
                name=label,
                showlegend=(True if idx == 1 else False),
            )
        )
    # fig.update_layout(lineplot_layout)
    # fig.update_traces(hovertemplate="band-index: %{customdata}<br> energy: %{y} eV")

    return fig


def proj_bandplot(fig: go.Figure, kpath, bands, weights, **kwargs):
    xrange = (kpath.min(), kpath.max())
    yrange = kwargs.get("yrange", [-4, 4])
    cmap = kwargs.get("cmap", "jet")
    label = kwargs.get("name", None)
    scatter_layout = dict(
        yaxis=dict(range=yrange, showgrid=False),
        xaxis=dict(range=xrange, showgrid=False),
        width=800,
        height=600,
    )

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
                name=label,
                showlegend=(True if idx == 1 else False),
            )
        )
    fig.update_layout(scatter_layout)

    return fig
