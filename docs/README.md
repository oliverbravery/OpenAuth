# Open Auth
Open Auth provides authentication and authorization for other services. It is built using the FastAPI framework and MongoDB. This service follows the [OAuth 2.0 protocol](https://datatracker.ietf.org/doc/html/rfc6749) and complies with the [Authorization Code flow with PKCE (Proof Key Code Exchange)](https://datatracker.ietf.org/doc/html/rfc7636).

> **Note:** This service is still under development and is not yet ready for production use. Many features are still missing, and the service is not yet secure. Please use this service at your own risk. I will try to address any issues and implement any suggestions as soon as possible but please be patient as this is a side project.

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
    - [Authentication Flow](#authentication-flow)
    - [Refresh Token Flow](#refresh-token-flow)
- [Issues and Suggestions](#issues-and-suggestions)
- [Upcoming Features](#upcoming-features)
- [License](#license)
- [Development](#development)
- [Support](#support)

## Quick Links
- [API Documentation](ENDPOINTS.md)
- [Environment Setup](ENVIRONMENT.md)
- [Development Documentation](DEVELOPMENT.md)

## Getting Started
### Prerequisites
Before you can get started with Open Auth, you need to have the following installed on your system:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.12](https://www.python.org/downloads/release/python-3120/)

### Installation
To get started with Open Auth, follow the steps below:
1. Clone the repository:
```bash
git clone https://github.com/oliverbravery/OpenAuth
```
2. Change into the project directory:
```bash
cd OpenAuth
```
3. Copy the `.env.template` file and rename it to `.env`:
```bash
cp .env.template .env
```
4. Open the `.env` file and fill in the values for the environment variables. If you are unsure about how to generate the values, refer to the [Environment Variables](ENVIRONMENT.md) documentation.
5. Start the service using Docker Compose. Note that this command will build the service and start it in detached mode (in the background):
```bash
docker-compose up --build -d
```
## Usage
All the endpoints for Open Auth are documented in the [API documentation](ENDPOINTS.md) file. Below is a breif overview of the flow to authenticate a user.
### Authentication Flow
1. Register the new user using the `/account/register` endpoint.
2. To authenticate the user, redirect them to the `/authentication/authorize` endpoint with the required parameters. The user will be prompted to log in and authorize the client.
3. After the user has authorized the client, they will be redirected back to the client (using the redirect uri of the stored client) with an authorization code.
4. The client can then exchange the authorization code for an access token and refresh token using the `/authentication/token` endpoint.
5. The client can then use the access token to access the protected resources of the user.
### Refresh Token Flow
1. If the access token expires, the client can use the refresh token to get a new access token using the `/authentication/token` endpoint.
2. The client can then use the new access token to access the protected resources of the user. Note that the previous refresh token will be invalidated.

## Issues and Suggestions
If you encounter any issues or have any suggestions for Open Auth, please open an issue on the [GitHub repository](https://github.com/oliverbravery/OpenAuth/issues). Your feedback is greatly appreciated. I will do my best to address any issues and implement any suggestions as soon as possible but please be patient as this is a side project.

## Upcoming Features
The following features are planned for future releases of Open Auth:
- Logging and monitoring - Implement functionality to log requests and responses and monitor the service for errors.
- Rate limiting - Implement rate limiting to prevent abuse of the service.
- Full test coverage - Write unit tests for all endpoints and services to ensure the service is working as expected.
- Improved Encryption - Implement better encryption to encrypt all user data at rest.
- Passkey Authentication - Implement passkey authentication through the [FIDO2](https://fidoalliance.org/fido2/) protocol.

## License
This project is licensed under the MIT License - see the [LICENSE](/LICENSE.md) file for details.

## Development
All development-related documentation can be found in the [development documentation](/docs/DEVELOPMENT.md). This includes information on the project structure and coding standards.

> **Note:** This is a side project, and as such, contributions may take some time to be reviewed and merged. I will do my best to address any issues and implement any suggestions as soon as possible but please be patient.

## Support
As a university student, I dedicate a significant amount of my free time to maintaining and improving projects like this one. If you would like to support me and my work, please consider sponsoring me on GitHub. Your support means a lot to me and helps me to continue developing and maintaining these projects. Thank you for your support!
