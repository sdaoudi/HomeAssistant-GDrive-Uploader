import logging
import threading

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import GDriveApi
from .const import (
    ATTR_DIR_NAME,
    ATTR_PARENT_ID,
    ATTR_TARGET_DIR_NAME,
    ATTR_UPLOAD_FILE_PATH,
    ATTR_OVERRIDE_FILE,
    CREDENTIALS_FILE_PATH,
    DOMAIN,
    SECRET_FILE_PATH,
    UPLOAD_COMPLETED_EVENT,
    UPLOAD_FAILED_EVENT,
)

_LOGGER = logging.getLogger(__name__)


def validate_credentials_or_secret(value):
    if CREDENTIALS_FILE_PATH in value or SECRET_FILE_PATH in value:
        return value
    raise vol.Invalid(
        "Either CREDENTIALS_FILE_PATH or SECRET_FILE_PATH must be provided"
    )


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            vol.Schema(
                {
                    vol.Optional(CREDENTIALS_FILE_PATH): cv.isfile,
                    vol.Optional(SECRET_FILE_PATH): cv.isfile,
                }
            ),
            validate_credentials_or_secret,
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    def handle_upload(call):
        credentials_file_path = config.get(DOMAIN, {}).get(
            CREDENTIALS_FILE_PATH
        ) or config.get(DOMAIN, {}).get(SECRET_FILE_PATH)

        upload_file_path = call.data.get(ATTR_UPLOAD_FILE_PATH)
        parent_id = call.data.get(ATTR_PARENT_ID)
        target_dir_name = call.data.get(ATTR_TARGET_DIR_NAME, "")
        override_file = call.data.get(ATTR_OVERRIDE_FILE, False)

        gdrive = GDriveApi(credentials_file_path)
        try:
            file = gdrive.upload_file(upload_file_path, parent_id, target_dir_name, override_file)
            hass.bus.fire(
                f"{DOMAIN}_{UPLOAD_COMPLETED_EVENT}",
                {"file_id": file["id"]},
            )
        except (FileExistsError, FileNotFoundError) as error:
            _LOGGER.error(error)
            hass.bus.fire(
                f"{DOMAIN}_{UPLOAD_FAILED_EVENT}",
                {"message": str(error)},
            )

    def handle_delete(call):
        credentials_file_path = config.get(DOMAIN, {}).get(CREDENTIALS_FILE_PATH)
        parent_id = call.data.get(ATTR_PARENT_ID)
        dir_name = call.data.get(ATTR_DIR_NAME)
        gdrive = GDriveApi(credentials_file_path)
        delete_lock = threading.Lock()

        def do_delete():
            with delete_lock:
                gdrive.delete_directory_by_name(parent_id, dir_name)

        threading.Thread(target=do_delete).start()

    hass.services.register(DOMAIN, "upload", handle_upload)
    hass.services.register(DOMAIN, "delete", handle_delete)

    return True
