# Generating Access Token and Refresh Token with OAuth 2.0 (Google API)

This guide explains how to generate an `access_token` and a `refresh_token` using Google’s OAuth 2.0 API, then save this information into a JSON file for later use.

## Prerequisites

1. **Google Cloud Console**: Have a Google Cloud project set up with an **API enabled** (e.g., Google Drive API).
2. **Client ID and Client Secret**: Obtain your OAuth 2.0 credentials (Client ID and Client Secret) from [Google Cloud Console](https://console.cloud.google.com/).
3. **Authorization code**: This code is generated after the user authorizes your app via an OAuth authorization URL.

## Steps to Generate Access Token and Refresh Token

### 1. Create an OAuth Authorization URL

To obtain the authorization code, you need to direct the user to the following URL in a browser:

https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/drive.file&access_type=offline&prompt=consent


- **client_id**: Replace with your own Client ID.
- **redirect_uri**: The URL to which the user will be redirected after granting permission. Use `http://localhost` for local development.
- **scope**: The permissions required by your application. Example: `https://www.googleapis.com/auth/drive.file`.
- **access_type=offline**: Indicates that you are requesting a `refresh_token`.
- **prompt=consent**: Forces the user to give fresh consent.

### 2. Obtain the Authorization Code

Once the user is redirected and grants permission, an **authorization code** will be generated and sent in the redirection URL. Copy this code to use in the next step.

### 3. Use a Bash Script to Generate Access Token and Refresh Token

Create a Bash script to send a request to Google’s OAuth API, then generate a JSON file containing all the necessary information.

#### Bash Script

```bash
#!/bin/bash

# Define client_id, client_secret, and the authorization code
client_id="YOUR_CLIENT_ID"
client_secret="YOUR_CLIENT_SECRET"
code="YOUR_AUTH_CODE"
redirect_uri="http://localhost"
token_uri="https://oauth2.googleapis.com/token"

# Make a cURL request to retrieve the token
response=$(curl --silent --request POST \
  --url $token_uri \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data "code=$code" \
  --data "client_id=$client_id" \
  --data "client_secret=$client_secret" \
  --data "redirect_uri=$redirect_uri" \
  --data 'grant_type=authorization_code')

# Extract the necessary information from the JSON response using jq
access_token=$(echo "$response" | jq -r '.access_token')
refresh_token=$(echo "$response" | jq -r '.refresh_token')
expires_in=$(echo "$response" | jq -r '.expires_in')
scope=$(echo "$response" | jq -r '.scope')

# Get the current time in seconds since Unix epoch
current_time=$(date +%s)

# Add expires_in seconds to the current time to get the expiry time
expiry_time=$((current_time + expires_in))

# Convert the expiry time to ISO 8601 format
expiry_time_iso=$(date -u -d @"$expiry_time" +"%Y-%m-%dT%H:%M:%SZ")

# Create the JSON file in the required format
cat <<EOF > credentials.json
{
  "access_token": "$access_token",
  "client_id": "$client_id",
  "client_secret": "$client_secret",
  "refresh_token": "$refresh_token",
  "token_expiry": "$expiry_time_iso",
  "token_uri": "$token_uri",
  "user_agent": null,
  "revoke_uri": "https://oauth2.googleapis.com/revoke",
  "id_token": null,
  "id_token_jwt": null,
  "token_response": {
    "access_token": "$access_token",
    "expires_in": $expires_in,
    "scope": "$scope",
    "token_type": "Bearer"
  },
  "scopes": $(echo $scope | jq -R 'split(" ")'),
  "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
  "invalid": false,
  "_class": "OAuth2Credentials",
  "_module": "oauth2client.client"
}
EOF

echo "File 'credentials.json' generated successfully."
```

### 4. Run the Bash Script

1. Save the above script into a file, for example, generate_credentials.sh.
2. Make the script executable with the following command:
```bash
chmod +x generate_credentials.sh
````

3. Run the script:

```bash
./generate_credentials.sh
```

The script will generate a credentials.json file containing all the information, including the access_token, refresh_token, and token expiry.

### 5. Revoking Tokens

If you need to revoke access or tokens, you can use the following revocation URL:

```bash
curl --request POST \
  --url https://oauth2.googleapis.com/revoke \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data 'token=YOUR_ACCESS_OR_REFRESH_TOKEN'
```