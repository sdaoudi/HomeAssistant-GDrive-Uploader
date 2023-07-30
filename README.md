# GDrive Uploader

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

GDrive Uploader is a [Home Assistant](https://www.home-assistant.io/)  integration that offers service to upload files
to Google Drive.

## Installation

Copy contents of custom_components/gdrive_uploader/ to custom_components/gdrive_uploader/ in your Home Assistant config folder.

## Services

### Example upload file

```yaml
service: gdrive_uploader.upload
data:
  parent_id: 20YTAZESppoiZ4hvuI543diltpez53tSt
  upload_file_path: /config/home-assistant.log
```

