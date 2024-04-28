# Authentication and Authorization Service (auth_service)
This service is responsible for managing user authentication and authorization. It provides the following functionalities:
- Centralized user authentication, authorization, and user profile management

## Development Setup
1. Clone the repository.
2. Create a virtual environment and activate it:
```bash
python3.12 -m venv venv
source venv/bin/activate
```
3. Install the dependencies:
```bash
pip install -r requirements.txt
```
4. Copy the `.env.template` file to `.env` and update the environment variables:
```bash
cp .env.template .env
```
For generating auth client id and secret, use these commands respectively:
```bash
openssl rand -hex 32 # For client secret
openssl rand -hex 16 # For client id
```
For signing JWT tokens we use the RS256 algorithm. Private keys need to be PKCS#8. To generate a private and public key pair, use the following commands:
```bash
openssl genpkey -out environment/private.pem -algorithm RSA -pkeyopt rsa_keygen_bits:2048
openssl pkey -in environment/private.pem -outform PEM -pubout -out environment/public.pem
```
For encrypting the username with the authentication code (AUTH_CODE_SECRET). To generate the key, use the following command:
```bash
python 
from cryptography.fernet import Fernet
Fernet.generate_key()
```
5. To run the API server, use the following command:
```bash
uvicorn app.main:app
```

## Docker Setup and usage
For simple containerization, you can use the provided `Dockerfile` and `docker-compose.yml` files to build the image and run the container. 

*Ensure docker is installed and running on your machine before continuing:*
```bash
docker --version
```

Once everything is up and running you can check that the service is working by sending a GET request to the `/` endpoint:
```bash
# replace the host and port with the correct values from the .env file
curl http://${AUTH_SERVICE_HOST}:${AUTH_SERVICE_PORT}/
```

### Build and run the container
Use the following commands to build the image and run the container:
```bash
docker-compose down
docker-compose up -d
```

### Re-build the auth service api and run the container
If you want to re-build the authentication service but not the database (useful for development):
```bash
docker-compose down
docker-compose up -d --build auth_service_api
```

### Clear the database
To clear the database:
```bash
docker-compose down
docker volume rm auth_service_mongodb_data
```

### Fully clear the database, rebuild the container and run it
To fully clear the database, rebuild the container and run it:
```bash
docker-compose down
docker volume rm auth_service_mongodb_data
docker-compose up -d --build auth_service_api
```

# Project Structure
The project structure is as follows:


- `/` - The root directory of the project.

    - `/database` - contains all generic database interactions (i.e. "_get_user_").

    - `/models` - contains all the Pydantic models used throughout the project (i.e. "_Account_").
        
    - `/validators` - contains all validation related functions (i.e. "_check_user_exists_" and "_verify_captcha_completed_").

    - `/environment` - contains any non-committed environment files (i.e. private key PEM files).

    - `/routes` - contains all the API endpoints in their own files based on their route (i.e. "_/account.register_" would be in "_account.py_").

    - `/services` - contains all the business logic for the API endpoints (i.e. "_register_user_").

    - `/utils` - contains all the utility functions used throughout the project that don't rely on the database (i.e. "_hash_password_").

    - `/templates` - contains all the HTML templates for rendered responses.