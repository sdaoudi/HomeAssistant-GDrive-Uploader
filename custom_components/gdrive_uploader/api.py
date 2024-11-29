import json
import logging
import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

_LOGGER = logging.getLogger(__name__)


class GDriveApi:
    def __init__(self, credentials_file_path: str):
        gauth = GoogleAuth()
        # Vérify if the file exists
        if not os.path.exists(credentials_file_path):
            error_message = (
                f"The credentials file {credentials_file_path} does not exist."
            )
            _LOGGER.error(error_message)
            raise FileNotFoundError(error_message)

        # Load the credentials from the file and raise an error if it is empty
        try:
            json_data = json.load(open(credentials_file_path))
        except json.JSONDecodeError:
            error_message = f"The credentials file {credentials_file_path} is empty."
            _LOGGER.error(error_message)
            raise json.JSONDecodeError(error_message)

        # Verify if the json_data contains the access_token
        if "access_token" in json_data:
            gauth.LoadCredentialsFile(credentials_file_path)
            if gauth.access_token_expired:
                # Refresh them if expired
                gauth.Refresh()
            else:
                # Initialize the saved creds
                gauth.Authorize()
            # Save the current credentials to a file
            gauth.SaveCredentialsFile(credentials_file_path)
            self.drive = GoogleDrive(gauth)
        # Verify if the credentials file is a service account
        elif "type" in json_data and json_data["type"] == "service_account":
            settings = {
                "client_config_backend": "service",
                "service_config": {
                    "client_json_file_path": credentials_file_path,
                },
            }
            gauth = GoogleAuth(settings=settings)
            gauth.ServiceAuth()
            self.drive = GoogleDrive(gauth)
        else:
            error_message = (
                "The credentials file is not valid. Please check the format."
            )
            _LOGGER.error(error_message)
            raise ValueError(error_message)

    def _create_folder(self, parent_folder_id, subfolder_name):
        _LOGGER.debug(f"Create folder {subfolder_name} in parent {parent_folder_id}")
        new_folder = self.drive.CreateFile(
            {
                "title": subfolder_name,
                "parents": [{"kind": "drive#fileLink", "id": parent_folder_id}],
                "mimeType": "application/vnd.google-apps.folder",
            }
        )

        new_folder.Upload()
        return new_folder

    # Fonction pour obtenir l'ID du sous-dossier s'il existe, sinon renvoie None
    def _get_subfolder_id(self, parent_folder_id, subfolder_name):
        query = f"'{parent_folder_id}' in parents and title = '{subfolder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        subfolder_list = self.drive.ListFile({"q": query}).GetList()

        if subfolder_list:
            return subfolder_list[0]["id"]
        else:
            return None

    # Création de l'arborescence de répertoires si elle n'existe pas
    def _create_subfolders(self, root_folder_id, folder_names):
        current_folder_id = root_folder_id

        for folder_name in folder_names:
            subfolder_id = self._get_subfolder_id(current_folder_id, folder_name)

            if subfolder_id:
                current_folder_id = subfolder_id
            else:
                new_folder = self._create_folder(current_folder_id, folder_name)
                current_folder_id = new_folder["id"]

        return current_folder_id

    def upload_file(self, source_file_path, parent_dir_id, directory_name: str = "", override_file: bool = False):
        _LOGGER.debug(f"source file path : {source_file_path}")
        _LOGGER.debug(f"parent directory id : {parent_dir_id}")
        _LOGGER.debug(f"directory name : {str(directory_name)}")
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(
                f"The file with path {source_file_path} is not found."
            )

        if directory_name != "":
            folder_names_to_create = directory_name.split("/")
            final_folder_id = self._create_subfolders(
                parent_dir_id, folder_names_to_create
            )
        else:
            final_folder_id = parent_dir_id
            _LOGGER.debug("The parent directory is used as a target directory")

        filename = os.path.basename(source_file_path)
        file_id = self._resource_exists(final_folder_id, filename)
        if file_id and not override_file:
            raise FileExistsError(
                f"File already exists in Google Drive with {filename} name."
            )

        if file_id and override_file:
            _LOGGER.debug(f"File already exists in Google Drive with {filename} name. Overriding...")
            file = self.drive.CreateFile({'id': file_id})
        else:
            file = self.drive.CreateFile({"parents": [{"id": final_folder_id}]})

        file.SetContentFile(source_file_path)
        file.Upload()
        _LOGGER.debug(f"A new file is created with id: {file['id']}")

        return file

    def _find_resource_by_title(self, parent_directory_id, resource_title):
        resource_list = self.drive.ListFile(
            {"q": f"'{parent_directory_id}' in parents and trashed=false"}
        ).GetList()

        for resource in resource_list:
            if resource["title"] == resource_title:
                return resource
        raise FileNotFoundError(
            f"The resource with title {resource_title} is not found inside the folder with {parent_directory_id} id."
        )

    def _resource_exists(self, parent_directory_id, resource_title):
        resource_list = self.drive.ListFile(
            {"q": f"'{parent_directory_id}' in parents and trashed=false"}
        ).GetList()
        for resource in resource_list:
            if resource["title"] == resource_title:
                _LOGGER.debug(
                    f"resource {resource_title} exists in parent {parent_directory_id}"
                )
                return resource["id"]

        _LOGGER.debug(
            f"resource {resource_title} not exists in parent {parent_directory_id}"
        )
        return False

    def delete_directory_by_name(self, parent_dir_id, directory_name):
        try:
            resource = self._find_resource_by_title(parent_dir_id, directory_name)
            self._delete_resource(resource["id"])
            resource.Delete()
        except FileNotFoundError:
            _LOGGER.debug(
                f"The {directory_name} directory is not deleted because it does not exist."
            )

    def _delete_resource(self, resource_id):
        file_list = self.drive.ListFile(
            {"q": f"'{resource_id}' in parents and trashed=false"}
        ).GetList()
        for file in file_list:
            if file["mimeType"] == "application/vnd.google-apps.folder":
                self._delete_resource(file["id"])
            file.Delete()
