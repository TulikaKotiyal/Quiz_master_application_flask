# Quiz Master – Flask-based Multi-user Quiz Application

## Overview
**Quiz Master** is a multi-user Flask-based web application where:
- **Admin (Superuser)** manages subjects, chapters, and quizzes.
- **Registered Users** attempt quizzes and view their scores.  

The application focuses on:
- **Role-based access control**
- **Quiz creation and management**
- **User performance analytics**
- **Score tracking with dashboards**

Built with:
- **Flask** for backend
- **SQLite** for database
- **Bootstrap** for responsive UI

---

## Features

### Admin (Superuser)
- Create, edit, and delete:
  - Subjects
  - Chapters
  - Multiple Choice Questions (MCQs)
- Manage registered users
- View analytics and quiz performance

### Users
- Attempt **timed quizzes**
- View scores and results
- Track past performance

---

## Frameworks & Libraries Used
- **Flask** – Web framework
- **Jinja2** – Templating and HTML generation
- **Flask-SQLAlchemy** & **sqlite3** – Database operations
- **HTML/CSS** – Structure and styling
- **Flask-Login** / **Flask-Security** – Authentication & user session management
- **JavaScript** – Frontend validation and interactivity

---

## Database Schema
The database schema includes tables for:
- **Users**
- **Scores**
- **Quizzes**
- **Subjects**
- **Chapters**
- **Questions**

**Relationships:**
- Foreign keys (e.g., `quiz_id` in `Question`) link entities.
- `is_admin` flag in `Users` table defines admin privileges.
- Supports CRUD operations for quizzes, users, and analytics.

---

## API Endpoints

| Endpoint | Method(s) | Function | Description |
|----------|-----------|----------|-------------|
| `/login` | GET, POST | User Login | Authenticates user credentials and redirects to dashboard based on role. |
| `/register` | GET, POST | User Registration | Allows new user creation with details like username, email, password, etc. |
| `/quiz/<int:quiz_id>` | GET, POST | Attempt Quiz | Displays quiz (GET) and processes answers, calculates score (POST). |
| `/quiz/<int:quiz_id>/results` | GET | Quiz Results | Shows latest score for the given quiz attempt. |
| `/users` | GET | Manage Users | Admin-only, lists and searches non-admin users. |
| `/subjects` | GET, POST | Manage Subjects | Admin-only, add new subjects and view existing ones. |

---

## Project Structure

Quiz_Master/
│
├── instance/         # Stores configuration & SQLite database (quiz_master.db)
├── static/           # CSS, JavaScript, images
├── templates/        # Jinja2 HTML templates
│
├── config.py         # Flask configuration (SECRET_KEY, DB URI, etc.)
├── database.py       # Database setup & SQLAlchemy initialization
├── forms.py          # WTForms classes
├── main.py           # Application entry point
├── routes.py         # Route definitions & view functions


---

## Architecture
1. **Instance folder** – Stores database and config files.
2. **Static folder** – Holds CSS, JS, images.
3. **Templates folder** – HTML files using Jinja2 templating.
4. **Configuration files** – `config.py` for settings.
5. **Database initialization** – `database.py` connects to SQLite.
6. **Forms handling** – `forms.py` for managing form validation.
7. **Main app** – `main.py` starts the application.
8. **Routes** – `routes.py` for defining URL endpoints.

---

## How to Run Locally
```bash
# Clone the repository
git clone https://github.com/yourusername/Quiz_master_application_flask.git

# Navigate to project folder
cd Quiz_master_application_flask

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
flask run
```
