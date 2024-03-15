from dash import Dash, html, dcc
import dash

app = Dash(__name__, use_pages=True, prevent_initial_callbacks=True)

app.layout = html.Div([
    html.H1('PLANT DASHBOARD FOR VARIOUS PARAMETERS MONITERING',
            style={'textAlign': 'center', 'color': 'blue'}),
    html.P('Click any of the link to visit the page'),
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

    dash.page_container
])

if __name__ == '__main__':
    app.run_server()
