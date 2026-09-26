"""
PostgreSQL setup helper for PeopleHub HRMS.
This script helps diagnose PostgreSQL connection issues.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

def test_postgres_connection():
    """Test PostgreSQL connection with current credentials."""
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/peoplehub")
    
    print("Testing PostgreSQL connection...")
    print(f"DATABASE_URL: {db_url}")
    
    try:
        # Parse connection string
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(db_url)
        except ImportError:
            import urlparse
            parsed = urlparse.urlparse(db_url)
        
        connection_params = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "database": parsed.path[1:] if parsed.path else "peoplehub",
            "user": parsed.username or "postgres",
            "password": parsed.password or "password"
        }
        
        print(f"Host: {connection_params['host']}")
        print(f"Port: {connection_params['port']}")
        print(f"Database: {connection_params['database']}")
        print(f"User: {connection_params['user']}")
        
        conn = psycopg2.connect(**connection_params)
        print("SUCCESS: PostgreSQL connection successful!")
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"FAILED: PostgreSQL connection failed")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def provide_solutions():
    """Provide solutions for PostgreSQL setup."""
    print("\n" + "="*60)
    print("SOLUTIONS FOR POSTGRESQL SETUP")
    print("="*60)
    
    print("\nOption 1: Start Docker Desktop")
    print("-" * 40)
    print("1. Start Docker Desktop from your applications")
    print("2. Run: docker-compose up -d postgres")
    print("3. Wait for PostgreSQL to start")
    print("4. Run: python seed_data.py")
    
    print("\nOption 2: Use Local PostgreSQL")
    print("-" * 40)
    print("1. Install PostgreSQL 15+ from https://www.postgresql.org/download/windows/")
    print("2. During installation, set password to 'password'")
    print("3. Create database 'peoplehub'")
    print("4. Update .env file with your PostgreSQL password if different")
    print("5. Run: python seed_data.py")
    
    print("\nOption 3: Update .env with Your PostgreSQL Credentials")
    print("-" * 40)
    print("1. If you have PostgreSQL running with different credentials:")
    print("2. Edit the .env file in the backend directory")
    print("3. Update these lines:")
    print("   DATABASE_PASSWORD=your_actual_password")
    print("   DATABASE_USER=your_postgres_user")
    print("   DATABASE_HOST=your_host (if not localhost)")
    print("   DATABASE_PORT=your_port (if not 5432)")
    print("4. Run: python seed_data.py")
    
    print("\nOption 4: Use SQLite for Testing (Quick Start)")
    print("-" * 40)
    print("1. Update DATABASE_URL in .env to use SQLite:")
    print("   DATABASE_URL=sqlite:///peoplehub.db")
    print("2. Run: python seed_data.py")
    print("Note: SQLite doesn't require a separate database server")


def main():
    """Main function."""
    print("PeopleHub HRMS - PostgreSQL Setup Helper")
    print("=" * 60)
    
    # Test current connection
    success = test_postgres_connection()
    
    if not success:
        provide_solutions()
        
        print("\n" + "="*60)
        choice = input("Would you like to use SQLite for testing? (y/n): ")
        
        if choice.lower() == 'y':
            print("\nSwitching to SQLite for testing...")
            load_dotenv()
            
            # Update .env file for SQLite
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Replace DATABASE_URL with SQLite
            new_content = content.replace(
                "DATABASE_URL=postgresql://postgres:password@localhost:5432/peoplehub",
                "DATABASE_URL=sqlite:///peoplehub.db"
            )
            
            with open(env_path, 'w') as f:
                f.write(new_content)
            
            print("Updated .env file to use SQLite")
            print("Now run: python seed_data.py")
    else:
        print("\nPostgreSQL is ready! You can now run:")
        print("python seed_data.py")


if __name__ == "__main__":
    main()