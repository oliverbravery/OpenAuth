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

## Docker Setup
For simple containerization, you can use the provided `Dockerfile` and `docker-compose.yml` files to build the image and run the container. 
1. Ensure docker is installed and running on your machine:
```bash
docker --version
```
2. Use the following command to create, start and attach to the container:
```bash
docker-compose up
```