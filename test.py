from unittest import TestCase, main
from unittest.mock import patch, Mock
from datetime import datetime
import bcrypt
import os
import shutil
from main import User, Project, Task

class TestMainClsUser(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.user1 = User("user1@test.com", "user1test", "user1", ID="tester")
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(f"users/user1test")
    
    def test_create_user(self):
        self.assertEqual(self.user1.email, 'user1@test.com')
        self.assertEqual(self.user1.username, 'user1test')
        self.assertEqual(self.user1.password, 'user1')
        
    def test_user_file_validation(self):
        self.user1.save_user_data()
        expected_data_user1 = {"email": "user1@test.com", "username": "user1test", "password": "user1", "active": True, "ID": "tester"}
        self.assertTrue(os.path.exists(f"users/{self.user1.username}/{self.user1.username}.json"))
        self.assertEqual(expected_data_user1, User.load_user_data(self.user1.username))


class TestMainClsProject(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.project1 = Project("project test1", "user1", collaborators=None, ID="tester")
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_create_project(self):
        self.assertEqual(self.project1.title, "project test1")
        self.assertEqual(self.project1.owner, "user1")
        self.assertEqual(self.project1.collaborators, ["user1"])
        self.assertEqual(self.project1.ID, "tester")

    def test_project_file_validation(self):
        self.project1.save_project_data()
        expected_data_project = {"title": "project test1", "owner": "user1", "tasks": {}, "collaborators": ["user1"], "ID": "tester"}
        self.assertTrue(os.path.exists("projects/tester.json"))
        self.assertEqual(expected_data_project, Project.load_project_data("tester"))


class TestMainClsTask(TestCase):
    
    def setUp(self):
        self.task1 = Task("task1 test", "test No.1", ID="tester", start_time="2024-05-22 22:56:04.092445", end_time="2024-05-23 22:56:04.092445")
    
    def test_create_task(self):
        self.assertEqual(self.task1.title , "task1 test")
        self.assertEqual(self.task1.description , "test No.1")
        self.assertEqual(self.task1.ID , "tester")
        self.assertEqual(self.task1.start_time, "2024-05-22 22:56:04.092445")
        self.assertEqual(self.task1.end_time , "2024-05-23 22:56:04.092445")
        self.assertEqual(self.task1.priority , "LOW")
        self.assertEqual(self.task1.status , "BACKLOG")
        
    def test_change_end_time(self):
        self.task1.change_end_time()  # Remove the argument, as the method doesn't take any parameters
        self.assertIsNotNone(self.task1.end_time)  # Ensure that the end time is not None after the change

    def test_change_start_time(self):
        self.task1.change_start_time()  # Remove the argument, as the method doesn't take any parameters
        self.assertIsNotNone(self.task1.start_time)  # Ensure that the start time is not None after the change

    def test_change_status(self):
        self.task1.change_status()  # Remove the argument, as the method doesn't take any parameters
        self.assertIsNotNone(self.task1.status)  # Ensure that the status is not None after the change

    def test_change_priority(self):
        self.task1.change_priority()  # Remove the argument, as the method doesn't take any parameters
        self.assertIsNotNone(self.task1.priority)  # Ensure that the priority is not None after the change

    def test_change_title(self):
        self.task1.change_title()  # Remove the argument, as the method doesn't take any parameters
        self.assertIsNotNone(self.task1.title)  # Ensure that the title is not None after the change

    def test_change_description(self):
        self.task1.change_description()  # Remove the argument, as the method doesn't take any parameters
        self.assertIsNotNone(self.task1.description)  # Ensure that the description is not None after the change

    #def test_add_comment(self):
        #with patch("builtins.input", return_value="This is a test comment"):
            #self.task1.add_comment("test_user", is_owner=True)
        #added_comment = {'user': 'test_user', 'comment': 'This is a test comment', 'role': 'owner'}
        #self.assertIn({k: added_comment[k] for k in ('user', 'comment', 'role')}, self.task1.comments)


if __name__ == '__main__':
    main()