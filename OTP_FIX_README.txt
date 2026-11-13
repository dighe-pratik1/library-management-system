LibraPro OTP / Registration Fix
================================

Updated files:
- accounts/views.py: registration keeps an inactive account when SMTP delivery fails; failed OTP sends clean up the unsent OTP record; logs detailed exception to the runserver terminal.
- config/settings.py: supports configurable SMTP timeout/TLS/SSL environment variables.

Local development (console email backend):
  python manage.py runserver
If SMTP credentials are not configured, the OTP is printed in the terminal running the server.

Gmail SMTP in Windows CMD (current terminal session only):
  set EMAIL_HOST_USER=your-email@gmail.com
  set EMAIL_HOST_PASSWORD=your-google-app-password
  set DEFAULT_FROM_EMAIL=your-email@gmail.com
  python manage.py runserver

Use a Google App Password, not your normal Gmail password. Never commit secrets to source control.

Test commands:
  python manage.py check
  python manage.py migrate
  python manage.py test

Note: run these commands in the directory containing manage.py. This archive's source-level Python syntax was checked, but run the Django commands in your own environment to verify installed dependencies and database state.
