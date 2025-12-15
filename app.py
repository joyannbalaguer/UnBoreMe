"""
Flask Application Entry Point
Run this file to start the Flask development server
"""
from app import create_app
import os

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # Run the application
    print(f"\n{'='*60}")
    print(f"  UnBoreMe Server")
    print(f"{'='*60}")
    print(f"  Running on: http://{host}:{port}")
    print(f"  Debug Mode: {debug_mode}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug_mode)
