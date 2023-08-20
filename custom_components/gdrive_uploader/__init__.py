import logging
import threading

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import GDriveApi
from .const import (ATTR_DIR_NAME, ATTR_PARENT_ID, ATTR_TARGET_DIR_NAME, ATTR_UPLOAD_FILE_PATH,
                    CONF_SECRET_FILE_PATH, DOMAIN)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SECRET_FILE_PATH): cv.isfile,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    def handle_upload(call):
        secret_file_path = config.get(DOMAIN, {}).get(CONF_SECRET_FILE_PATH)
        upload_file_path = call.data.get(ATTR_UPLOAD_FILE_PATH)
        parent_id = call.data.get(ATTR_PARENT_ID)
        target_dir_name = call.data.get(ATTR_TARGET_DIR_NAME, "")
        gdrive = GDriveApi(secret_file_path)

        def do_upload():
            """Upload the file."""
            try:
                gdrive.upload_file(upload_file_path, parent_id, target_dir_name)
            except (FileExistsError, FileNotFoundError) as error:
                _LOGGER.error(error)

        if not gdrive.resource_exists(parent_id, target_dir_name):
            gdrive.create_folder(parent_id, target_dir_name)

        threading.Thread(target=do_upload).start()

    def handle_delete(call):
        secret_file_path = config.get(DOMAIN, {}).get(CONF_SECRET_FILE_PATH)
        parent_id = call.data.get(ATTR_PARENT_ID)
        dir_name = call.data.get(ATTR_DIR_NAME)
        gdrive = GDriveApi(secret_file_path)

        def do_delete():
            gdrive.delete_directory_by_name(parent_id, dir_name)

        threading.Thread(target=do_delete).start()

    hass.services.register(DOMAIN, "upload", handle_upload)
    hass.services.register(DOMAIN, "delete", handle_delete)

    return True
