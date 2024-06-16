# Environment Setup
_This document explains how to set up the environment for the service._

To prevent hard-coding sensitive information, the applications use environment variables. The [.env.template](../.env.template) file contains the list of environment variables used by the applications alongside their descriptions. There is also a [`/environment`](../environment/) directory which should contain the private and public keys for [signing JWT tokens](#jwt-variables) alongside the [default client model](#default-client-variables) (more on that later).

## Setup Steps
1. Copy the [.env.template](../.env.template) file and rename it to `.env`.
```bash
cp .env.template .env
```
2. Open the `.env` file and fill in the values for the environment variables. If you are unsure about how to generate the values, refer to the [Environment Variables](#environment-variables) section below.

## Environment Variables

- [Connection Variables](#connection-variables)
- [Auth Database Connection Variables](#database-connection-variables)
- [JWT Variables](#jwt-variables)
- [Google reCAPTCHA Variables](#google-recaptcha-variables)
- [Authorization Variables](#authorization-variables)
- [Default Client Variables](#default-client-variables)

#### Connection Variables

- `AUTH_HOST` - The host of the Open Auth service. Should be a domain name or IP address. For local development, use '0.0.0.0'.
- `AUTH_PORT` - The port of the Open Auth service. Should be an integer representing the port number used for the API.

#### Database Connection Variables

- `AUTH_MONGO_HOST` - The host of the MongoDB database. Should be a domain name or IP address. For local development, use 'mongodb'.
- `AUTH_MONGO_PORT` - The port of the MongoDB database. Should be an integer representing the port number for the MongoDB database.
- `AUTH_MONGO_DATABASE_NAME` - The name of the MongoDB database to use.
- `AUTH_MONGO_USERNAME` - The username of the MongoDB root user. This user will be given the root role. It is created when the MongoDB container is started for the first time.
- `AUTH_MONGO_PASSWORD` - The password of the MongoDB root user. This user will be given the root role. It is created when the MongoDB container is started for the first time.

#### JWT Variables

- `AUTH_ACCESS_TOKEN_EXPIRE` - The time in minutes for the access token to expire. Should be between 15 and 30 minutes.
- `AUTH_REFRESH_TOKEN_EXPIRE` - The time in minutes for the refresh token to expire. Should be between 30 and 90 days.
- `AUTH_STATE_TOKEN_EXPIRE` - The time in minutes for the state token to expire. Should be between 1 and 5 minutes.
- `AUTH_TOKEN_ALGORITHM` - The algorithm used to sign the JWT tokens. Should be 'RS256'.
- `AUTH_JWT_PRIVATE_PEM_PATH` - The path to the private key used to sign the JWT tokens. You can use this command to generate a private key: 
    ```bash
    openssl genpkey -out environment/private.pem -algorithm RSA -pkeyopt rsa_keygen_bits:2048
    ```
- `AUTH_JWT_PUBLIC_PEM_PATH` - The path to the public key used to verify the JWT tokens. You can use this command to generate a public key:
    ```bash
    openssl pkey -in environment/private.pem -outform PEM -pubout -out environment/public.pem
    ```

#### Google reCAPTCHA Variables

- `AUTH_RECAPTCHA_SITE_KEY` - The site key for Google reCAPTCHA. You can get this key from the Google reCAPTCHA website.
- `AUTH_RECAPTCHA_SECRET_KEY` - The secret key for Google reCAPTCHA. You can get this key from the Google reCAPTCHA website.

#### Authorization Variables

- `AUTH_CODE_SECRET` - The secret key used to encrypt the username with the authentication code. You can generate this key using the following command:
    ```bash
    python
    from cryptography.fernet import Fernet
    Fernet.generate_key()
    ```

#### Default Client Variables

- `AUTH_DEFAULT_CLIENT_ID` - The default client ID for the Auth service. Must be a random 128-bit hexadecimal value. You can generate this key using the following command:
    ```bash
    openssl rand -hex 16
    ```
- `AUTH_DEFAULT_CLIENT_SECRET` - The default client secret for the Auth service. Must be a random 256-bit hexadecimal value. You can generate this key using the following command:
    ```bash
    openssl rand -hex 32
    ```
- `AUTH_DEFAULT_CLIENT_MODEL_PATH` - A model of a client to be created when the application starts for the first time. The client will only be created once. An initial client is important as a client is required to generate tokens to use the API. It is recommended to use the template below:
    ```json
    {
        "client_id": "auto-generated from environment",
        "client_secret_hash": "auto-generated from environment",
        "name": "Authentication Service",
        "description": "This service provides authentication and authorization for the platform.",
        "redirect_uri": "auto-generated from environment",
        "developers": [
        ],
        "profile_metadata_attributes": [
        ],
        "profile_defaults": {
        },
        "scopes": [
        ]
    }
    ```