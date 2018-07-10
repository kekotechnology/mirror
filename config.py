#Microsoft OAuth info

CLIENT_ID = '0f756d8d-6e4f-4b28-805a-41d4e7a92a0e'
CLIENT_SECRET = 'dmoeDVOF[sylCCA26059_@-'
REDIRECT_URI = 'http://localhost:5000/login/authorized'

# AUTHORITY_URL ending determines type of account that can be authenticated:
# /organizations = organizational accounts only
# /consumers = MSAs only (Microsoft Accounts - Live.com, Hotmail.com, etc.)
# /common = allow both types of accounts
AUTHORITY_URL = 'https://login.microsoftonline.com/common'

AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'
RESOURCE = 'https://graph.microsoft.com/'
API_VERSION = 'v1.0'
SCOPES = ['User.Read', 'Calendars.Read', 'Calendars.Read.Shared'] # Add other scopes/permissions as needed.