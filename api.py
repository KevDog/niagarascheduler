#!/usr/bin/env python
"""
Flask API server for Niagara University Syllabus Generator

This is the main entry point for the modular Flask API.
The application is built using the factory pattern with blueprints
for clean separation of concerns.
"""
import os
import sys
from api import create_app

def main():
    """Main entry point for the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Niagara University Scheduler API Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run in development mode on port 5000
  %(prog)s --port 8000              # Run on port 8000
  %(prog)s --env production         # Run in production mode
  %(prog)s --env production -p 8080 # Production mode on port 8080
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=int(os.environ.get('PORT', 5000)),
        help='Port to run the API server on (default: 5000, or PORT env var)'
    )
    
    parser.add_argument(
        '--env',
        choices=['development', 'production', 'testing'],
        default=os.environ.get('FLASK_ENV', 'development'),
        help='Environment configuration (default: development, or FLASK_ENV env var)'
    )
    
    parser.add_argument(
        '--host',
        default=os.environ.get('HOST', '0.0.0.0'),
        help='Host to bind the server to (default: 0.0.0.0, or HOST env var)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Force debug mode (overrides environment setting)'
    )
    
    args = parser.parse_args()
    
    # Create application
    try:
        app = create_app(args.env)
        
        # Override debug if specified
        if args.debug:
            app.config['DEBUG'] = True
        
        print(f"🚀 Starting Niagara University Scheduler API")
        print(f"   Environment: {args.env}")
        print(f"   Host: {args.host}")
        print(f"   Port: {args.port}")
        print(f"   Debug: {app.config['DEBUG']}")
        print(f"   Data Directory: {app.config['DATA_DIR']}")
        print(f"   Template Directory: {app.config['TEMPLATE_DIR']}")
        
        if args.env == 'development':
            print(f"   Frontend Proxy: Vue dev server should proxy API requests")
            print(f"   Health Check: http://{args.host}:{args.port}/api/health")
        
        print(f"\n📚 API Documentation endpoints:")
        print(f"   GET  /api/health           - Health check")
        print(f"   GET  /api/config           - Application configuration") 
        print(f"   GET  /api/departments      - List all departments")
        print(f"   GET  /api/departments/{{id}} - Get specific department")
        print(f"   GET  /api/courses/{{id}}     - Get specific course")
        print(f"   GET  /api/offerings/...    - Get course offerings")
        print(f"   POST /api/generate-schedule - Generate class schedule")
        print(f"   POST /api/generate-syllabus - Generate syllabus content")
        print(f"   POST /api/export-syllabus  - Export syllabus file")
        
        # Run the application
        app.run(
            host=args.host,
            port=args.port,
            debug=app.config['DEBUG'],
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start API server: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()