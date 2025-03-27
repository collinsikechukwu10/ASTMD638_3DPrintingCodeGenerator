import gradio as gr

from app.core.models import GcodeSettings
from app.generate_code import ASTM638TestSampleGCodeGenerator
from app.render import render_config_field, get_plot_object_from_gcode

settings = GcodeSettings.from_json_file("./config.json")


def generate_gcode(state):
    print(state)
    gcode_generator = ASTM638TestSampleGCodeGenerator(app_config=state)
    plot_fig = get_plot_object_from_gcode(gcode_generator.path())
    gcode_file_bytes = gcode_generator.gcode_file(as_bytes=True)
    return plot_fig #, gcode_file_bytes


with gr.Blocks() as demo:
    gr.Markdown("ASTM638 Test Sample GCode Generator")
    settings_fields = []
    state = gr.BrowserState(settings.default_values())
    with gr.Row():
        with gr.Column(scale=2):
            for section in settings.sections:
                with gr.Tab(section.section_name):
                    for field in section.fields:
                        settings_fields.append(render_config_field(config_field=field, state=state)[1])
            generate_button = gr.Button("Generate GCODE")

        with gr.Column(scale=2):
            plot_obj = gr.Plot(label="forecast", format="png")
            download_button = gr.DownloadButton(label="Download GCODE", value=None, interactive=False)

    generate_button.click(generate_gcode, state, [plot_obj]) #, download_button])

#  TODO Do loading settings from browser memory.
#  TODO Fix issue with refreshing settings on browser

