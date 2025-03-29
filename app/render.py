import gradio as gr
import plotly.graph_objects as go

from app.core.constants import PLOT_TITLE
from app.core.models import GCode
from app.core.models.config import *
from app.core.state import UserGCodeSettingsSession


def render_config_field(config_field: BaseConfigValue, state):
    rendered_field = None
    params = dict(
        interactive=True,
        key=config_field.name,
        label=config_field.config_label,
        info=config_field.description,
        value=config_field.initial_value)
    if isinstance(config_field, NumericConfigValue):
        params.update(
            dict(minimum=config_field.min_value, maximum=config_field.max_value, step=config_field.step)
        )
        rendered_field = gr.Number(**params) if config_field.max_value > 150 else gr.Slider(**params)
    elif isinstance(config_field, BooleanConfigValue):
        rendered_field = gr.Checkbox(**params)
    elif isinstance(config_field, CategoricalConfigValue):
        params.update(dict(choices=config_field.choices))
        rendered_field = gr.Dropdown(**params) if len(config_field.choices) > 5 else gr.Radio(**params)
    else:
        raise ValueError(f"Config field type {type(config_field)} is not supported")

    def update_state(value, state_obj: UserGCodeSettingsSession):
        state_obj.update_state(config_field.name, value)
        return state_obj

    rendered_field.change(fn=update_state, inputs=[rendered_field, state], outputs=state)


def get_plot_object_from_gcode(gcode_path: List[GCode]):
    x, y, z = [], [], []
    for i in gcode_path:
        (x_i, y_i, z_i) = i.coordinate()
        x.append(x_i)
        y.append(y_i)
        z.append(z_i)
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z, marker=dict(size=1, color="black", colorscale='Viridis', ), line=dict(color='green', width=3)
    )])
    fig.update_layout(title=PLOT_TITLE, autosize=True, margin=dict(l=65, r=50, b=20, t=20))
    return fig
