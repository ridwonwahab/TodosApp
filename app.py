import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, url_for


MAX_TITLE_LENGTH = 200


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "TODO_DATABASE", str(Path("instance") / "todos.sqlite3")
        ),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error=None):
        database = g.pop("db", None)
        if database is not None:
            database.close()

    def initialize_database():
        with sqlite3.connect(app.config["DATABASE"]) as database:
            database.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                    completed INTEGER NOT NULL DEFAULT 0
                        CHECK(completed IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    initialize_database()

    def render_home(error=None, status=200):
        selected_filter = request.args.get("filter", "all")
        if selected_filter not in {"all", "active", "completed"}:
            selected_filter = "all"

        filters = {
            "all": "",
            "active": "WHERE completed = 0",
            "completed": "WHERE completed = 1",
        }
        database = get_db()
        todos = database.execute(
            f"SELECT id, title, completed FROM todos {filters[selected_filter]} "
            "ORDER BY completed ASC, id DESC"
        ).fetchall()
        counts = database.execute(
            """
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(completed = 0), 0) AS active,
                   COALESCE(SUM(completed = 1), 0) AS completed
            FROM todos
            """
        ).fetchone()
        return (
            render_template(
                "index.html",
                todos=todos,
                counts=counts,
                active_filter=selected_filter,
                error=error,
                max_title_length=MAX_TITLE_LENGTH,
            ),
            status,
        )

    @app.get("/")
    def index():
        return render_home()

    @app.post("/todos")
    def add_todo():
        title = request.form.get("title", "").strip()
        if not title:
            return render_home("Please enter a task before adding it.", 400)
        if len(title) > MAX_TITLE_LENGTH:
            return render_home(
                f"Tasks must be {MAX_TITLE_LENGTH} characters or fewer.", 400
            )

        database = get_db()
        with database:
            database.execute("INSERT INTO todos (title) VALUES (?)", (title,))
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/toggle")
    def toggle_todo(todo_id):
        database = get_db()
        with database:
            cursor = database.execute(
                """
                UPDATE todos
                SET completed = CASE completed WHEN 0 THEN 1 ELSE 0 END
                WHERE id = ?
                """,
                (todo_id,),
            )
        if cursor.rowcount == 0:
            abort(404)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/delete")
    def delete_todo(todo_id):
        database = get_db()
        with database:
            cursor = database.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            abort(404)
        return redirect(url_for("index"))

    @app.post("/todos/clear-completed")
    def clear_completed():
        database = get_db()
        with database:
            database.execute("DELETE FROM todos WHERE completed = 1")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
