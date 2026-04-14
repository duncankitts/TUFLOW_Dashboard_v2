

def finalise_dashboard(fig, title):
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, x=0.5),
        title_font_size=22,
        height=950,
        margin=dict(l=40, r=25, t=80, b=80),
        legend=dict(
            orientation="h",     # horizontal legend
            x=0.5,               # centered
            xanchor="center",
            y=-0.2,              # below the plot area
            yanchor="top")
    )
    return fig

    if logo:
        fig.add_layout_image(
            dict(
                source=app.get_asset_url("Logo.jpg"),
                xref="paper",
                yref="paper",
                x=1,
                y=1.0,
                sizex=0.18,
                sizey=0.18,
                xanchor="right",
                yanchor="bottom",
            )
        )

    return fig