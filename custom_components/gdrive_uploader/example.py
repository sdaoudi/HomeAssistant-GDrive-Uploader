from api import GDriveApi

secret_file_path = "service_account.json"
credentials_file_path = "credentials.json"

parent_id = "1ZwGEEDlsisVKBuhAl9LlJnLeIzn-j-IA"
upload_file_path = "/workspaces/homeassistant/config/home-assistant.log"

gdrive = GDriveApi(secret_file_path)
gdrive.upload_file(upload_file_path, parent_id)
