from unittest import TestCase , main
from unittest.mock import patch , Mock
import bcrypt
import os
import shutil
from main import User , Project , Task

class TestMain_cls_User(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.user1 = User("user1@test.com" , "user1test" , "user1" , ID = "tester")
        # cls.user2 = User("user2@test.com" , "user2test" , "user2")
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(f"users/user1test")
        # shutil.rmtree(f"users/user2test")
    
    def test_create_user(self):
        self.assertEqual(self.user1.email , 'user1@test.com')
        self.assertEqual(self.user1.username , 'user1test')
        self.assertEqual(self.user1.password , 'user1')
        
    def test_user_file_validation(self):
        self.user1.save_user_data()
        expected_data_user1 ={"email": "user1@test.com","username": "user1test","password": "user1","active": True,"ID": "tester"}
        self.assertTrue(os.path.exists(f"users/{self.user1.username}/{self.user1.username}.json"))
        self.assertEqual(expected_data_user1 , User.load_user_data(self.user1.username))


class TestMain_cls_Project(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.project1 = Project("project test1" , "user1" , collaborators = None , ID = "tester")
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_create_project(self):
        self.assertEqual(self.project1.title, "project test1")
        self.assertEqual(self.project1.owner , "user1")
        self.assertEqual(self.project1.collaborators , ["user1"])
        self.assertEqual(self.project1.ID , "tester")

    def test_project_file_validation(self):
        self.project1.save_project_data()
        expected_data_project ={"title": "project test1","owner": "user1","tasks": {},"collaborators": ["user1"],"ID": "tester"}
        self.assertTrue(os.path.exists("projects/tester.json"))
        self.assertEqual(expected_data_project , Project.load_project_data("tester"))
        
    # def test_add_member(self):
    #     sample_user  = "sample user"
    #     self.project1.add_member(sample_user)
    #     self.assertIn(sample_user,self.project1.collaborators)
        
    # def test_remove_member(self):
    #     sample_user = "sample user"
    #     self.project1.collaborators.append(sample_user)
    #     with patch("builtins.input" , return_value = "sample user"):
    #         self.project1.remove_member(sample_user)
    # self.assertNotIn(sample_user , self.project1.collaborators)

class TestMain_cls_Task(TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.task1 = Task("task1 test" , "test No.1" , ID = "tester" , start_time="2024-05-22 22:56:04.092445" , end_time="2024-05-23 22:56:04.092445")
    
    def tearDown(self):
        pass
    
    def test_create_task(self):
        self.assertEqual(self.task1.title , "task1 test")
        self.assertEqual(self.task1.description , "test No.1")
        self.assertEqual(self.task1.ID , "tester")
        self.assertEqual(self.task1.start_time, "2024-05-22 22:56:04.092445")
        self.assertEqual(self.task1.end_time , "2024-05-23 22:56:04.092445")
        self.assertEqual(self.task1.priority , "LOW")
        self.assertEqual(self.task1.status , "BACKLOG")
        
    def test_change_end_time(self):
        pass
    
    def test_change_start_time(self):
        pass
    
    def test_change_status(self):
        pass
    
    def test_change_priority(self):
        pass
    
    def test_change_title(self):
        pass
    
    def test_change_description(self):
        pass
    
    def test_add_comment(self):
        pass
    
        
if __name__ == '__main__':
    main()