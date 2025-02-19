from pymongo import MongoClient
import bcrypt
from SHOPNIQ.settings import MONGO_DB
from bson import ObjectId
import pytz
import datetime

# Connect to MongoDB client and set the database
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Specify the 'test' database
products_collection = db["products"]

# Reference the collections correctly from 'db'
users_collection = db["users"]
contact_messages = db["contact_messages"]
reviews_collection = db["reviews"]
descriptions_collection = db["descriptions"]
categories_collection = db["categories_collection"]

ist = pytz.timezone('Asia/Kolkata')
from datetime import datetime
# client = MongoClient("mongodb://localhost:27017/")
# db = client["your_database"]
users_collection = MONGO_DB["users"]
contact_messages = MONGO_DB["contact_messages"]

class MongoDBUser:
    @staticmethod
    def create_user(username, email, password, role="user", phone_number=None):  # Default role = user
        # Hashing the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Prepare user data to be inserted
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "phone_number": phone_number,  # Optional, can be None
            "role": role,
            "date_of_register": datetime.datetime.now(ist),  # Store registration date in IST timezone
            "last_login": None,  # Initially, no login
            "session_timing": None,  # Initially, no session time
            "address": [],  # Initially, no address
            "orders": []  # Initially, no orders
        }

        # Insert user data into MongoDB
        result = users_collection.insert_one(user_data)
        return result.inserted_id

    @staticmethod
    def create_user(username, email, role, password=None,):
        """ Create a new user in MongoDB. """
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            return existing_user  # Return existing user
        
        # Create new user
        new_user = {
            "username": username,
            "email": email,
            "password": password if password else None,  # Allow None password for Google OAuth
            "role": role,
            "date_of_register": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "session_timing": "120 min",
            "address": [],
            "orders": []
        }
        
        inserted = users_collection.insert_one(new_user)
        new_user["_id"] = inserted.inserted_id
        return new_user

    @staticmethod
    def get_user_by_email(email):
        # Fetch user by email
        return users_collection.find_one({"email": email})

    @staticmethod
    def get_user_by_id(user_id):
        try:
            print(f"🔍 Fetching User by ID: {user_id}")  # Debugging
            # Ensure ObjectId is used correctly for MongoDB's _id field
            return users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            print(f"❌ Error fetching user by ID: {e}")
            return None

from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# Assuming `products_collection` is initialized somewhere in your MongoDB setup
# Example: `products_collection = MongoClient()["your_database"]["products"]`

class MongoDBProduct:
    @staticmethod
    def add_product(name, category_id, subcategory, actual_price, price, stock, variants, tags, weight, dimensions, images, description_id, reviews, banner_img):
        """Add a new product to the database."""
        product_data = {
            "name": name,
            "added_date": datetime.datetime.utcnow(),  # Automatically set the added date
            "updated_date": None,  # Initially set the updated_date as None
            "category_id": ObjectId(category_id),  # Reference to category
            "subcategory": subcategory,
            "actual_price": actual_price,  # New field for actual price
            "price": price,  # Discounted or selling price
            "stock": stock,
            "variants": variants,  # e.g., {"color": {"black": 10, "brown": 5}, "size": {"S": 5, "M": 8}}
            "tags": tags,  # e.g., ["leather", "jacket", "men"]
            "description_id": ObjectId(description_id),  # Reference to description
            "reviews": [ObjectId(review_id) for review_id in reviews],  # List of ObjectId references for reviews
            "weight": weight,  # e.g., "1.5kg"
            "dimensions": dimensions,  # e.g., {"length": "70cm", "width": "50cm"}
            "images": images,  # List of image dictionaries
            "banner_img": banner_img,  # Banner image details
        }

        # Insert the product data into the products collection
        result = products_collection.insert_one(product_data)
        return str(result.inserted_id)  # Return the inserted product's ObjectId as a string

    @staticmethod
    def get_product_by_id(product_id):
        """Retrieve a product by its ID and return serialized data."""
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        return MongoDBProduct.serialize_product(product) if product else None

    @staticmethod
    def serialize_product(product):
        """Convert product document into a dictionary with string IDs."""
        if product:
            return {
                "_id": str(product["_id"]),  # Product ID
                "name": product["name"],
                "added_date": product["added_date"],
                "updated_date": product["updated_date"],
                "category_id": str(product["category_id"]),  # Category ID as a string
                "subcategory": product["subcategory"],
                "actual_price": product["actual_price"],  # Actual price before discount
                "price": product["price"],  # Selling price
                "stock": product["stock"],
                "variants": product["variants"],  # Variants like colors and sizes
                "tags": product["tags"],
                "description_id": str(product["description_id"]),  # Description ID as a string
                "reviews": [str(review_id) for review_id in product.get("reviews", [])],  # Reviews references
                "weight": product["weight"],
                "dimensions": product["dimensions"],
                "images": product["images"],  # List of image dictionaries
                "banner_img": product["banner_img"],  # Banner image details
            }
        return None

    @staticmethod
    def update_product(product_id, update_fields):
        """Update product details in the database."""
        update_fields['updated_date'] = datetime.datetime.utcnow()  # Update timestamp

        result = products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_fields}
        )

        return result.modified_count > 0  # Return True if update was successful

    @staticmethod
    def delete_product(product_id):
        """Delete a product from the database by ID."""
        result = products_collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0  # Return True if deletion was successful



# sample_product = {
#     "name": "Premium Leather Jacket",
#     "category_id": "C001",  # This should be a valid ObjectId in MongoDB
#     "subcategory": "Men's Jackets",
#     "price": 299.99,
#     "stock": 0,
#     "variants": {
#         "color": {
#             "black": 10,
#             "brown": 5
#         },
#         "size": {
#             "S": 5,
#             "M": 8,
#             "L": 12
#         }
#     },
#     "tags": ["leather", "jacket", "men"],
#     "description_id": "D001",  # This should be a valid ObjectId in MongoDB
#     "reviews": ["R001"],  # This should be a list of valid ObjectIds in MongoDB
#     "weight": "1.5kg",
#     "dimensions": {
#         "length": "70cm",
#         "height": "10cm",
#         "width": "50cm"
#     },
#     "images": [
#         {"main": "image_url_1.jpg", "alt": "image_url_2.jpg"},
#         {"main": "image_url_3.jpg", "alt": "image_url_4.jpg"}
#     ],
#     "banner_img": {
#         "Url": "banner_image.jpg",
#         "alt": "banner_alt_text"
#     }
# }
class MongoDBReview:
    @staticmethod
    def add_review(product_id, user_id, review_text, review_stars):
        review_data = {
            "PID": ObjectId(product_id),  # Reference to the product
            "UID": ObjectId(user_id),  # Reference to the user who wrote the review
            "ReviewText": review_text,  # Review content
            "ReviewStars": review_stars,  # Rating out of 5
            "Date": datetime.datetime.utcnow()  # Timestamp when the review was added
        }

        result = reviews_collection.insert_one(review_data)
        return str(result.inserted_id)

    @staticmethod
    def get_review_by_product_id(product_id):
        reviews = reviews_collection.find({"PID": ObjectId(product_id)})
        return [MongoDBReview.serialize_review(review) for review in reviews] if reviews else []

    @staticmethod
    def serialize_review(review):
        if review:
            return {
                "_id": str(review["_id"]),
                "PID": str(review["PID"]),  # Product ID reference
                "UID": str(review["UID"]),  # User ID reference
                "ReviewText": review["ReviewText"],
                "ReviewStars": review["ReviewStars"],
                "Date": review["Date"]
            }
        return None



# Define sample data for a review
# sample_review_data = {
#     "PID": ObjectId("67b3f31f4a6a40a08c5ad809"),  # Reference to the product
#     "UID": ObjectId("67b3de5cb43e12c7dd584856"),  # Reference to the user
#     "ReviewText": "This product is amazing! High quality and comfortable.",
#     "ReviewStars": 5,  # Rating out of 5
#     "Date": datetime.datetime.utcnow()  # Timestamp when the review was added
# }


class MongoDBDescription:
    @staticmethod
    def add_description(product_id, description_text):
        description_data = {
            "PID": ObjectId(product_id),  # Reference to the product ID
            "description": description_text,  # Description text
            "added_date": datetime.datetime.utcnow(),  # Timestamp when the description is added
            "updated_date": None  # Initially, no update
        }

        result = descriptions_collection.insert_one(description_data)
        return str(result.inserted_id)

    @staticmethod
    def update_description(product_id, new_description_text):
        updated_result = descriptions_collection.update_one(
            {"PID": ObjectId(product_id)},
            {
                "$set": {
                    "description": new_description_text,
                    "updated_date": datetime.datetime.utcnow()  # Update timestamp
                }
            }
        )
        return updated_result.modified_count > 0  # Return True if update was successful

    @staticmethod
    def get_description_by_product_id(product_id):
        description = descriptions_collection.find_one({"PID": ObjectId(product_id)})
        return MongoDBDescription.serialize_description(description) if description else None

    @staticmethod
    def serialize_description(description):
        if description:
            return {
                "_id": str(description["_id"]),
                "PID": str(description["PID"]),  # Product ID
                "description": description["description"],  # Description text
                "added_date": description["added_date"],  # Timestamp when added
                "updated_date": description.get("updated_date")  # Timestamp when last updated
            }
        return None


class MongoDBCategory:
    @staticmethod
    def add_category(category_name):
        """Add a new category to the database."""
        category_data = {
            "CategoryName": category_name
        }

        result = categories_collection.insert_one(category_data)
        return str(result.inserted_id)

    @staticmethod
    def get_category_by_id(category_id):
        """Retrieve category by ID."""
        category = categories_collection.find_one({"_id": ObjectId(category_id)})
        return MongoDBCategory.serialize_category(category) if category else None

    @staticmethod
    def get_all_categories():
        """Retrieve all categories."""
        categories = categories_collection.find()
        return [MongoDBCategory.serialize_category(category) for category in categories]

    @staticmethod
    def update_category(category_id, new_category_name):
        """Update category name."""
        result = categories_collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": {"CategoryName": new_category_name}}
        )
        return result.modified_count > 0  # Returns True if update was successful

    @staticmethod
    def delete_category(category_id):
        """Delete category by ID."""
        result = categories_collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0  # Returns True if deletion was successful

    @staticmethod
    def serialize_category(category):
        """Convert category document into a dictionary with string IDs."""
        if category:
            return {
                "_id": str(category["_id"]),  # Convert ObjectId to string
                "CategoryName": category["CategoryName"]
            }
        return None
