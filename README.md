# LibraPro Library Management System

Django project with accounts, books, authors, publishers, categories, book copies, members, circulation, fines, reservations, notifications, payments and reports.

## What was corrected in this integration pass

- Added a default-deny login gate for application URLs; authentication, static/media and Django admin entry points remain reachable without a library session.
- Added safe handling of `next` during login so external websites cannot be used as open redirects.
- Connected the shared navigation to existing module URL names and added a CSRF-protected POST logout control.
- Replaced hard-coded email credentials and production secret/debug values with environment configuration. Local development uses console email if SMTP credentials are not configured.
- Added authentication integration tests for protected pages, login, unsafe redirects and POST-only logout.

## Setup (Windows)

1. Open Command Prompt in the folder containing `manage.py`.
2. Create/activate a virtual environment:

   ```bat
   py -3.8 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. For local testing, the default `DJANGO_DEBUG=1` behavior is enabled if the variable is absent. OTP email is printed to the terminal until SMTP credentials are configured.
4. Apply migrations and create an administrator:

   ```bat
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py check
   python manage.py test
   python manage.py runserver
   ```

5. Open `http://127.0.0.1:8000/accounts/login/`. Create an account, verify its OTP from the terminal (local console-email mode), or sign in using a superuser account.

## Production security

- Set a long random `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and correct `DJANGO_ALLOWED_HOSTS`.
- Configure SMTP environment variables for real OTP delivery.
- Serve behind HTTPS before enabling secure cookies/HSTS and SSL redirects. Review `python manage.py check --deploy` with the actual deployment settings.
- Do not commit `.env`, credentials, or the production database.

## Important testing note

The project archive did not include a runnable Linux-compatible Django environment. Python source syntax was checked after the edits, but `manage.py check` and the test suite still need to be run in the project's installed Windows virtual environment using the commands above. No claim is made that every workflow has been runtime-verified.
