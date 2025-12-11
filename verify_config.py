"""
Verify Flask app configuration is loading correctly
"""
from app import create_app

app = create_app()

print("=" * 60)
print("FLASK APP CONFIGURATION VERIFICATION")
print("=" * 60)
print(f"DB_HOST: {app.config['DB_HOST']}")
print(f"DB_PORT: {app.config['DB_PORT']}")
print(f"DB_USER: {app.config['DB_USER']}")
print(f"DB_PASSWORD: {'<empty>' if not app.config['DB_PASSWORD'] else '<set>'}")
print(f"DB_NAME: {app.config['DB_NAME']}")
print("=" * 60)

if app.config['DB_NAME'] == 'final_project':
    print("✓ Configuration is correct - using 'final_project' database")
else:
    print(f"✗ Configuration is WRONG - using '{app.config['DB_NAME']}' instead of 'final_project'")
    print("\nThis means the app may be:")
    print("  1. Not reloading .env properly")
    print("  2. Using cached Python modules")
    print("  3. Still running with old configuration")

print("=" * 60)
