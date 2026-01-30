import os
import shutil
import sys
import unittest

# Ensure src is in python path
sys.path.append(os.getcwd())

from src.core.session_manager import SessionManager
from src.models.dungeon import SessionModule, RoomNode

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.test_session_dir = "data/test_sessions"
        if os.path.exists(self.test_session_dir):
            shutil.rmtree(self.test_session_dir)
        self.manager = SessionManager(session_dir=self.test_session_dir)

    def tearDown(self):
        if os.path.exists(self.test_session_dir):
            shutil.rmtree(self.test_session_dir)

    def test_create_default_session(self):
        session_id = "test_default"
        session = self.manager.load_session(session_id)

        # Verify file creation
        self.assertTrue(os.path.exists(os.path.join(self.test_session_dir, f"{session_id}.json")))

        # Verify session content
        self.assertEqual(session.session_id, session_id)
        self.assertIn("room_01", session.rooms)
        self.assertEqual(session.rooms["room_01"].title, "Damp Crypt")
        self.assertEqual(len(session.rooms["room_01"].entities), 1)
        self.assertEqual(session.rooms["room_01"].entities[0].name, "goblin_01")

    def test_save_and_load_session(self):
        session_id = "test_save_load"
        session = self.manager.create_default_session(session_id)

        # Modify session
        session.rooms["room_01"].is_visited = True
        self.manager.save_session(session)

        # Reload
        loaded_session = self.manager.load_session(session_id)
        self.assertTrue(loaded_session.rooms["room_01"].is_visited)

if __name__ == "__main__":
    unittest.main()
