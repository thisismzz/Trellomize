import os
import shutil
from unittest import TestCase, main
from unittest.mock import patch, Mock

from main import User, Project, Task


class TestMainClsUser(TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up a test user
        cls.user1 = User("user1@test.com", "user1test", "user1", ID="tester")

    @classmethod
    def tearDownClass(cls):
        # Clean up after testing by removing user data directory
        shutil.rmtree(f"users/user1test")

    def test_create_user(self):
        # Check if user attributes match expected values
        self.assertEqual(self.user1.email, 'user1@test.com')
        self.assertEqual(self.user1.username, 'user1test')
        self.assertEqual(self.user1.password, 'user1')

    def test_user_file_validation(self):
        # Save user data and check if file exists
        self.user1.save_user_data()
        expected_data_user1 = {"email": "user1@test.com", "username": "user1test", "password": "user1", "active": True, "ID": "tester"}
        self.assertTrue(os.path.exists(f"users/{self.user1.username}/{self.user1.username}.json"))
        # Check if loaded user data matches expected data
        self.assertEqual(expected_data_user1, User.load_user_data(self.user1.username))


class TestMainClsProject(TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up a test project
        cls.project1 = Project("project test1", "user1", collaborators=None, ID="tester")

    @classmethod
    def tearDownClass(cls):
        # Clean up after testing by removing project data file
        os.remove(f"projects/tester.json")

    def test_create_project(self):
        # Check if project attributes match expected values
        self.assertEqual(self.project1.title, "project test1")
        self.assertEqual(self.project1.owner, "user1")
        self.assertEqual(self.project1.collaborators, ["user1"])
        self.assertEqual(self.project1.ID, "tester")

    def test_project_file_validation(self):
        # Save project data and check if file exists
        self.project1.save_project_data()
        expected_data_project = {"title": "project test1", "owner": "user1", "tasks": {}, "collaborators": ["user1"], "ID": "tester"}
        self.assertTrue(os.path.exists("projects/tester.json"))
        # Check if loaded project data matches expected data
        self.assertEqual(expected_data_project, Project.load_project_data("tester"))

class TestMainClsTask(TestCase):

    def setUp(self):
        # Set up a test task
        self.task1 = Task("task1 test", "test No.1", ID="tester", start_time="2024-05-22 22:56:04", end_time="2024-05-23 22:56:04")

    def test_create_task(self):
        self.assertEqual(self.task1.title, "task1 test")
        self.assertEqual(self.task1.description, "test No.1")
        self.assertEqual(self.task1.ID, "tester")
        self.assertEqual(self.task1.start_time, "2024-05-22 22:56:04")
        self.assertEqual(self.task1.end_time, "2024-05-23 22:56:04")
        self.assertEqual(self.task1.priority, "LOW")
        self.assertEqual(self.task1.status, "BACKLOG")

    @patch("builtins.input", side_effect=["2024-05-22 22:56:04"])
    def test_change_end_time(self, mock_input):
        self.task1.change_end_time()
        self.assertEqual(self.task1.end_time, "2024-05-22 22:56:04")

    @patch("builtins.input", side_effect=["2024-05-22 22:56:04"])
    def test_change_start_time(self, mock_input):
        self.task1.change_start_time()
        self.assertEqual(self.task1.start_time, "2024-05-22 22:56:04")

    @patch("builtins.input", side_effect=["2"])
    def test_change_status(self, mock_input):
        self.task1.change_status()
        self.assertEqual(self.task1.status, "TODO")

    @patch("builtins.input", side_effect=["2"])
    def test_change_priority(self, mock_input):
        self.task1.change_priority()
        self.assertEqual(self.task1.priority, "HIGH")

    @patch("builtins.input", side_effect=["New Title"])
    def test_change_title(self, mock_input):
        self.task1.change_title()
        self.assertEqual(self.task1.title, "New Title")

    @patch("builtins.input", side_effect=["New Description"])
    def test_change_description(self, mock_input):
        self.task1.change_description()
        self.assertEqual(self.task1.description, "New Description")

    # Test using mock object
    def test_using_mock(self):
        mock_obj = Mock()
        mock_obj.method()
        mock_obj.method.assert_called_once()


if __name__ == '__main__':
    main()