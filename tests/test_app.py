import os
import sqlite3
import tempfile
import unittest
from contextlib import closing

from app import create_app


class TodoAppTests(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile(delete=False)
        self.database_file.close()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.database_file.name,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.database_file.name)

    def test_home_shows_empty_state(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"A fresh start", response.data)

    def test_add_and_display_task(self):
        response = self.client.post(
            "/todos", data={"title": "  Read a chapter  "}, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Read a chapter", response.data)
        self.assertNotIn(b"  Read a chapter  ", response.data)

    def test_rejects_empty_and_overlong_tasks(self):
        empty_response = self.client.post("/todos", data={"title": "   "})
        long_response = self.client.post("/todos", data={"title": "x" * 201})

        self.assertEqual(empty_response.status_code, 400)
        self.assertIn(b"Please enter a task", empty_response.data)
        self.assertEqual(long_response.status_code, 400)
        self.assertIn(b"200 characters or fewer", long_response.data)

    def test_can_complete_filter_and_clear_task(self):
        self.client.post("/todos", data={"title": "Take a walk"})
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as connection:
            todo_id = connection.execute("SELECT id FROM todos").fetchone()[0]

        self.client.post(f"/todos/{todo_id}/toggle")
        completed = self.client.get("/?filter=completed")
        active = self.client.get("/?filter=active")

        self.assertIn(b"Take a walk", completed.data)
        self.assertIn(b"All done for now", active.data)

        self.client.post("/todos/clear-completed")
        self.assertIn(b"A fresh start", self.client.get("/").data)

    def test_can_delete_task(self):
        self.client.post("/todos", data={"title": "Water the plants"})
        with closing(sqlite3.connect(self.app.config["DATABASE"])) as connection:
            todo_id = connection.execute("SELECT id FROM todos").fetchone()[0]

        response = self.client.post(f"/todos/{todo_id}/delete", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Water the plants", response.data)

    def test_unknown_task_returns_not_found(self):
        response = self.client.post("/todos/999/toggle")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
