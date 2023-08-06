import factory_component
from dash import Dash, html, Input, Output

app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        id='div-position'
    ),
    html.Div(
        id='div-size'
    ),
    factory_component.Rnd(
        default={
            'x':0,
            'y':0,
            'width':200,
            'height':200,
        },
        style={
            'background':'red',
        },
        id='teste'
    )
])

@app.callback(
    Output('div-position','children'),
    Input('teste','position'),
)
def update_position(position):
    print(position)
    return str(position)

@app.callback(
    Output('div-size','children'),
    Input('teste','size'),
)
def update_position(size):
    print(size)
    return str(size)

if __name__ == '__main__':
    app.run_server(debug=True)
