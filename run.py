import gradio as gr
import tempfile

from app.core.models import GcodeSettings
from app.generate_code import ASTM638TestSampleGCodeGenerator
from app.render import render_config_field, get_plot_object_from_gcode
from app.sessionStore import UserGCodeSettingsSession

settings = GcodeSettings.from_json_file("./config.json")


def generate_gcode(state: UserGCodeSettingsSession):
    print(state.settings)
    gcode_generator = ASTM638TestSampleGCodeGenerator(settings=state.settings)
    plot_fig = get_plot_object_from_gcode(gcode_generator.path())
    gcode_file_str = gcode_generator.gcode_file()
    gcode_save_path = state.generate_path_for_gcode_file()

    with open(gcode_save_path, 'w') as file_io:
        file_io.write(gcode_file_str)

    return plot_fig, gr.DownloadButton(value=gcode_save_path, label="Download GCODE File", visible=True, interactive=True)


with gr.Blocks() as demo:
    gr.HTML("""<h1 style="text-align: center;">ASTM D638 Test Sample GCode Generator</h1>""")
    settings_fields = []
    session_store = gr.State(
        value=UserGCodeSettingsSession(settings.default_values()),
        delete_callback=lambda state: state.close()
    )
    with gr.Row():
        with gr.Column(scale=1):
            for section in settings.sections:
                with gr.Tab(section.section_name):
                    for field in section.fields:
                        settings_fields.append(render_config_field(config_field=field, state=session_store)[1])
            generate_button = gr.Button("Generate GCODE")

        with gr.Column(scale=2):
            plot_obj = gr.Plot(label="forecast", format="png")
            download_button = gr.DownloadButton(visible=False, interactive=False)

    generate_button.click(generate_gcode, session_store, [plot_obj, download_button])

#  TODO Do loading settings from browser memory.
#  TODO Fix issue with refreshing settings on browser
# Implement downloading of data
demo.launch()
