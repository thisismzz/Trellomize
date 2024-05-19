import argparse
import json
import os
import uuid
import base64


class Manager:
    def create_admin(username, password):
        if os.path.exists("admin_info.json"):
            print("Error: Admin info already exists.")
            return
        admin_info = {"username": username, "password": str(base64.b64encode(password.encode("utf-8"))) }
        with open("admin_info.json", "w") as admin_file:
            json.dump(admin_info, admin_file)
        print("Admin info created successfully.")

    def load_users():
        pass
    
    def inactive_users():
        pass
        
    def purge_data():
        pass

if "name" == "__main__":
    parser = argparse.ArgumentParser(description="Create admin info")
    parser.add_argument("--username", help="Admin username", required=True)
    parser.add_argument("--password", help="Admin password", required=True)
    args = parser.parse_args()
    create_admin(args.username, args.password)