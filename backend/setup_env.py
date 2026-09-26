"""
Setup script to create .env file for PeopleHub HRMS.
Run this script to configure your environment variables.
"""
import os

def create_env_file():
    """Create .env file with default configuration."""
    env_content = """# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/peoplehub
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=peoplehub
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Configuration
APP_NAME=PeopleHub HRMS
APP_VERSION=1.0.0
DEBUG=True

# CORS Configuration
FRONTEND_URL=http://localhost:8501
"""
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f".env file created at: {env_path}")
    print("Please update the following values:")
    print("   - DATABASE_PASSWORD: Your PostgreSQL password")
    print("   - SECRET_KEY: A secure secret key for JWT")
    print("   - OPENAI_API_KEY: Your OpenAI API key (optional)")
    print("\nAfter updating, you can run the seed script:")
    print("   python seed_data.py")


if __name__ == "__main__":
    create_env_file()