from pymongo import MongoClient
import bcrypt
from SHOPNIQ.settings import MONGO_DB
from bson import ObjectId
import pytz
import datetime as dt
from datetime import datetime, timedelta
from .coupons_manager import MongoDBCoupons

# Connect to MongoDB client and set the database
# client = MongoClient("mongodb://localhost:27017/")
# db = client["test"]  # Specify the 'test' database
# products_collection = db["products"]
# descriptions_collection = db["descriptions"] 
# # Reference the collections correctly from 'db'
# users_collection = db["users"]
# contact_messages = db["contact_messages"]
# reviews_collection = db["reviews"]
# descriptions_collection = db["descriptions"]
# categories_collection = db["categories_collection"]
# brands_collection = db["brands_collection"]

products_collection = MONGO_DB["products"]
descriptions_collection = MONGO_DB["descriptions"]
users_collection = MONGO_DB["users"]
contact_messages = MONGO_DB["contact_messages"]
reviews_collection = MONGO_DB["reviews"]
categories_collection = MONGO_DB["categories"]
brands_collection = MONGO_DB["brands"]
cart_collection = MONGO_DB["cart"]
db = MONGO_DB

ist = pytz.timezone('Asia/Kolkata')
from datetime import datetime
# client = MongoClient("mongodb://localhost:27017/")
# db = client["your_database"]
users_collection = MONGO_DB["users"]
contact_messages = MONGO_DB["contact_messages"]

# MongoDB collection for wishlists
wishlist_collection = MONGO_DB["wishlists"]

class MongoDBUser:
    @staticmethod
    def create_user(username, email, password=None, phone_number=None, profile_image=None, role="user", is_google_auth=False):
        """
        Create a new user in MongoDB.
        Handles both normal and Google OAuth signups.
        
        Args:
            username (str): The user's name.
            email (str): The user's email.
            password (str, optional): The user's password. Required for normal signup.
            phone_number (str, optional): The user's phone number.
            profile_image (str, optional): The user's profile image URL.
            role (str, optional): The user's role. Default is "user".
            is_google_auth (bool, optional): True if the signup is via Google OAuth.
            
        Returns:
            dict: The created or existing user.
        """

        # Check if the user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return existing_user  # Return existing user if found

        # Handle password hashing for normal signup
        hashed_password = None
        if not is_google_auth:
            if not password:
                raise ValueError("Password is required for normal signup.")
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Prepare user data for insertion
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,  # None if Google OAuth
            "phone_number": phone_number,
            "role": role,
            "profile_image": profile_image,
            "is_google_auth": is_google_auth,
            "date_of_register": dt.datetime.now(dt.timezone.utc),
            "last_login": dt.datetime.now(dt.timezone.utc),
            "session_timing": "120 min" if is_google_auth else None,
            "orders": []
        }

        # Insert new user data into MongoDB
        result = users_collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data

    @staticmethod
    def get_user_by_email(email):
            # Fetch user by email
            return users_collection.find_one({"email": email})

    @staticmethod
    def get_user_by_id(user_id):
            try:
                print(f"🔍 Fetching User by ID: {user_id}")  # Debugging
                # Ensure ObjectId is used correctly for MongoDB's _id field
                user = users_collection.find_one({"_id": ObjectId(user_id)})
                print(user)
                return user
            except Exception as e:
                print(f"❌ Error fetching user by ID: {e}")
                return None

    
    @staticmethod
    def save_address(user_id, address_data):
        """
        Save or update the address for a user.
        
        Args:
            user_id (str): The ID of the user.
            address_data (dict): The address data to save.
        """
        try:
            # Ensure the user_id is converted to ObjectId
            user_id = ObjectId(user_id)
            
            # Add timestamp to the address data
            address_data["updated_at"] = dt.datetime.now(dt.timezone.utc)
            
            # Update the user document with the new address as a dictionary
            result = users_collection.update_one(
                {"_id": user_id},
                {"$set": {"address": address_data}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error saving address: {e}")
            return False

    @staticmethod
    def get_address(user_id):
        """
        Fetch the address for a user.
        
        Args:
            user_id (str): The ID of the user.
        
        Returns:
            dict: The address of the user, or an empty dict if none is found.
        """
        try:
            # Ensure the user_id is converted to ObjectId
            user_id = ObjectId(user_id)
            
            # Fetch the user document and return the address
            user = users_collection.find_one(
                {"_id": user_id},
                {"address": 1}  # Only fetch the address field
            )
            
            return user.get("address", {}) if user else {}
        except Exception as e:
            print(f"❌ Error fetching address: {e}")
            return {}

    @staticmethod
    def update_user_details(user_id, update_data):
        """
        Update user details in MongoDB.
        
        Args:
            user_id (str): The ID of the user.
            update_data (dict): A dictionary of fields to update.
        
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating user details: {e}")
            return False

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
    def get_top_latest_products(limit=10):
        """Fetch the latest products, sorted by added_date (newest first)."""
        products = products_collection.find().sort("added_date", -1).limit(limit)
        return [MongoDBProduct.serialize_product(p) for p in products]

    @staticmethod
    def get_top_selling_products(limit=10):
        """Fetch top products based on sales count (highest first)."""
        products = products_collection.find().sort("sales_count", -1).limit(limit)
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
            "sales_count": 0,  # ✅ New field to track sales count
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
    def update_sales_count(product_id, quantity):
        """Update the sales count when a product is purchased."""
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"sales_count": quantity}}
        )

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
        """Convert product document into a dictionary with string IDs and formatted fields."""
        if not product:
            return None

        return {
            "_id": str(product["_id"]),
            "name": product.get("name", ""),
            "brand_id": str(product.get("brand_id", "")),  # ✅ Include brand reference
            "added_date": product["added_date"].isoformat() if "added_date" in product else None,  # ✅ Convert to ISO format
            "updated_date": product["updated_date"].isoformat() if "updated_date" in product and product["updated_date"] else None,
            "category_id": str(product.get("category_id", "")),
            "subcategory": product.get("subcategory", ""),
            "actual_price": product.get("actual_price", 0.0),
            "price": product.get("price", 0.0),
            "stock": product.get("stock", 0),
            "variants": product.get("variants", []),
            "tags": product.get("tags", []),
            "description_id": str(product.get("description_id", "")) if product.get("description_id") else None,
            "reviews": [str(review_id) for review_id in product.get("reviews", [])],
            "weight": product.get("weight", ""),
            "dimensions": product.get("dimensions", ""),
            "images": product.get("images", []),
            "banner_img": product.get("banner_img", ""),
            "sales_count": product.get("sales_count", 0),  # ✅ Include sales count
        }


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
    @staticmethod
    def get_brands_by_query(query):
        """
        Retrieve a list of brand names that match the given query.
        :param query: The search query string.
        :return: A list of brand names matching the query.
        """
        if not query:
            return []

        matching_brands = brands_collection.find(
            {"name": {"$regex": query, "$options": "i"}}, {"name": 1}
        )

        return [brand["name"] for brand in matching_brands]
    
    @staticmethod
    def get_brand_categories(brand_id=None):
        """
        Fetch all products, extract their brand IDs and category IDs,
        retrieve corresponding category names, and return data accordingly.

        - If `brand_id` is provided, return only categories for that brand.
        - If `brand_id` is None, return a dictionary of all categories grouped by brand.
        """
        # Query to filter by brand_id if provided
        query = {"brand_id": ObjectId(brand_id)} if brand_id else {}

        # Fetch matching products
        products = products_collection.find(query, {"brand_id": 1, "category_id": 1})

        brand_categories = {}

        for product in products:
            product_brand_id = str(product.get("brand_id", "Unknown"))
            category_id = product.get("category_id")

            if category_id:
                category = MongoDBCategory.get_category_by_id(category_id)
                category_name = category["CategoryName"] if category else "Unknown Category"
            else:
                category_name = "No Category"

            # Organize categories under brand IDs
            if product_brand_id not in brand_categories:
                brand_categories[product_brand_id] = set()
            brand_categories[product_brand_id].add(category_name)

        # Convert sets to lists before returning
        result = {brand: list(categories) for brand, categories in brand_categories.items()}

        # If brand_id was provided, return only its categories
        return result.get(str(brand_id), []) if brand_id else result



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
    @staticmethod
    def get_matching_descriptions(query):
        """Fetch descriptions that contain the search query."""
        matching_descriptions = descriptions_collection.find(
            {"description": {"$regex": query, "$options": "i"}},  # Case-insensitive search
            {"_id": 0, "description": 1}  # Only return descriptions
        )
        return [desc["description"] for desc in matching_descriptions]


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
        """Decrease product count for the given category, ensuring it doesn't go below zero."""
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
    

    @staticmethod
    def get_categories_by_query(query):
        """
        Retrieve a list of category names that match the given query.
        :param query: The search query string.
        :return: A list of category names.
        """
        if not query:
            return []

        matching_categories = categories_collection.find(
            {"CategoryName": {"$regex": query, "$options": "i"}}, {"CategoryName": 1}
        )

        return [cat["CategoryName"] for cat in matching_categories]


from bson import ObjectId
import datetime
from datetime import datetime, timedelta
from bson import ObjectId
from bson import ObjectId, errors
from datetime import datetime, timedelta

orders_collection = MONGO_DB["orders"]  # Assuming you have an 'orders' collection
order_counters_collection = MONGO_DB["order_counters"]

class MongoDBOrders:

    @staticmethod
    def generate_order_number():
        """
        Generates a sequential order number in the format ORD-YYYYMMDD-XXXX.
        Starts from ORD-YYYYMMDD-1001 and increments without repeating.
        """
        today_date = datetime.now().strftime("%Y%m%d")  # Get current date in YYYYMMDD format
        
        # Find and update counter atomically
        counter_data = order_counters_collection.find_one_and_update(
            {"date": today_date},
            {"$inc": {"last_order_no": 1}},  # Increment last order number
            upsert=True,  # If not found, create a new entry
            return_document=True  # Get updated document
        )
        
        # Initialize order number to 1001 if it's a new day
        if not counter_data or "last_order_no" not in counter_data:
            order_number = 1001  # Start from 1001 if it's a new day
            order_counters_collection.update_one(
                {"date": today_date},
                {"$set": {"last_order_no": order_number}}, 
                upsert=True
            )
        else:
            order_number = counter_data["last_order_no"]

        return f"ORD-{today_date}-{order_number}"  # Return the formatted order number


    @staticmethod
    def place_order(user_id, items,original_total_amount,discount_amount, gst, delevery_fee, total_amount, shipping_address, payment_status="Pending", transaction_id=None, estimated_delivery_days=5, applied_coupon=None):
        """
        Places an order with multiple items and sets an estimated delivery date.
        """
        def is_valid_objectid(oid):
            try:
                return ObjectId(oid)
            except errors.InvalidId:
                return None
        # Validate ObjectIds
        user_id = is_valid_objectid(user_id)
        if not user_id:
            raise ValueError("Invalid user_id format")

        for item in items:
            item["product_id"] = is_valid_objectid(item["product_id"])
            if not item["product_id"]:
                raise ValueError("Invalid product_id format")

        # Redeem coupon if provided
        if applied_coupon:
            MongoDBCoupons().redeem_coupon(applied_coupon)

        # Generate unique order number
        order_no = MongoDBOrders.generate_order_number()

        # Create order data
        order_data = {
            "UID": user_id,
            "OrderNo": order_no,
            "Items": [
                {
                    "PID": item["product_id"],
                    "ProductName": item["product_name"],
                    "Quantity": item["quantity"],
                    "PricePerUnit": item["price_per_unit"],
                    "Subtotal": item["subtotal"],
                    "ImageURL": item["image_url"]
                }
                for item in items
            ],
            "FirstName": shipping_address.get("FirstName", ""),
            "LastName": shipping_address.get("LastName", ""),
            "CompanyName": shipping_address.get("CompanyName", ""),
            "CountryRegion": shipping_address.get("CountryRegion", ""),
            "StreetAddress": shipping_address["StreetAddress"],
            "StreetAddress2": shipping_address.get("StreetAddress2", ""),
            "City": shipping_address["City"],
            "State": shipping_address["State"],
            "Zipcode": shipping_address["Zipcode"],
            "Phone": shipping_address["Phone"],
            "Email": shipping_address["Email"],
            "OrderNotes": shipping_address.get("OrderNotes", ""),
            "OriginalTotalAmount": original_total_amount,
            "DiscountAmount": discount_amount,
            "GST": gst,
            "DeliveryFee": delevery_fee,
            "TotalAmount": total_amount,
            "AppliedCoupon": applied_coupon,
            "ShippingAddress": shipping_address,
            "Status": "Pending",
            "PaymentStatus": payment_status,
            "TransactionID": transaction_id,
            "OrderDate": datetime.utcnow(),
            "EstimatedDelivery": datetime.utcnow() + timedelta(days=estimated_delivery_days),
            "Tracking": [],
            "RefundStatus": None,
            "Cancelled": False
        }

        # Insert order and handle errors
        try:
            result = orders_collection.insert_one(order_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Order placement error: {e}")
            return None


    @staticmethod
    def get_orders_by_user(user_id):
        """
        Retrieves all orders placed by a specific user.
        """
        orders = orders_collection.find({"UID": ObjectId(user_id)})
        return [MongoDBOrders.serialize_order(order) for order in orders] if orders else []

    @staticmethod
    def get_order_by_id(order_id):
        """
        Retrieves order details by order ID.
        """
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        return MongoDBOrders.serialize_order(order) if order else {"error": "Order not found"}

    @staticmethod
    def get_order_by_order_no(order_no):
        """
        Retrieves order details by the unique OrderNo.
        """
        order = orders_collection.find_one({"OrderNo": order_no})
        return MongoDBOrders.serialize_order(order) if order else None
    @staticmethod
    def get_all_orders():
        """
        Retrieves all orders from the database for the orders list page.
        """
        orders = orders_collection.find()
        return [MongoDBOrders.serialize_order(order) for order in orders] if orders else []

    @staticmethod
    def track_order(order_id):
        """
        Retrieves tracking details and estimated delivery date of an order.
        """
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            return {
                "OrderID": str(order["_id"]),
                "Status": order["Status"],
                "TrackingUpdates": order["Tracking"],
                "OrderDate": order["OrderDate"],
                "EstimatedDelivery": order.get("EstimatedDelivery"),
                "RefundStatus": order.get("RefundStatus")
            }
        return {"error": "Order not found"}

    @staticmethod
    def update_order_status(order_id, new_status):
        """
        Updates the status of an order (e.g., Processing, Shipped, Delivered).
        """
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"Status": new_status}})
            return {"message": f"Order status updated to {new_status}"}
        return {"error": "Order not found"}

    @staticmethod
    def cancel_order(order_id, reason):
        """
        Cancels an order if it has not been shipped yet.
        """
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            if order["Status"] in ["Pending", "Processing"]:
                orders_collection.update_one({"_id": ObjectId(order_id)}, {
                    "$set": {"Status": "Cancelled", "Cancelled": True, "CancelReason": reason}
                })
                return {"message": "Order cancelled successfully"}
            return {"error": "Order cannot be cancelled as it has already been shipped or delivered"}
        return {"error": "Order not found"}

    @staticmethod
    def process_refund(order_id, reason):
        """
        Processes a refund if the order is eligible.
        """
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            if order["PaymentStatus"] == "Paid" and order["Status"] in ["Cancelled", "Delivered"]:
                refund_data = {
                    "RefundStatus": "Initiated",
                    "RefundReason": reason,
                    "RefundDate": datetime.datetime.utcnow()
                }
                orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": refund_data})
                return {"message": "Refund initiated successfully"}
            return {"error": "Order is not eligible for a refund"}
        return {"error": "Order not found"}

    @staticmethod
    def add_tracking_update(order_id, status_update):
        """
        Adds a tracking update to the order.
        """
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            tracking_update = {
                "Status": status_update,
                "Timestamp": datetime.datetime.utcnow()
            }
            orders_collection.update_one({"_id": ObjectId(order_id)}, {"$push": {"Tracking": tracking_update}})
            return {"message": "Tracking update added successfully"}
        return {"error": "Order not found"}

    @staticmethod
    def serialize_order(order):
        """
        Converts the MongoDB order document into a dictionary format for API responses or frontend rendering.
        """
        if order:
            return {
                "OrderID": str(order["_id"]),
                "OrderNo": str(order["OrderNo"]),
                "UserID": str(order["UID"]),
                "OriginalTotalAmount": order.get("OriginalTotalAmount", 0),
                "DiscountAmount": order.get("DiscountAmount", 0),
                "GST": order.get("GST", 0),
                "DeliveryFee": order.get("DeliveryFee", 0),
                "TotalAmount": order.get("TotalAmount", 0),
                "AppliedCoupon": order.get("AppliedCoupon", None),
                "ShippingAddress": {
                    "FirstName": order.get("FirstName", ""),
                    "LastName": order.get("LastName", ""),
                    "CompanyName": order.get("CompanyName", ""),
                    "CountryRegion": order.get("CountryRegion", ""),
                    "StreetAddress": order.get("StreetAddress", ""),  # Added missing field
                    "StreetAddress2": order.get("StreetAddress2", ""),
                    "City": order.get("City", ""),
                    "State": order.get("State", ""),
                    "Zipcode": order.get("Zipcode", ""),
                    "Phone": order.get("Phone", ""),
                    "Email": order.get("Email", ""),
                    "OrderNotes": order.get("OrderNotes", "")  # Added order notes
                },
                "Status": order.get("Status", "Pending"),
                "PaymentStatus": order.get("PaymentStatus", "Pending"),
                "TransactionID": order.get("TransactionID", None),
                "OrderDate": order.get("OrderDate"),
                "EstimatedDelivery": order.get("EstimatedDelivery"),
                "RefundStatus": order.get("RefundStatus", None),
                "Cancelled": order.get("Cancelled", False),
                "Tracking": order.get("Tracking", []),
                "Items": [
                    {
                        "PID": str(item["PID"]),
                        "ProductName": item.get("ProductName", ""),
                        "Quantity": item.get("Quantity", 0),
                        "PricePerUnit": item.get("PricePerUnit", 0),
                        "Subtotal": item.get("Subtotal", 0),
                        "ImageURL": item.get("ImageURL", "")
                    }
                    for item in order.get("Items", [])
                ]
            }
        return None

    @staticmethod
    def get_product_details_from_orders(user_id):
        """
        Fetches product details from all orders placed by a specific user.
        """
        orders = orders_collection.find({"UID": ObjectId(user_id)})
        product_details = []

        for order in orders:
            for item in order.get("Items", []):
                product_details.append({
                    "OrderID": str(order["_id"]),
                    "OrderNo": order.get("OrderNo", ""),
                    "ProductID": str(item["PID"]),
                    "ProductName": item.get("ProductName", ""),
                    "Quantity": item.get("Quantity", 0),
                    "PricePerUnit": item.get("PricePerUnit", 0),
                    "Subtotal": item.get("Subtotal", 0),
                    "ImageURL": item.get("ImageURL", "")
                })

        return product_details




from datetime import datetime
from bson import ObjectId

class MongoDBCart:
    @staticmethod
    def get_user_cart(user_id):
        """Fetch the entire cart for a user along with product details."""
        cart = MONGO_DB["cart"].find_one({"user_id": ObjectId(user_id)})

        if not cart:
            return None

        return {
            "_id": str(cart["_id"]),
            "user_id": str(cart["user_id"]),
            "products": [
                {
                    "product_id": str(item["product_id"]),
                    "quantity": item["quantity"]
                } 
                for item in cart["products"]
            ],
            "created_at": cart.get("created_at"),
            "updated_at": cart.get("updated_at")
        }

    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        """Add a product to the user's cart or create a new cart if needed."""

        try:
            print(f"🔹 Debug: Received - user_id={user_id}, product_id={product_id}, quantity={quantity}")

            # Validate and convert ObjectId
            user_id = ObjectId(user_id)
            product_id = ObjectId(product_id)
            
            # Connect to MongoDB collection
            cart_collection = MONGO_DB["cart"]

            # Check if the user's cart exists
            cart = cart_collection.find_one({"user_id": user_id})
            print(f"🔹 Debug: Fetched Cart - {cart}")

            if cart:
                # Check if product already exists in the cart
                existing_product = next((item for item in cart["products"] if item["product_id"] == product_id), None)

                if existing_product:
                    # Increase quantity of existing product
                    print(f"🛒 Updating existing product {product_id} quantity")
                    cart_collection.update_one(
                        {"user_id": user_id, "products.product_id": product_id},
                        {"$inc": {"products.$.quantity": quantity}, "$set": {"updated_at": datetime.now(ist)}}
                    )
                else:
                    # Add new product to the cart
                    print(f"🛍️ Adding new product {product_id} to cart")
                    cart_collection.update_one(
                        {"user_id": user_id},
                        {
                            "$push": {"products": {"product_id": product_id, "quantity": quantity}},
                            "$set": {"updated_at": datetime.utcnow()}
                        }
                    )
            else:
                # Create a new cart for the user
                print(f"🆕 Creating new cart for user {user_id}")
                new_cart = {
                    "user_id": user_id,
                    "products": [{"product_id": product_id, "quantity": quantity}],
                    "created_at": datetime.now(ist),
                    "updated_at": datetime.now(ist)
                }
                cart_collection.insert_one(new_cart)

            return {"success": True, "message": "Product added to cart successfully"}

        except Exception as e:
            print(f"❌ Error in add_to_cart: {e}")
            return {"success": False, "error": str(e)}
        
    @staticmethod
    def get_cart_items(user_id):
        """Retrieve all cart items for a specific user."""
        cart = db["cart"].find_one({"user_id": ObjectId(user_id)})
        return cart["products"] if cart else []

    @staticmethod
    def update_cart_item(user_id, product_id, new_quantity):
        """Update the quantity of a specific cart item."""
        result = db["cart"].update_one(
            {"user_id": ObjectId(user_id), "products.product_id": ObjectId(product_id)},
            {"$set": {"products.$.quantity": new_quantity, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0  # True if updated

    @staticmethod
    def remove_from_cart(user_id, product_id):
        """Remove a specific product from the cart."""
        result = db["cart"].update_one(
            {"user_id": ObjectId(user_id)},
            {"$pull": {"products": {"product_id": ObjectId(product_id)}}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0  # True if removed

    @staticmethod
    def clear_cart(user_id):
        """Remove all items from a user's cart."""
        result = db["cart"].update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {"products": [], "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0  # True if cart cleared

    @staticmethod
    def get_cart_total_items(user_id):
        """Get the total number of items in a user's cart."""
        cart = db["cart"].find_one({"user_id": ObjectId(user_id)}, {"products.quantity": 1})

        if not cart or "products" not in cart:
            return 0

        return sum(item["quantity"] for item in cart["products"])

    @staticmethod
    def serialize_cart_item(cart_item):
        """Convert cart document into a dictionary."""
        return {
            "_id": str(cart_item["_id"]),
            "user_id": str(cart_item["user_id"]),
            "products": [
                {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
                for item in cart_item["products"]
            ],
            "created_at": cart_item.get("created_at"),
            "updated_at": cart_item.get("updated_at")
        }

from bson import ObjectId

class MongoDBCustomers:
    @staticmethod
    def get_all_users():
        """
        Fetch all registered users from the database and serialize them.
        """
        users = list(users_collection.find())
        return [MongoDBCustomers.serialize_user(user) for user in users]

    @staticmethod
    def get_users_with_cart():
        """
        Fetch users who have added items to their cart and serialize them.
        """
        user_ids_with_cart = cart_collection.distinct("user_id", {"products": {"$exists": True, "$ne": []}})
        users = list(users_collection.find({"_id": {"$in": [ObjectId(user_id) for user_id in user_ids_with_cart]}}))
        return [MongoDBCustomers.serialize_user(user) for user in users]

    @staticmethod
    def get_users_who_visited():
        """
        Fetch users who have visited the site and serialize them.
        """
        users = list(users_collection.find({"visited": True}))  # Assuming there's a 'visited' field
        return [MongoDBCustomers.serialize_user(user) for user in users]

    @staticmethod
    def get_users_who_ordered():
        """
        Fetch users who have ordered products and serialize them.
        """
        user_ids = orders_collection.distinct("UID")  # Assuming 'UID' is the user ID in the orders collection
        users = list(users_collection.find({"_id": {"$in": [ObjectId(user_id) for user_id in user_ids]}}))
        return [MongoDBCustomers.serialize_user(user) for user in users]

    @staticmethod
    def get_user_details(user_id):
        """
        Fetch details of a specific user by user ID and serialize them.
        """
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return MongoDBCustomers.serialize_user(user) if user else None

    @staticmethod
    def calculate_total_spent(user_id):
        """
        Calculate the total amount spent by a specific user.
        """
        total_spent = 0
        # Fetch all orders for the user
        orders = orders_collection.find({"UID": ObjectId(user_id)})
        
        # Sum the total amount from each order
        for order in orders:
            total_spent += order.get("TotalAmount", 0)  # Assuming 'TotalAmount' is the field in the order document
        
        return total_spent

    @staticmethod
    def serialize_user(user):
        """
        Convert a user document into a dictionary format for API responses or frontend rendering.
        """
        if user:
            print("Date of register", user.get("date_of_register",""))
            return {
                "id": str(user["_id"]),  # Convert ObjectId to string
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                "visited": user.get("visited", False),
                "created_at": user.get("date_of_register", ""),
                "last_order_date": user.get("last_order_date", ""),
                "orders_count": user.get("orders_count", 0),
                "loyalty_points": user.get("loyalty_points", 0),
                "address": user.get("address", ""),
                "phone_number": user.get("phone_number", ""),
                "profile_image": user.get("profile_image"),
                "status": MongoDBCustomers.assign_user_status(user),
                "total_orders": MongoDBCustomers.count_orders(user['_id']),  # Assign status
                "total_spent": MongoDBCustomers.calculate_total_spent(user['_id'])  # Calculate total spent
                # Add any other fields you want to include
            }
        
        return None

    @staticmethod
    def assign_user_status(user):
        """
        Assign a status to the user based on certain criteria.
        """
        # Ensure the user has the necessary fields
        loyalty_points = user.get("loyalty_points", 0)
        orders_count = user.get("total_orders", 0)
        created_at = user.get("date_of_register")
        last_order_date = user.get("last_order_date")

        # Example criteria for assigning status
        if loyalty_points > 100:
            return "VIP"
        elif orders_count > 5:
            return "loyal"
        elif created_at and (datetime.now() - created_at).days < 30:
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            return "new"
        elif last_order_date and (datetime.now() - last_order_date).days < 30:
            return "active"
        elif last_order_date and (datetime.now() - last_order_date).days >= 30:
            return "repeat"
        elif user.get("referral_code"):
            return "referral"
        else:
            return "inactive"

    @staticmethod
    def count_loyalty_points(user_id):
        """
        Count the loyalty points for a specific user.
        """
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return user.get("loyalty_points", 0) if user else 0

    @staticmethod
    def count_orders(user_id):
        """
        Count the number of orders placed by a specific user.
        """
        return orders_collection.count_documents({"UID": ObjectId(user_id)})

    @staticmethod
    def count_users():
        """
        Count the total number of registered users.
        """
        return users_collection.count_documents({})

    @staticmethod
    def count_users_with_cart():
        """
        Count the number of users who have items in their cart.
        """
        user_ids_with_cart = cart_collection.distinct("user_id", {"products": {"$exists": True, "$ne": []}})
        return len(user_ids_with_cart)

    @staticmethod
    def count_users_who_visited():
        """
        Count the number of users who have visited the site.
        """
        return users_collection.count_documents({"visited": True})

    @staticmethod
    def count_users_who_ordered():
        """
        Count the number of users who have ordered products.
        """
        return orders_collection.distinct("UID").count()

class MongoDBWishlist:
    @staticmethod
    def add_to_wishlist(user_id, product_id):
        """Add a product to the user's wishlist."""
        # Check if the item is already in the wishlist

        product = MongoDBProduct.get_product_by_id(product_id)
        if not product:
            return {"success": False, "message": "Product not found"}
        

        existing_item = wishlist_collection.find_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id)
            
        })

        if existing_item:
            return {"success": False, "message": "Item already in wishlist"}

        # Add the item to the wishlist
        wishlist_collection.insert_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id),
            "created_at": datetime.now()
        })

        return {"success": True, "message": "Product added to wishlist successfully."}

    @staticmethod
    def get_wishlist(user_id):
        """Fetch all wishlist items for a user with complete product details."""
        wishlist_items = wishlist_collection.find({"user_id": ObjectId(user_id)})
        
        # Prepare a list to hold the product details
        product_details = []
        
        for item in wishlist_items:
            product_id = item["product_id"]
            product = MongoDBProduct.get_product_by_id(product_id)  # Fetch product details
            
            if product:
                product_details.append(product)  # Append the complete product details
        
        return product_details  # Return the list of product details

    @staticmethod
    def remove_from_wishlist(user_id, product_id):
        """Remove a product from the user's wishlist."""
        result = wishlist_collection.delete_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id)
        })
        return result.deleted_count > 0  # Returns True if the item was removed

    @staticmethod
    def is_item_in_wishlist(user_id, product_id):
        """Check if a product is in the user's wishlist."""
        return wishlist_collection.find_one({
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id)
        }) is not None
    
    @staticmethod
    def get_product_ids_by_user(user_id):
        """Fetch a list of product IDs from the user's wishlist."""
        wishlist_items = wishlist_collection.find(
            {"user_id": ObjectId(user_id)},
            {"product_id": 1, "_id": 0}  # Only fetch the product_id field
        )
        return [str(item["product_id"]) for item in wishlist_items]
