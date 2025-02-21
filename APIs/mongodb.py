from pymongo import MongoClient
import bcrypt
from SHOPNIQ.settings import MONGO_DB
from bson import ObjectId
import pytz
import datetime as dt

# Connect to MongoDB client and set the database
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Specify the 'test' database
products_collection = db["products"]
descriptions_collection = db["descriptions"] 
# Reference the collections correctly from 'db'
users_collection = db["users"]
contact_messages = db["contact_messages"]
reviews_collection = db["reviews"]
descriptions_collection = db["descriptions"]
categories_collection = db["categories_collection"]
brands_collection = db["brands_collection"]

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
            "date_of_register": dt.datetime.now(dt.timezone.utc),  # Use timezone-aware UTC now
            "last_login": dt.datetime.now(dt.timezone.utc),  # Use timezone-aware UTC now
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
            "date_of_register": dt.datetime.now(dt.timezone.utc),  # Use timezone-aware UTC now
            "last_login": dt.datetime.now(dt.timezone.utc),  # Use timezone-aware UTC now
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
    def filter_products_by_price(min_price=None, max_price=None, sort_by="price", order="asc"):
        """Fetch products based on a price range and sorting criteria."""
        sort_order = -1 if order == "desc" else 1
        price_filter = {}

        # Apply minimum price filter
        if min_price is not None and min_price.isdigit():
            price_filter["$gte"] = float(min_price)

        # Apply maximum price filter
        if max_price is not None and max_price.isdigit():
            price_filter["$lte"] = float(max_price)

        # Build query
        query = {"price": price_filter} if price_filter else {}

        # Fetch filtered products from the database
        products = products_collection.find(query).sort(sort_by, sort_order)

        return [MongoDBProduct.serialize_product(p) for p in products]

    @staticmethod
    def get_products_by_category(category_id, sort_by="price", order="asc"):
        """Fetch top products in a given category, sorted by stock/popularity."""
        sort_order = -1 if order == "desc" else 1
        products = products_collection.find({"category_id": ObjectId(category_id)}).sort(sort_by, sort_order)
        return [MongoDBProduct.serialize_product(p) for p in products]

    @staticmethod
    def search_products(query, sort_by="price", order="asc"):
            """Find products related to a search query (name, tags, or linked description)."""
            sort_order = -1 if order == "desc" else 1

            # Step 1: Search for matching descriptions
            matching_descriptions = descriptions_collection.find(
                {"description": {"$regex": query, "$options": "i"}}
            )

            # Extract matching product IDs from found descriptions
            matching_product_ids = [desc["PID"] for desc in matching_descriptions]

            # Step 2: Search in products for name, tags, and matching description IDs
            search_criteria = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}},
                    {"_id": {"$in": matching_product_ids}}  # Match products with found descriptions
                ]
            }

            products = products_collection.find(search_criteria).sort(sort_by, sort_order)

            return [MongoDBProduct.serialize_product(p) for p in products]


    @staticmethod
    def get_all_products(sort_by="price", order="asc"):
        """Fetch all products, sorted by the specified field."""
        sort_order = -1 if order == "desc" else 1
        products = products_collection.find().sort(sort_by, sort_order)
        return [MongoDBProduct.serialize_product(p) for p in products]

    @staticmethod
    def add_product(name, brand_name, category_name, subcategory, actual_price, price, stock, variants, tags, weight, dimensions, images, description_id, reviews, banner_img):
        """Add a new product to the database, ensuring category, brand, and description exist."""

        # Ensure brand exists or create a new one
        brand_id = MongoDBBrand.get_or_create_brand(brand_name)

        # Ensure category exists or create a new one
        category_id = MongoDBCategory.get_or_create_category(category_name)

        # Create product entry first (without description_id)
        product_data = {
            "name": name,
            "brand_id": ObjectId(brand_id),  # ✅ Store brand as ObjectId
            "added_date": dt.datetime.now(dt.timezone.utc),
            "updated_date": None,
            "category_id": ObjectId(category_id),
            "subcategory": subcategory,
            "actual_price": actual_price,
            "price": price,
            "stock": stock,
            "variants": variants,
            "tags": tags,
            "description_id": None,  # Initially set to None
            "reviews": [ObjectId(review_id) for review_id in reviews] if reviews else [],
            "weight": weight,
            "dimensions": dimensions,
            "images": images,
            "banner_img": banner_img,
        }

        # Insert the product into MongoDB
        result = products_collection.insert_one(product_data)
        product_id = result.inserted_id  # Get the inserted product's ObjectId

        # Now, create the description with the product_id
        description_id = MongoDBDescription.get_or_create_description(product_id, description_id)

        # Update the product to include the description_id
        products_collection.update_one(
            {"_id": product_id}, {"$set": {"description_id": description_id}}
        )

        # Increment product count in the category
        MongoDBCategory.increment_product_count(category_id)

        return str(product_id)

    @staticmethod
    def delete_product(product_id):
        """Delete a product and decrement its category count."""
        product = products_collection.find_one({"_id": ObjectId(product_id)})

        if product:
            category_id = product.get("category_id")
            
            # Delete the product from the database
            products_collection.delete_one({"_id": ObjectId(product_id)})

            # Decrement the product count in the category
            if category_id:
                MongoDBCategory.decrement_product_count(category_id)

            return True
        return False


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
                "_id": str(product["_id"]),
                "name": product["name"],
                "brand_id": str(product["brand_id"]),  # ✅ Include brand reference
                "added_date": product["added_date"],
                "updated_date": product["updated_date"],
                "category_id": str(product["category_id"]),
                "subcategory": product["subcategory"],
                "actual_price": product["actual_price"],
                "price": product["price"],
                "stock": product["stock"],
                "variants": product["variants"],
                "tags": product["tags"],
                "description_id": str(product["description_id"]),
                "reviews": [str(review_id) for review_id in product.get("reviews", [])],
                "weight": product["weight"],
                "dimensions": product["dimensions"],
                "images": product["images"],
                "banner_img": product["banner_img"],
            }
        return None
    

class MongoDBBrand:
    @staticmethod
    def get_or_create_brand(brand_name):
        """Check if brand exists, otherwise create a new one."""
        existing_brand = brands_collection.find_one({"name": brand_name})

        if existing_brand:
            return str(existing_brand["_id"])  # Return existing brand ID

        # Create a new brand entry
        brand_data = {
            "name": brand_name,
            "created_at": dt.datetime.now(dt.timezone.utc)
        }

        result = brands_collection.insert_one(brand_data)
        return str(result.inserted_id)  # Return new brand ID

    @staticmethod
    def get_brand_by_id(brand_id):
        """Retrieve a brand by ID."""
        brand = brands_collection.find_one({"_id": ObjectId(brand_id)})
        return MongoDBBrand.serialize_brand(brand) if brand else None

    @staticmethod
    def get_brand_id_by_name(brand_name):
        """Retrieve a brand ID by name."""
        brand = brands_collection.find_one({"name": {"$regex": f"^{brand_name}$", "$options": "i"}})
        return str(brand["_id"]) if brand else None

    @staticmethod
    def serialize_brand(brand):
        """Convert brand document into a dictionary."""
        if brand:
            return {
                "_id": str(brand["_id"]),
                "name": brand["name"],
                "created_at": brand["created_at"]
            }
        return None

    @staticmethod
    def get_all_brands():
        """Retrieve all brands."""
        brands = brands_collection.find({})
        return [MongoDBBrand.serialize_brand(brand) for brand in brands]

    @staticmethod
    def list_brand_names():
        """Retrieve a list of all brand names for filtering."""
        brands = brands_collection.find({}, {"name": 1, "_id": 0})
        return [brand["name"] for brand in brands]

    @staticmethod
    def get_product_brands():
        """
        Fetch all products, extract their category IDs and brand IDs,
        retrieve corresponding brand names, and return a dictionary.
        """
        # Fetch all products from the database
        products = products_collection.find({}, {"category_id": 1, "brand_id": 1})

        category_brands = {}

        for product in products:
            category_id = str(product.get("category_id", "Unknown"))
            brand_id = product.get("brand_id")

            if brand_id:
                brand = MongoDBBrand.get_brand_by_id(brand_id)
                if brand:
                    brand_name = brand["name"]
                else:
                    brand_name = "Unknown Brand"
            else:
                brand_name = "No Brand"

            # Organize brands under category IDs
            if category_id not in category_brands:
                category_brands[category_id] = set()
            category_brands[category_id].add(brand_name)

        # Convert sets to lists before returning
        return {category: list(brands) for category, brands in category_brands.items()}
    
    @staticmethod
    def get_brands_by_category(category_id):
        """
        Fetch all brands associated with a specific category.
        :param category_id: The ID of the category (as a string or ObjectId).
        :return: A list of brand names for the given category.
        """
        if not ObjectId.is_valid(category_id):
            return []  # Return empty if invalid category_id

        # Fetch products with the given category_id
        products = products_collection.find({"category_id": ObjectId(category_id)}, {"brand_id": 1})

        brand_names = set()  # Use set to avoid duplicates

        for product in products:
            brand_id = product.get("brand_id")
            if brand_id:
                brand = MongoDBBrand.get_brand_by_id(brand_id)
                if brand:
                    brand_names.add(brand["name"])

        return list(brand_names)  # Convert set to list before returning


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
            "Date": dt.datetime.now(dt.timezone.utc)  # Use timezone-aware UTC now
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
#     "Date": dt.datetime.now(dt.timezone.utc)  # Timestamp when the review was added
# }


class MongoDBDescription:
    @staticmethod
    def get_or_create_description(product_id, description_text):
        """Retrieve description ID if it exists, otherwise create a new one."""
        description = descriptions_collection.find_one({"PID": ObjectId(product_id)})

        if description:
            return str(description["_id"])  # Return existing description ID
        else:
            # Create a new description
            new_description_id = MongoDBDescription.add_description(product_id, description_text)
            return new_description_id  # Return newly created description ID

    @staticmethod
    def add_description(product_id, description_text):
        """Add a new description entry in the database with product ID."""
        description_data = {
            "PID": ObjectId(product_id),  # Reference to the product ID
            "description": description_text,  # Description text
            "added_date": dt.datetime.now(dt.timezone.utc),  # Use timezone-aware UTC now
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
                    "updated_date": dt.datetime.now(dt.timezone.utc)  # Use timezone-aware UTC now
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


from bson import ObjectId

class MongoDBCategory:
    @staticmethod
    def get_category_ids_by_name(query):
        """Retrieve category IDs where the name contains the search query."""
        matching_categories = categories_collection.find(
            {"CategoryName": {"$regex": query, "$options": "i"}}  # Case-insensitive search
        )
        return [str(cat["_id"]) for cat in matching_categories]  # Return list of IDs as strings

    @staticmethod
    def get_or_create_category(category_name):
        """Retrieve category ID if it exists, otherwise create a new category."""
        category = categories_collection.find_one({"CategoryName": category_name})

        if category:
            return str(category["_id"])  # Return existing category ID
        else:
            # Create a new category with product_count = 0
            new_category_id = MongoDBCategory.add_category(category_name)
            return new_category_id  # Return newly created category ID

    @staticmethod
    def add_category(category_name):
        """Add a new category to the database with an initial product count of 0."""
        category_data = {
            "CategoryName": category_name,
            "product_count": 0  # Initialize product count
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
        """Delete category by ID. Only delete if product count is zero."""
        category = categories_collection.find_one({"_id": ObjectId(category_id)})
        if category and category.get("product_count", 0) > 0:
            return False  # Prevent deletion if products exist

        result = categories_collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0  # Returns True if deletion was successful

    @staticmethod
    def increment_product_count(category_id):
        """Increase product count for the given category."""
        categories_collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$inc": {"product_count": 1}}  # Increment by 1
        )

    @staticmethod
    def decrement_product_count(category_id):
        """Decrease product count for the given category, ensuring it doesn’t go below zero."""
        categories_collection.update_one(
            {"_id": ObjectId(category_id), "product_count": {"$gt": 0}},  # Prevent negative count
            {"$inc": {"product_count": -1}}
        )

    @staticmethod
    def serialize_category(category):
        """Convert category document into a dictionary with string IDs."""
        if category:
            return {
                "_id": str(category["_id"]),  # Convert ObjectId to string
                "CategoryName": category["CategoryName"],
                "product_count": category.get("product_count", 0)  # Default to 0 if missing
            }
        return None
