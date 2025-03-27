import gradio as gr
import tempfile


from app.core.models import GcodeSettings
from app.generate_code import ASTM638TestSampleGCodeGenerator
from app.render import render_config_field, get_plot_object_from_gcode

settings = GcodeSettings.from_json_file("./config.json")


def generate_gcode(state):
    print(state)
    gcode_generator = ASTM638TestSampleGCodeGenerator(app_config=state)
    plot_fig = get_plot_object_from_gcode(gcode_generator.path())
    gcode_file_str = gcode_generator.gcode_file()

    # tmp = tempfile.mkstemp()
    # with open(tmp.name, 'w') as f:
    #     f.write(gcode_file_str)

    return {
        plot_obj: plot_fig,
        download_button: gr.DownloadButton(value=None, label="Download GCODE File", visible=True, interactive=True)
    }


with gr.Blocks() as demo:
    gr.HTML("""<h1 style="text-align: center;">ASTM D638 Test Sample GCode Generator</h1>""")
    settings_fields = []
    browser_local_storage = gr.BrowserState(settings.default_values())
    with gr.Row():
        with gr.Column(scale=2):
            for section in settings.sections:
                with gr.Tab(section.section_name):
                    for field in section.fields:
                        settings_fields.append(render_config_field(config_field=field, state=browser_local_storage)[1])
            generate_button = gr.Button("Generate GCODE")

        with gr.Column(scale=2):
            plot_obj = gr.Plot(label="forecast", format="png")
            download_button = gr.DownloadButton(visible=False, interactive=False)

    generate_button.click(generate_gcode, browser_local_storage, [plot_obj, download_button])

#  TODO Do loading settings from browser memory.
#  TODO Fix issue with refreshing settings on browser
# Implement downloading of data
demo.launch()
