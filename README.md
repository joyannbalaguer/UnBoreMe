# Flask Gaming Platform – UnBoreMe

UnBoreMe is a Flask web application that I developed as my final project.  
The goal of this project was to apply what I learned about web development, databases, security, and object-oriented programming by building a complete and working system.

This platform includes user authentication, an admin panel, a blog feature, and several browser-based games.

---

## Features

### Authentication System
- User registration with email OTP verification
  - OTP expires after 10 minutes
  - 5-minute resend cooldown
- Login system using session management
- Password reset functionality
- Passwords are securely hashed using Bcrypt
- Account activation and deactivation managed by admins

---

### User Dashboard
- Edit personal profile information
- Create, update, and delete personal blog posts
- Access games enabled by the admin
- View basic user statistics and activity

---

### Admin Panel
- User Management (CRUD)
  - Create, view, edit, and delete users
  - Activate or deactivate user accounts
- Game Management
  - Enable or disable games
  - Control which games are accessible to users
- Audit Logs
  - Track administrative actions for monitoring and security

---

### Blog System
- Create, read, update, and delete blog posts
- View all public posts
- Manage personal posts
- Supports formatted text content

---

### Games (Object-Oriented Design)

The platform includes 8 games implemented using object-oriented programming concepts:

1. Snake  
2. Pong  
3. Tetris  
4. Breakout  
5. Space Invaders  
6. Memory Match  
7. 2048  
8. Flappy Bird  

Each game:
- Uses object-oriented design
- Can be played directly in the browser
- Can be enabled or disabled by admins
- Tracks user high scores
- Global Leaderbourd

---

## Technology Stack

- Backend: Flask with Blueprint architecture
- Database: MySQL (via XAMPP / phpMyAdmin)
- Authentication: Flask-Bcrypt, session-based login
- Email: Flask-Mail (SMTP) for OTP verification
- Frontend: HTML, CSS, and JavaScript
- Templates: Jinja2
- Security: Server-side validation and password hashing

--http://127.0.0.1:5000

