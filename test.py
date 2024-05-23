import unittest
import bcrypt
import os
import shutil
from main import User , Project , Task

class TestMain_cls_User(unittest.TestCase):
    
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


class TestMain_cls_Project(unittest.TestCase):
    
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
    #     self.project1.remove_member(sample_user)
    #     self.assertNotIn(sample_user , self.project1.collaborators)


class TestMain_cls_Task(unittest.TestCase):
    pass
    
    

        
if __name__ == '__main__':
    unittest.main()