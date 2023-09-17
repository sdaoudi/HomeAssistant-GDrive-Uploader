# GDrive Uploader

[![HACS Validation](https://github.com/sdaoudi/HomeAssistant-GDrive-Uploader/actions/workflows/hacs.yaml/badge.svg)](https://github.com/sdaoudi/HomeAssistant-GDrive-Uploader/actions/workflows/hacs.yaml)
[![hassfest Validation](https://github.com/sdaoudi/HomeAssistant-GDrive-Uploader/actions/workflows/hass.yaml/badge.svg)](https://github.com/sdaoudi/HomeAssistant-GDrive-Uploader/actions/workflows/hass.yaml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

GDrive Uploader is a [Home Assistant](https://www.home-assistant.io/)  integration that offers service to upload files to Google Drive.

## Installation

**Method 1.** [HACS](https://hacs.xyz/) custom repo:

> HACS > Integrations > 3 dots (upper top corner) > Custom repositories > URL: `sdaoudi/HomeAssistant-GDrive-Uploader`, Category: Integration > Add > wait > GDrive Uploader > Install

**Method 2.** Manually copy `gdrive_uploader` folder from [latest release](https://github.com/sdaoudi/HomeAssistant-GDrive-Uploader/releases/latest) to `/config/custom_components` folder.

## Configuration

In your `configuration.yaml`, include:

```yaml
gdrive_uploader:
  secret_file_path: "/config/secrets/credentials.json"
```

The `credentials.json` is the path to your credetnials.json file generated with your client_id and client_secret.

## Usage

### Upload file

New service `gdrive_uploader.upload`:

```yaml
script:
  upload_video:
    alias: Upload video
    sequence:
      - service: gdrive_uploader.upload
        data:
          parent_id: 20YTAZESppoiZ4hvuI543diltpez53tSt # Google Drive folder ID
          upload_file_path: /config/home-assistant.log # Path of file to upload
```

You can specify a `target_dir_name`, which allows you to create a new directory within the parent directory, and it is this new directory where your file will be uploaded:

```yaml
script:
  upload_video:
    alias: Upload video
    sequence:
      - service: gdrive_uploader.upload
        data:
          parent_id: 20YTAZESppoiZ4hvuI543diltpez53tSt
          target_dir_name: "my_videos"
          upload_file_path: /config/home-assistant.log
```

### Delete file or directory

New service `gdrive_uploader.delete`:

```yaml
script:
  upload_video:
    alias: Upload video
    sequence:
      - service: gdrive_uploader.upload
        data:
          parent_id: 20YTAZESppoiZ4hvuI543diltpez53tSt # Google Drive folder ID
          dir_name: my_dir_to_remove # The directory name in Google Drive
```
