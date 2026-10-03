# Daymark Todo

A small, responsive todo app built with Python and Flask. It uses SQLite for local development and can use PostgreSQL when deployed.

## Run it

You need Python 3.9 or newer.

1. Open a terminal in this project folder.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the app dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Start the app:

   ```powershell
   py app.py
   ```

5. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The first run creates `instance/todos.sqlite3` for the task list. The page works on desktop and mobile; adding, completing, filtering, and deleting tasks all work with regular HTML forms.

## Deploy to Vercel

Vercel's serverless filesystem is temporary, so use a hosted PostgreSQL database for tasks that should persist. Create a PostgreSQL database using a Vercel Marketplace provider such as Neon, then connect it to the Vercel project. Make sure the project has a `DATABASE_URL` environment variable containing the PostgreSQL connection string. The app creates its `todos` table automatically when it starts. Without `DATABASE_URL`, the app uses local SQLite for development and a temporary SQLite file on Vercel; tasks saved to that temporary file are not durable.

This starter app is a shared list: anyone with its public URL can view, add, complete, or delete tasks. Do not use it for private information.

## Run the tests

```powershell
py -m unittest discover -s tests
```

## Project files

- `app.py` — Flask routes and SQLite/PostgreSQL database setup.
- `templates/index.html` — the page structure and task forms.
- `static/style.css` — responsive layout and visual styles.
- `tests/test_app.py` — tests for the main todo workflows.
