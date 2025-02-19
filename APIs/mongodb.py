from pymongo import MongoClient
import bcrypt
from SHOPNIQ.settings import MONGO_DB
from bson import ObjectId
import pytz
import datetime

# Connect to MongoDB client and set the database
# client = MongoClient("mongodb://localhost:27017/")
# db = client["test"]  # Specify the 'test' database

# Reference the collections correctly from 'db'
products_collection = MONGO_DB["products"]
users_collection = MONGO_DB["users"]
contact_messages = MONGO_DB["contact_messages"]
reviews_collection = MONGO_DB["reviews"]
descriptions_collection = MONGO_DB["descriptions"]
categories_collection = MONGO_DB["categories_collection"]

ist = pytz.timezone('Asia/Kolkata')
from datetime import datetime
# client = MongoClient("mongodb://localhost:27017/")
# db = client["your_database"]

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
    
    # from bson import ObjectId

    def add_product(name, category_id, subcategory, actual_price, price, stock, variants, tags, weight, dimensions, images, description_id, reviews, banner_img, is_new_arrival=False, is_best_seller=False, is_top_rated=False, rating=0, sales_count=0):
        """Add a new product to the database with additional filtering fields."""

        # Calculate discount percentage
        discount_percentage = round(((actual_price - price) / actual_price) * 100, 2) if actual_price > price else 0

        # Extract available colors and sizes
        available_colors = list(variants.get("color", {}).keys())  # Example: ["black", "brown"]
        available_sizes = list(variants.get("size", {}).keys())  # Example: ["S", "M", "L"]

        product_data = {
            "name": name,
            "added_date": datetime.datetime.utcnow(),  # Automatically set the added date
            "updated_date": None,  # Initially set as None
            "category_id": ObjectId(category_id),  # Reference to category
            "subcategory": subcategory,
            "actual_price": actual_price,  # Original price before discount
            "price": price,  # Selling price
            "discount_percentage": discount_percentage,  # Calculated discount %
            "stock": stock,
            "variants": variants,  # {"color": {"black": 10, "brown": 5}, "size": {"S": 5, "M": 8}}
            "tags": tags,  # ["leather", "jacket", "men"]
            "description_id": ObjectId(description_id),  # Reference to description
            "reviews": [ObjectId(review_id) for review_id in reviews],  # List of review IDs
            "weight": weight,  # "1.5kg"
            "dimensions": dimensions,  # {"length": "70cm", "width": "50cm"}
            "images": images,  # List of image dictionaries
            "banner_img": banner_img,  # Banner image details
            "is_new_arrival": is_new_arrival,  # Boolean flag for new arrivals
            "is_best_seller": is_best_seller,  # Boolean flag for best sellers
            "is_top_rated": is_top_rated,  # Boolean flag for top-rated
            "rating": rating,  # Numeric rating (1-5 scale)
            "sales_count": sales_count,  # Number of times sold
            "available_colors": available_colors,  # List of colors
            "available_sizes": available_sizes,  # List of sizes
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
        """Convert MongoDB product document into a properly formatted dictionary."""
        if not product or "_id" not in product:
            return None  # 🛑 Skip if product is invalid

        return {
            "id": str(product["_id"]),  # Product ID
            "name": product.get("name", "Unknown Product"),
            "added_date": product.get("added_date", ""),
            "updated_date": product.get("updated_date", ""),
            "category_id": str(product.get("category_id", "")),  # Ensure string format
            "subcategory": product.get("subcategory", "Unknown Category"),
            "actual_price": product.get("actual_price", 0),  # Original price
            "price": product.get("price", 0),  # Selling price
            "discount_percentage": product.get("discount_percentage", 0),  # Discount %
            "stock": product.get("stock", 0),
            "variants": product.get("variants", {}),  # Dictionary for variants (e.g., color, size)
            "tags": product.get("tags", []),  # Tags for filtering
            "description_id": str(product.get("description_id", "")),  # Convert to string
            "reviews": [str(review_id) for review_id in product.get("reviews", [])],  # Convert IDs to strings
            "weight": product.get("weight", ""),
            "dimensions": product.get("dimensions", {}),  # Product dimensions
            "images": product.get("images", []),  # List of image dictionaries
            "banner_img": product.get("banner_img", {}),  # Banner image details

            # 🔹 Filtering Fields for Category Sections
            "is_new_arrival": product.get("is_new_arrival", False),  # New arrivals
            "is_best_seller": product.get("is_best_seller", False),  # Best sellers
            "is_top_rated": product.get("is_top_rated", False),  # Top-rated
            "rating": product.get("rating", 0),  # Rating (1-5 scale)
            "sales_count": product.get("sales_count", 0),  # Number of times sold
            "available_colors": product.get("available_colors", []),  # Color options
            "available_sizes": product.get("available_sizes", []),  # Size options
        }

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
