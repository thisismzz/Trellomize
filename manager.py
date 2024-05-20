import argparse
import json
import os
import base64

class Manager:
    def create_admin(username, password):
        if os.path.exists("admin_info.json"):
            print("Error: Admin info already exists.")
            return
        admin_info = {
            "username": username, 
            "password": base64.b64encode(password.encode("utf-8")).decode("utf-8")
        }
        with open("admin_info.json", "w") as admin_file:
            json.dump(admin_info, admin_file)
        print("Admin info created successfully.")

    def load_users():
        if not os.path.exists("user_info.json"):
            print("Error: User info file not found.")
            return
        with open("user_info.json", "r") as user_file:
            users_data = json.load(user_file)
        return users_data

    def inactive_users():
        users_data = Manager.load_users()
        inactive_users = [user for user in users_data if not user["active"]]
        return inactive_users

    def purge_data():
        if os.path.exists("user_info.json"):
            os.remove("user_info.json")
            print("User data purged successfully.")
        else:
            print("Error: User info file not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin info")
    parser.add_argument("--username", help="Admin username", required=True)
    parser.add_argument("--password", help="Admin password", required=True)
    args = parser.parse_args()
    Manager.create_admin(args.username, args.password)