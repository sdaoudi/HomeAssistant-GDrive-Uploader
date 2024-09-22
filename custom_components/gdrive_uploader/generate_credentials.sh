#!/bin/bash

# Define client_id, client_secret, and the authorization code
client_id="YOUR_CLIENT_ID"
client_secret="YOUR_CLIENT_SECRET"
code="YOUR_AUTH_CODE"
redirect_uri="http://localhost"
token_uri="https://oauth2.googleapis.com/token"

# Run a cURL request to retrieve the token
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

echo "The file 'credentials.json' has been generated successfully."
