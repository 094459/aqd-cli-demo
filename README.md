# Customer Survey Application

A simple web application for creating and managing customer surveys.

## Features

- User registration and authentication
- Create custom surveys with multiple choice options
- Share surveys via unique links
- View and analyze survey results
- Track customer feedback

## Authentication Flow Diagrams

### User Registration Process

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant RegisterRoute as /register Route
    participant UserModel as User Model
    participant Database
    
    User->>Browser: Navigate to registration page
    Browser->>RegisterRoute: GET /register
    RegisterRoute->>Browser: Return registration form
    
    User->>Browser: Fill in email and password
    Browser->>RegisterRoute: POST /register with form data
    
    RegisterRoute->>RegisterRoute: Validate form data
    alt Invalid form data
        RegisterRoute->>Browser: Return form with error messages
        Browser->>User: Display validation errors
    else Valid form data
        RegisterRoute->>UserModel: Check if email exists
        UserModel->>Database: Query for existing user
        Database->>UserModel: Return result
        
        alt Email already exists
            UserModel->>RegisterRoute: User already exists
            RegisterRoute->>Browser: Return form with error message
            Browser->>User: Display "Email already registered"
        else Email available
            RegisterRoute->>UserModel: Create new user
            UserModel->>UserModel: Hash password
            UserModel->>Database: Save new user
            Database->>UserModel: Confirm save
            UserModel->>RegisterRoute: User created
            RegisterRoute->>Browser: Redirect to login page with success message
            Browser->>User: Display success message and login form
        end
    end
```

### User Login Process

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant LoginRoute as /login Route
    participant UserModel as User Model
    participant Database
    participant FlaskLogin as Flask-Login
    participant Dashboard as /dashboard Route
    
    User->>Browser: Navigate to login page
    Browser->>LoginRoute: GET /login
    LoginRoute->>Browser: Return login form
    
    User->>Browser: Enter email and password
    Browser->>LoginRoute: POST /login with credentials
    
    LoginRoute->>UserModel: Find user by email
    UserModel->>Database: Query for user
    Database->>UserModel: Return user data
    
    alt User not found
        UserModel->>LoginRoute: User not found
        LoginRoute->>Browser: Return form with error message
        Browser->>User: Display "Invalid email or password"
    else User found
        UserModel->>UserModel: Check password hash
        
        alt Invalid password
            UserModel->>LoginRoute: Invalid password
            LoginRoute->>Browser: Return form with error message
            Browser->>User: Display "Invalid email or password"
        else Valid password
            UserModel->>LoginRoute: Authentication successful
            LoginRoute->>UserModel: Update last login timestamp
            UserModel->>Database: Save updated timestamp
            
            LoginRoute->>FlaskLogin: Log in user (login_user)
            FlaskLogin->>FlaskLogin: Create user session
            
            alt Remember me checked
                FlaskLogin->>Browser: Set long-term session cookie
            else Remember me not checked
                FlaskLogin->>Browser: Set session cookie
            end
            
            LoginRoute->>Browser: Redirect to dashboard
            Browser->>Dashboard: GET /dashboard
            Dashboard->>Database: Query user's surveys
            Database->>Dashboard: Return survey data
            Dashboard->>Browser: Return dashboard view
            Browser->>User: Display dashboard with surveys
        end
    end
```

## Project Structure

```
src/
├── static/          # Static assets (CSS, JS, images)
├── models/          # Database models
├── routes/          # Route handlers
├── templates/       # HTML templates
├── extensions.py    # Flask extensions
├── app.py           # Application factory
```

## Database Schema

The application uses the following database tables:
- Users: Store user information
- Surveys: Store survey information
- Survey_Options: Store survey options
- Survey_Responses: Store survey responses

For a detailed ERD, see [data-model.md](data-model.md).

## Installation

1. Clone the repository
2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set environment variables (optional):
   ```
   export SECRET_KEY=your_secret_key
   export DATABASE_URL=sqlite:///survey_app.db
   ```

## Running the Application

### Development Mode

```
python run.py
```

The application will be available at http://127.0.0.1:5000/

### Production Mode with Gunicorn

```
gunicorn -c gunicorn_config.py wsgi:app
```

The application will be available at http://0.0.0.0:8000/

### Using Containers

#### Local Development

Build and run the container:

```
# Build the container image with a specific version
./build-container.sh 1.0.0

# Run with Finch
finch run -p 8000:8000 customer-survey-app:1.0.0
```

Or using Docker Compose:

```
finch compose up
```

#### Using Pre-built Images

Pull and run the pre-built container images from GitHub Container Registry:

```
# Pull the latest image
finch pull ghcr.io/username/customer-survey-app:latest

# Run the container
finch run -p 8000:8000 ghcr.io/username/customer-survey-app:latest
```

The application will be available at http://localhost:8000/

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and delivery:

1. **Container Builds**: Container images are built for both AMD64 and ARM64 architectures
2. **Automatic Deployment**: Tagged releases are automatically pushed to GitHub Container Registry

## Usage

1. Register a new account
2. Log in with your credentials
3. Create a new survey from the dashboard
4. Share the survey link with your customers
5. View results as responses come in

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/my-new-feature`
5. Submit a pull request
