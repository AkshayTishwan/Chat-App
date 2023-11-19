from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from user import User
client = MongoClient("mongodb+srv://test:test@chatapp-q7wkc.mongodb.net/test?retryWrites=true&w=majority")
chat_db = client.get_database("ChatDB")
users_collection = chat_db.get_collection("users")

def save_user(username, email, password):
    password_hash = generate_password_hash(password)  # Fix: Call generate_password_hash with the password
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})

# Example usage
save_user("akshay", "a@gmail.com", "test")


def get_user(username):
    user_data = users_collection.find_one({'_id':username})
    return User(user_data['_id'],user_data['email'],user_data['password']) if user_data else None