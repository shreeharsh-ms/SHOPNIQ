from pymongo import MongoClient
import bcrypt
from SHOPNIQ.settings import MONGO_DB
from bson import ObjectId
import pytz
import datetime as dt

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
db = MONGO_DB

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

orders_collection = MONGO_DB["orders"]

class MongoDBOrders:
    @staticmethod
    def place_order(user_id, items, total_amount, shipping_address, payment_status="Pending", transaction_id=None, estimated_delivery_days=5):
        """
        Places an order with multiple items and sets an estimated delivery date.
        """
        order_data = {
            "UID": ObjectId(user_id),  # User who placed the order
            "Items": [
                {
                    "PID": ObjectId(item["product_id"]),
                    "ProductName": item["product_name"],
                    "Quantity": item["quantity"],
                    "PricePerUnit": item["price_per_unit"],
                    "Subtotal": item["subtotal"]
                }
                for item in items
            ],
            "TotalAmount": total_amount,
            "ShippingAddress": shipping_address,  # User’s shipping address
            "Status": "Pending",  # Order status
            "PaymentStatus": payment_status,  # Payment status
            "TransactionID": transaction_id,  # Payment transaction ID
            "OrderDate": datetime.datetime.utcnow(),  # Order timestamp
            "EstimatedDelivery": datetime.datetime.utcnow() + datetime.timedelta(days=estimated_delivery_days),  # Estimated delivery date
            "Tracking": [],  # Stores tracking updates
            "RefundStatus": None,  # Tracks refund status if applicable
            "Cancelled": False  # Order cancellation flag
        }

        result = orders_collection.insert_one(order_data)
        return str(result.inserted_id)

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
        Converts the MongoDB order document into a dictionary format.
        """
        if order:
            return {
                "OrderID": str(order["_id"]),
                "UserID": str(order["UID"]),
                "TotalAmount": order["TotalAmount"],
                "ShippingAddress": order["ShippingAddress"],
                "Status": order["Status"],
                "PaymentStatus": order["PaymentStatus"],
                "TransactionID": order.get("TransactionID"),
                "OrderDate": order["OrderDate"],
                "EstimatedDelivery": order.get("EstimatedDelivery"),
                "RefundStatus": order.get("RefundStatus"),
                "Cancelled": order.get("Cancelled", False),
                "Tracking": order.get("Tracking", []),
                "Items": [
                    {
                        "ProductID": str(item["PID"]),
                        "ProductName": item["ProductName"],
                        "Quantity": item["Quantity"],
                        "PricePerUnit": item["PricePerUnit"],
                        "Subtotal": item["Subtotal"]
                    }
                    for item in order["Items"]
                ]
            }
        return None
    



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
        
        user_id = ObjectId(user_id)
        product_id = ObjectId(product_id)

        cart = MONGO_DB["cart"].find_one({"user_id": user_id})

        if cart:
            # Check if product already exists in the cart
            existing_product = next((item for item in cart["products"] if item["product_id"] == product_id), None)

            if existing_product:
                # Increase quantity
                db["cart"].update_one(
                    {"user_id": user_id, "products.product_id": product_id},
                    {"$inc": {"products.$.quantity": quantity}, "$set": {"updated_at": datetime.utcnow()}}
                )
            else:
                # Add new product
                db["cart"].update_one(
                    {"user_id": user_id},
                    {"$push": {"products": {"product_id": product_id, "quantity": quantity}},
                     "$set": {"updated_at": datetime.utcnow()}}
                )
        else:
            # Create new cart for the user
            new_cart = {
                "user_id": user_id,
                "products": [{"product_id": product_id, "quantity": quantity}],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            db["cart"].insert_one(new_cart)

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
