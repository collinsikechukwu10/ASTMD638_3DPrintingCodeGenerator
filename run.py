import gradio as gr

from app.core.models import GcodeSettings
from app.generate_code import ASTM638TestSampleGCodeGenerator
from app.render import render_config_field, get_plot_object_from_gcode
from app.core.state import UserGCodeSettingsSession

settings = GcodeSettings.from_json_file("gcode_settings.json")


def generate_gcode(state: UserGCodeSettingsSession):
    print(state.settings)
    gcode_generator = ASTM638TestSampleGCodeGenerator(settings=state.settings)
    plot_fig = get_plot_object_from_gcode(gcode_generator.gcode_traversal())
    gcode_file_str = gcode_generator.gcode_file()
    gcode_path = state.generate_path_for_gcode_file()

    with open(gcode_path, 'w') as file_io:
        file_io.write(gcode_file_str)

    return plot_fig, gr.DownloadButton(value=gcode_path, label="Download GCODE File", visible=True, interactive=True)


with gr.Blocks(delete_cache=(43200, 86400)) as demo:
    gr.HTML("""<h1 style="text-align: center;">ASTM D638 Test Sample GCode Generator</h1>""")
    session_store = gr.State(
        value=UserGCodeSettingsSession(settings.default_values()),
        time_to_live=86400,
        delete_callback=lambda state: state.close()
    )
    with gr.Row():
        with gr.Column(scale=1):
            for section in settings.sections:
                with gr.Tab(section.section_name):
                    for field in section.fields:
                        render_config_field(config_field=field, state=session_store)
            generate_button = gr.Button("Generate GCODE")

        with gr.Column(scale=2):
            plot_obj = gr.Plot(label="3D ASTM D638 Sample Plot", format="png")
            download_button = gr.DownloadButton(visible=False, interactive=False)
    generate_button.click(generate_gcode, session_store, [plot_obj, download_button])

demo.launch()
