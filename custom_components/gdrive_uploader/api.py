import logging
import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

_LOGGER = logging.getLogger(__name__)

class GDriveApi:
    def __init__(self, client_secret_file_path: str):
        settings = {
                "client_config_backend": "service",
                "service_config": {
                    "client_json_file_path": client_secret_file_path,
                }
            }
        gauth = GoogleAuth(settings=settings)
        gauth.ServiceAuth()
        self.drive = GoogleDrive(gauth)

    def create_folder(self, parent_folder_id, subfolder_name):
        new_folder = self.drive.CreateFile(
            {
                'title': subfolder_name,
                "parents": [
                    {
                        "kind": "drive#fileLink",
                        "id": parent_folder_id
                    }
                ],
                "mimeType": "application/vnd.google-apps.folder"
             }
        )

        new_folder.Upload()
        return new_folder


    def find_resource_by_title(self, parent_directory_id, resource_title):
        resource_list = self.drive.ListFile(
            {'q': f"'{parent_directory_id}' in parents and trashed=false"}
        ).GetList()

        for resource in resource_list:
            if(resource['title'] == resource_title):
                return resource
        raise FileNotFoundError(f"The resource with title {resource_title} is not found inside the folder with {parent_directory_id} id.")

    def resource_exists(self, parent_directory_id, resource_title):
        resource_list = self.drive.ListFile({'q':  f"'{parent_directory_id}' in parents and trashed=false"}).GetList()
        for resource in resource_list:
            if(resource['title'] == resource_title):
                return resource
        return None

    def upload_file(self, source_file_path, parent_dir_id, directory_name):
        _LOGGER.debug(f"source file path : {source_file_path}")
        _LOGGER.debug(f"parent directory id : {parent_dir_id}")
        _LOGGER.debug(f"directory name : {str(directory_name)}")
        if (not os.path.exists(source_file_path)):
            raise FileNotFoundError(f"The file with path {source_file_path} is not found.")

        if directory_name != "":
            try:
                target_directory = self.find_resource_by_title(parent_dir_id, str(directory_name))
            except FileNotFoundError:
                target_directory = self.create_folder(parent_dir_id, directory_name)
        else:
            target_directory = {"id": parent_dir_id}

        filename = os.path.basename(source_file_path)
        if (self.resource_exists(target_directory["id"], filename)):
            raise FileExistsError(f"File already exists in Google Drive with {filename} name.")

        file = self.drive.CreateFile(
            {
                "parents": [
                    {
                        "id": target_directory["id"]
                    }
                ]
            }
        )
        file.SetContentFile(source_file_path)
        file.Upload()
        return file
