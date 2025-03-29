import errno

import os
import shutil
import uuid

from app.core.constants import GCODE_FILE_SAVE_NAME, BASE_DIR

GCODE_CACHE_LOCATION = os.path.join(BASE_DIR, "gcode_cache")

if not os.path.exists(GCODE_CACHE_LOCATION):
    os.makedirs(GCODE_CACHE_LOCATION)


def delete_state_folder_location(settings_session_id):
    try:
        shutil.rmtree(os.path.join(GCODE_CACHE_LOCATION, settings_session_id))
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise


class UserGCodeSettingsSession:
    def __init__(self, config_settings):
        self.settings_session_id = uuid.uuid4().hex
        self._settings_store = config_settings

        # Create user tmp folder
        self.generate_folder_for_session(self.settings_session_id)

    def generate_folder_for_session(self, session_id):
        os.makedirs(os.path.join(GCODE_CACHE_LOCATION, session_id))
        print("generated save folder for id: ", self.settings_session_id)
        return

    @property
    def settings(self):
        return self._settings_store

    def update_state(self, field_name, value):
        print(f"Updating state for {field_name} with value {value}")
        self._settings_store[field_name] = value
        return self._settings_store

    def generate_path_for_gcode_file(self):
        return os.path.join(GCODE_CACHE_LOCATION, self.settings_session_id, GCODE_FILE_SAVE_NAME)

    def close(self):
        print(f"Deleting state folder for {self.settings_session_id}")
        delete_state_folder_location(self.settings_session_id)
        return
