# UnBoreMe – Flask Gaming Platform

UnBoreMe is a full-stack Flask web application developed as an academic project by a 2nd-year Information Technology student.  
The goal of this project was to apply concepts from web development, backend systems, databases, security, and object-oriented programming by building a complete, data-driven platform.

The application combines user management, content features, and multiple games into a single system where all activity is centrally tracked and managed.

This project was built iteratively while learning Flask, backend architecture, and database-driven systems.

---

## Key Features

### Authentication & Security
- User registration with email OTP verification  
  - OTP expires after 10 minutes  
  - 5-minute resend cooldown  
- Session-based login system  
- Password reset functionality  
- Passwords securely hashed using bcrypt  
- Admin-controlled account activation and deactivation  

---

### User Dashboard
- Edit personal profile information  
- Create, update, and delete personal blog posts  
- Access games enabled by administrators  
- View personal activity and statistics  
- Track individual and global game scores  

---

### Admin Panel
- User management (CRUD)
  - Create, view, edit, and delete users  
  - Activate or deactivate user accounts  
- Game management
  - Enable or disable games globally  
  - Control which games are accessible to users  
- Audit logs
  - Track administrative actions for monitoring and security  

---

### Blog System
- Create, read, update, and delete blog posts  
- View all public posts  
- Manage personal posts  
- Supports formatted text content  

---

### Games & Global Leaderboards

The platform integrates multiple games directly into the system.  
All games are connected to the backend and database, allowing scores to be stored, tracked, and displayed globally.

**Included games:**
1. Snake  
2. Pong  
3. Tetris  
4. Breakout  
5. Space Invaders  
6. Memory Match  
7. 2048  
8. Flappy Bird  

Each game:
- Uses object-oriented programming principles  
- Is integrated with user accounts  
- Stores scores in the database  
- Appears in a global leaderboard  
- Can be enabled or disabled by administrators  

---

## Database Design
The application uses a relational MySQL database to manage users, authentication data, blog posts, games, scores, and audit logs.  
Core tables include users, otp_tokens, posts, games, game_scores, user_games, and audit_logs to support dashboards and global statistics.

---

## System Architecture Overview
- Modular Flask application using Blueprint architecture  
- Clear separation of concerns (authentication, admin, games, blog)  
- Centralized access control using custom decorators  
- Database-driven dashboards and leaderboards  
- Server-side validation and secure session handling  

---

## Technology Stack
- Backend: Flask (Blueprint architecture)  
- Database: MySQL (XAMPP / phpMyAdmin)  
- Authentication: Flask-Bcrypt, session-based login  
- Email: Flask-Mail (SMTP) for OTP verification  
- Frontend: HTML, CSS, JavaScript  
- Templates: Jinja2  
- Security: Server-side validation and password hashing  

## Author

Joy Ann Balaguer
