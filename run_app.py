# from app.application import start_app
import gradio as gr

from app.core.models import GcodeSettings
from app.generator import ASTM638TestSampleGCodeGenerator
from app.renderer import render_config_field

settings = GcodeSettings.from_json_file("./config.json")
print(settings.model_dump_json())


def generate_gcode(state, download_button):
    print(state)
    generated_code = ASTM638TestSampleGCodeGenerator(app_config=state).generate_code(as_bytes=True)
    # download_button.interactive = True
    # download_button.visible = True
    return generated_code


with gr.Blocks() as demo:
    gr.Markdown("Test app")
    settings_fields = []
    state = gr.BrowserState(settings.default_values())
    with gr.Column():
        for section in settings.sections:
            with gr.Tab(section.section_name):
                for field in section.fields:
                    settings_fields.append(render_config_field(config_field=field, state=state)[1])
        generate_button = gr.Button("Generate GCODE")

    with gr.Column():
        download_button = gr.DownloadButton(label="Download GCODE", value=None, interactive=False)

    generate_button.click(generate_gcode, [state, download_button], download_button)

#  TODO Do loading settings from browser memory.
#  TODO Fix issue with refreshing settings on browser

demo.launch()
