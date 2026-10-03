# Daymark Todo

A small, responsive todo app built with Python, Flask, and SQLite. Tasks are saved in a local database, so they are still there the next time you start the app.

## Run it

You need Python 3.9 or newer.

1. Open a terminal in this project folder.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install Flask:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Start the app:

   ```powershell
   py app.py
   ```

5. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The first run creates `instance/todos.sqlite3` for the task list. The page works on desktop and mobile; adding, completing, filtering, and deleting tasks all work with regular HTML forms.

## Run the tests

```powershell
py -m unittest discover -s tests
```

## Project files

- `app.py` — Flask routes and SQLite database setup.
- `templates/index.html` — the page structure and task forms.
- `static/style.css` — responsive layout and visual styles.
- `tests/test_app.py` — tests for the main todo workflows.
