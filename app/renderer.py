from app.core.models.config import *
import gradio as gr


def render_config_field(config_field: BaseConfigValue, state):
    rendered_field = None
    params = dict(
        interactive=True,
        key=config_field.name,
        label=config_field.config_label,
        info=config_field.description,
        value=config_field.initial_value)
    if isinstance(config_field, NumericConfig):
        params.update(
            dict(minimum=config_field.min_value, maximum=config_field.max_value, step=config_field.step)
        )
        rendered_field = gr.Number(**params) if config_field.max_value > 150 else gr.Slider(**params)
    elif isinstance(config_field, BooleanConfig):
        rendered_field = gr.Checkbox(**params)
    elif isinstance(config_field, CategoricalConfig):
        params.update(dict(choices=config_field.choices))
        rendered_field = gr.Dropdown(**params) if len(config_field.choices) > 5 else gr.Radio(**params)
    else:
        raise ValueError(f"Config field type {type(config_field)} is not supported")

    def update_state(value, state_obj):
        state_obj[config_field.name] = value
        return state_obj
    rendered_field.change(fn=update_state, inputs=[rendered_field, state], outputs=state)
    return config_field, rendered_field

#
#
# class PlotRenderer(ResultRenderer):
#     default_text = "plot shown here.."
#
#     def render(self, generator: CoordinateGenerator):
#         self.container.plotly_chart(generator.get_plot_figure(), True)
#
#
# class GCODETextRenderer(ResultRenderer):
#     default_text = "GCODE text shown here.."
#
#     def render(self, generator: CoordinateGenerator):
#         self.container.download_button("Download GCODE", generator.gcode(as_bytes=True), file_name=".gcode")
