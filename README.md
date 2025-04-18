# FastAPI Spring Boot Style Architecture

A modern, high-performance web API built with FastAPI, following a Spring Boot-inspired architecture. This project demonstrates best practices for building production-ready Python web applications with a clean, organized structure.

## Features
- **Authentication & Authorization**: JWT-based authentication system with role-based access control
- **MongoDB Integration**: Asynchronous database access using Motor
- **Clean Architecture**: Separation of concerns with controllers, services, repositories, and entities
- **Type Safety**: Full type hinting with Pydantic models
- **Exception Handling**: Comprehensive error handling system
- **Code Quality**: Configured with Ruff for linting and formatting

## Project Structure

```
.
├── src/
│   ├── configs/          # Configuration modules
│   ├── controllers/      # API route handlers
│   ├── dtos/             # Data Transfer Objects
│   ├── entities/         # Database models
│   ├── exceptions/       # Custom exception classes
│   ├── models/           # Response models
│   ├── repositories/     # Database access layer
│   ├── services/         # Business logic layer
│   ├── utils/            # Utility functions and classes
|   └── main.py           # Main ruunner
├── pyproject.toml        # Project configuration
├── requirements.txt      # Project dependencies
├── docker-compose.yml    # Docker configuration
├── private.pem           # RSA private key for JWT signing
├── public.pem            # RSA public key for JWT verification
└── README.md             # Project documentation
```

## Prerequisites

- Python 3.12+
- MongoDB
- Poetry (optional, for dependency management)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/xtAngmO/fastAPI-spring-boot-style-architecture
cd fastAPI-spring-boot-style-architecture
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fastapi_db
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=developer
```

5. Generate RSA key pair for JWT authentication:

```bash
# Install the required package
pip install cryptography

# Generate private and public keys
python -c "
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Get private key in PEM format (TraditionalOpenSSL format for compatibility)
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)

# Get public key in PEM format
public_key = private_key.public_key()
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# Write keys to files
with open('private.pem', 'wb') as f:
    f.write(private_key_pem)

with open('public.pem', 'wb') as f:
    f.write(public_key_pem)

print('RSA key pair generated successfully.')
"
```

## Running the Application

Start the application:

```bash
python -m src.main
```

The API will be available at `http://localhost:8080`.

## API Documentation

Once the application is running, you can access:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Authentication

### Register a new user

```bash
curl -X POST "http://localhost:8080/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"john","password":"password123","email":"john@example.com","name":"John Doe"}'
```

### Login

```bash
curl -X POST "http://localhost:8080/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"john","password":"password123"}'
```

### Protected routes

Use the JWT token from login:

```bash
curl -X GET "http://localhost:8080/api/auth/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## JWT Key Management

This project uses RS256 algorithm for JWT authentication, which requires a pair of RSA keys:

- `private.pem`: Used to sign JWT tokens
- `public.pem`: Used to verify JWT tokens

Benefits of using RSA keys for JWT:
- Asymmetric cryptography provides better security than symmetric algorithms
- The private key is only needed for signing tokens (on your server)
- The public key can be shared for token verification (could be distributed to other services)

If you need to regenerate the keys, run the script provided in the Installation section.

## Development

### Code Quality

The project uses Ruff for linting and formatting. Run:

```bash
ruff check .
ruff format .
```

### Database Management

The application uses MongoDB. Ensure you have MongoDB running locally or update the connection string in your `.env` file.

## Docker Deployment

1. Build and start the containers:

```bash
docker-compose up -d
```

2. The API will be available at `http://localhost:8080`.

## Troubleshooting

### JWT Authentication Issues

If you encounter JWT authentication errors:

1. Check that your RSA keys are properly formatted:
   - Private key should begin with `-----BEGIN RSA PRIVATE KEY-----`
   - Public key should begin with `-----BEGIN PUBLIC KEY-----`

2. Make sure the paths in your `.env` file are correct and the application can access the key files.

3. For development purposes, you can alternatively use HS256 algorithm with a symmetric key by modifying the JwtService class.