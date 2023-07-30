import logging
import os
from httpx import delete

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
                _LOGGER.debug(f"target directory already exists with id : {target_directory['id']}")
            except FileNotFoundError:
                target_directory = self.create_folder(parent_dir_id, directory_name)
                _LOGGER.debug(f"The target directory has just been created with id : {target_directory['id']}")
        else:
            target_directory = {"id": parent_dir_id}
            _LOGGER.debug("The parent directory is used as a target directory")

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
        _LOGGER.debug(f"A new file is create with id: {file['id']}")
        return file

    def delete_directory_by_name(self, parent_dir_id, directory_name):
        try:
            resource = self.find_resource_by_title(parent_dir_id, directory_name)
            self._delete_resource(resource["id"])
            resource.Delete()
        except FileNotFoundError:
            _LOGGER.debug(f"The {directory_name} directory is not deleted because it does not exist.")

    def _delete_resource(self, resource_id):
        file_list = self.drive.ListFile({'q': f"'{resource_id}' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self._delete_resource(file['id'])
            file.Delete()


