import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import GDriveApi
from .const import (ATTR_PARENT_ID, ATTR_TARGET_DIR_NAME, ATTR_UPLOAD_FILE_PATH,
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
    extra=vol.REMOVE_EXTRA,
)

def setup(hass, config):
    def handle_upload(call):
        secret_file_path = config.get(DOMAIN, {}).get(CONF_SECRET_FILE_PATH)
        upload_file_path = call.data.get(ATTR_UPLOAD_FILE_PATH)
        parent_id = call.data.get(ATTR_PARENT_ID)
        target_dir_name = call.data.get(ATTR_TARGET_DIR_NAME, "")

        try:
            gdrive = GDriveApi(secret_file_path)
            gdrive.upload_file(upload_file_path, parent_id, target_dir_name)
        except (FileExistsError, FileNotFoundError) as error:
            _LOGGER.error(error)

        hass.states.set("gdrive_uploader.upload", f"{upload_file_path}")

    hass.services.register(DOMAIN, "upload", handle_upload)

    return True
