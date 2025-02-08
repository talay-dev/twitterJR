
# TwitterJR

TwitterJR is a simplified version of Twitter built using Flask. It allows users to register, login, write tweets, view a feed of tweets, like tweets, and edit their profile.

## Features

- User registration and login
- Write and view tweets
- Like tweets
- Edit user profile
- Dark mode support

## Setup Instructions

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/talay-dev/twitterJR.git
    cd twitterJR
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:

    ```bash
    python init_db.py
    ```

5. Run the application:

    ```bash
    python app.py
    ```

6. Open your browser and navigate to `http://127.0.0.1:5000`.

## Project Structure

- `app.py`: Main application file containing routes and logic.
- `init_db.py`: Script to initialize the database.
- `templates/`: Directory containing HTML templates.
- `static/`: Directory containing static files (CSS, JavaScript, images).
- `requirements.txt`: List of Python packages required for the project.

## Usage

### User Registration

1. Navigate to the Register page.
2. Fill in the username and password fields.
3. Click the Register button.

### User Login

1. Navigate to the Login page.
2. Fill in the username and password fields.
3. Click the Login button.

### Writing a Tweet

1. Navigate to the Write Tweet page.
2. Enter your tweet content (up to 280 characters).
3. Click the Tweet button.

### Viewing the Feed

1. Navigate to the Feed page.
2. View tweets from all users.

### Liking a Tweet

1. Click the heart icon on a tweet to like it.
2. Click again to unlike.

### Editing Profile

1. Navigate to the Profile page.
2. Click the Edit Profile button.
3. Update your bio and/or profile picture.
4. Click the Save Changes button.

## Dark Mode

- Toggle dark mode using the moon/sun icon in the navigation bar.
- The theme preference is saved in local storage.

## License

This project is licensed under the MIT License.
