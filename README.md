# Flask Gaming Platform

A full-featured Flask web application with user authentication, admin controls, blog functionality, and 8 unique OOP-based games.

## Features

### Authentication System
- **User Registration** with email OTP verification
  - 10-minute OTP expiry
  - 5-minute resend cooldown
- **Login System** with session management
- **Password Reset** functionality
- **Bcrypt** password hashing for security
- **Account Activation/Deactivation** by admins

### User Dashboard
- Profile management and editing
- Personal blog post creation and management (CRUD operations)
- Access to enabled games
- User statistics and activity tracking

### Admin Panel
- **User Management** (CRUD operations)
  - Create, view, edit, and delete users
  - Activate/deactivate user accounts
  - View user details and activity
- **Game Management**
  - Enable/disable individual games
  - Control which games are available to users
- **Audit Logs**
  - Track all administrative actions
  - Monitor system changes

### Blog System
- Create, read, update, and delete blog posts
- View all public posts
- Manage personal posts
- Rich text content support

### 8 Unique OOP Games
1. **Snake** - Classic snake game with modern controls
2. **Pong** - Two-player paddle game
3. **Tetris** - Block-stacking puzzle game
4. **Breakout** - Brick-breaking arcade game
5. **Space Invaders** - Retro alien shooter
6. **Memory Match** - Card matching puzzle game
7. **2048** - Number sliding puzzle game
8. **Flappy Bird** - Side-scrolling obstacle game

Each game is:
- Object-oriented design
- Fully playable in the browser
- Can be enabled/disabled by admins
- Tracks user high scores

## Technology Stack

- **Backend**: Flask 3.0.0 with Blueprints architecture
- **Database**: MySQL (compatible with phpMyAdmin)
- **Authentication**: Flask-Bcrypt, session-based auth
- **Email**: Flask-Mail for OTP verification
- **Frontend**: HTML5, CSS3, JavaScript (Canvas API for games)
- **Security**: WTForms, CSRF protection, password hashing

## Project Structure

```
finalproject/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection
│   ├── extensions.py            # Flask extensions
│   ├── models.py                # Database models
│   ├── routes.py                # Main routes
│   ├── admin/                   # Admin blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── auth/                    # Authentication blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── blog/                    # Blog blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── dashboard/               # User dashboard blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── games/                   # Games blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/                   # Utility modules
│       ├── decorators.py        # Custom decorators
│       └── email_sender.py      # Email functionality
├── static/
│   ├── css/
│   │   └── style.css            # Main stylesheet
│   ├── js/
│   │   └── main.js              # Shared JavaScript
│   └── games/                   # Game assets
│       ├── snake/
│       ├── pong/
│       ├── tetris/
│       ├── breakout/
│       ├── spaceinvaders/
│       ├── memorymatch/
│       ├── 2048/
│       └── flappybird/
├── templates/                   # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── admin/
│   ├── auth/
│   ├── blog/
│   ├── dashboard/
│   └── games/
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── database.sql                 # MySQL database schema
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7+ or MariaDB
- Git (optional, for cloning)
- phpMyAdmin (optional, for database management)

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd finalproject

# Or download and extract the ZIP file, then navigate to the project directory
```

### Step 2: Create Virtual Environment

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
# Ensure pip is up to date
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Set Up Database

1. **Create MySQL Database:**
   - Open phpMyAdmin or MySQL command line
   - Create a new database (e.g., `flask_gaming_db`)
   
   ```sql
   CREATE DATABASE flask_gaming_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Import Database Schema:**
   - In phpMyAdmin: Import the `database.sql` file
   - Or via command line:
   
   ```bash
   mysql -u root -p flask_gaming_db < database.sql
   ```

### Step 5: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. **Edit `.env` file with your settings:**
   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-here-change-this-to-something-random
   FLASK_ENV=development
   FLASK_DEBUG=True
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_NAME=flask_gaming_db
   
   # Email Configuration (for OTP)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

3. **Important Notes:**
   - Change `SECRET_KEY` to a random string for production
   - For Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833?hl=en), not your regular password
   - Enable "Less secure app access" or use OAuth2 for email

### Step 6: Run the Application

```bash
# Make sure virtual environment is activated (you should see (venv) in prompt)
# Run the application
python run.py
```

Or alternatively:
```bash
flask run
```

The application will start at: **http://127.0.0.1:5000**

### Step 7: Access the Application

1. **Open your browser** and navigate to `http://127.0.0.1:5000`
2. **Register a new account** (you'll receive an OTP via email)
3. **Verify your email** with the OTP code
4. **Login** and explore the platform!

### Step 8: Create Admin Account

To access admin features, you need to manually set a user as admin in the database:

```sql
-- Find your user ID
SELECT id, username, email FROM users;

-- Set user as admin (replace 1 with your user ID)
UPDATE users SET is_admin = 1 WHERE id = 1;
```

Then logout and login again to access the admin panel at `http://127.0.0.1:5000/admin`

## Default Admin Credentials

If the database import created a default admin user:
- **Username**: admin
- **Password**: Admin@123

**⚠️ IMPORTANT: Change the default admin password immediately after first login!**

## Usage Guide

### For Regular Users

1. **Register**: Create an account with email verification
2. **Dashboard**: Access your personal dashboard
3. **Profile**: Edit your profile information
4. **Blog**: Create and manage your blog posts
5. **Games**: Play any games enabled by the admin
6. **View Posts**: Browse all public blog posts

### For Administrators

1. **User Management**:
   - View all users
   - Create new users
   - Edit user details
   - Activate/deactivate accounts
   - Delete users

2. **Game Management**:
   - Enable/disable games system-wide
   - Control which games users can access

3. **Audit Logs**:
   - Monitor all administrative actions
   - Track system changes

## Deactivating Virtual Environment

When you're done working on the project:

```bash
deactivate
```

## Troubleshooting

### Database Connection Issues

**Error: "Access denied for user"**
- Check your database credentials in `.env`
- Ensure MySQL service is running
- Verify user has proper permissions

**Error: "Unknown database"**
- Make sure you created the database
- Check database name in `.env` matches created database

### Email Issues

**OTP emails not sending:**
- Verify SMTP settings in `.env`
- For Gmail: Use App Password, not regular password
- Check firewall/antivirus isn't blocking port 587
- Enable "Less secure app access" in Google account settings

### Port Already in Use

**Error: "Address already in use"**
```bash
# Change port in .env file
FLASK_PORT=5001

# Or kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

### Import Errors

**Error: "No module named 'flask'"**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### Static Files Not Loading

- Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
- Check file paths in templates
- Ensure `static` folder has proper permissions

## Development

### Running Tests

```bash
pytest
pytest --cov=app tests/
```

### Database Migrations

If you modify database models:
```bash
# Backup your database first!
mysqldump -u root -p flask_gaming_db > backup.sql

# Then update your database.sql file
# And re-import it
```

### Adding New Games

1. Create game folder in `static/games/your_game/`
2. Create JavaScript file with OOP structure
3. Add game template in `templates/games/your_game.html`
4. Update database with new game entry
5. Add route in `app/games/routes.py`

## Security Considerations

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Keep dependencies updated: `pip install --upgrade -r requirements.txt`
- Use HTTPS in production
- Implement rate limiting for login attempts
- Regular database backups
- Monitor audit logs for suspicious activity

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in `.env`
2. Set `FLASK_DEBUG=False`
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up reverse proxy (Nginx, Apache)
5. Use a proper secret key
6. Enable HTTPS/SSL
7. Set up automated backups
8. Configure proper logging

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Modify and use as needed.

## Support

For issues or questions:
- Check the Troubleshooting section
- Review error logs in the console
- Check database connectivity
- Verify all dependencies are installed

## Credits

Developed as a comprehensive Flask learning project featuring:
- Modern web application architecture
- Secure authentication system
- Admin panel with audit trail
- Blog functionality
- 8 unique browser-based games

---
