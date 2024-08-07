# Exile

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/exile/static/images/exile/dark.svg">
  <img alt="Exile logo" src="/exile/static/images/exile/light.svg">
</picture>

Exile is a URL shortener with tracking features. Built with a modern stack including Flask, SQLAlchemy, Postgres, HTMX,
AlpineJS, PicoCSS, and ChartJS, it provides a sleek and efficient user experience.

## Features

- Shorten long URLs for easy sharing
- Track clicks and user interaction
- User-friendly interface with real-time updates
- Analytics dashboard to monitor link performance

## Stack

- **Backend**: Flask, SQLAlchemy, Postgres
- **Frontend**: HTMX, AlpineJS, PicoCSS, ChartJS

## Setup

### Prerequisites

- Python 3.8+
- Postgres database (if not using SQLite)
- Node.js and npm (for frontend assets, if necessary)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/pyrovetis/exile.git
    cd exile
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the environment variables:**

   Copy the `.env-sample` file to `.env` and fill in the necessary configuration.

    ```bash
    cp .env-sample .env
    ```

   **`.env-sample` content:**

    ```ini
    # [Flask]
    SECRET_KEY=

    # [Database]
    #DATABASE_URL=

    # [Mail]
    #MAIL_SERVER=
    #MAIL_PORT=465
    #MAIL_USE_TLS=1
    #MAIL_USE_SSL=1
    #MAIL_USERNAME=
    #MAIL_PASSWORD=
    ```

    - Remove the `#` from the beginning of a line to enable that setting.
    - If `DATABASE_URL` is not provided, the app will default to using a SQLite database (`app.db`).

5. **Initialize the database:**

    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

6. **Run the application:**

    ```bash
    flask run
    ```

   The app will be available at `http://127.0.0.1:5000`.

### Configuration

Configuration settings are managed via environment variables. The `.env` file should be used to set these variables.

- **SECRET_KEY**: A secret key for session management and CSRF protection.
- **DATABASE_URL**: The database connection URL. If not set, defaults to SQLite (`app.db`).
- **MAIL_SERVER**: SMTP server for sending emails.
- **MAIL_PORT**: SMTP server port.
- **MAIL_USE_TLS**: Use TLS for secure email transport.
- **MAIL_USE_SSL**: Use SSL for secure email transport.
- **MAIL_USERNAME**: Email account username.
- **MAIL_PASSWORD**: Email account password.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
