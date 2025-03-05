import pymongo
from datetime import datetime, timedelta
import pytz
import random
import string
from SHOPNIQ.settings import MONGO_DB, MONGO_URI

IST = pytz.timezone("Asia/Kolkata")  # Indian Timezone

class MongoDBCoupons:
    def __init__(self, mongo_uri=MONGO_URI):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client['shopniq_db']
        self.collection = self.db["coupons"]

    def generate_coupons(self, count=50, discount="10%", validity_days=30):
        """Generate unique coupons and store in MongoDB."""
        coupons = []
        for _ in range(count):
            code = self.generate_unique_code()
            expiry_date = datetime.now(IST) + timedelta(days=validity_days)  # Convert to IST
            coupon = {
                "code": code,
                "discount": discount,
                "expiry_date": expiry_date,
                "is_used": False
            }
            self.collection.insert_one(coupon)
            coupons.append(code)
        return coupons

    def generate_unique_code(self, length=8):
        """Generate a human-readable, unique coupon code."""
        words = ["SAVE", "DEAL", "OFFER", "DISCOUNT", "LUCKY", "SPECIAL"]
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{random.choice(words)}{suffix}"

    def validate_coupon(self, code):
        """Check if a coupon is valid."""
        coupon = self.collection.find_one({"code": code})
        if not coupon:
            return {"status": "error", "message": "Invalid coupon code"}
        if coupon["is_used"]:
            return {"status": "error", "message": "Coupon already used"}
        
        expiry_date = coupon["expiry_date"].replace(tzinfo=pytz.UTC).astimezone(IST)  # Convert stored UTC time to IST
        if expiry_date < datetime.now(IST):
            return {"status": "error", "message": "Coupon expired"}
        
        return {"status": "success", "message": "Coupon is valid", "discount": coupon["discount"]}

    def redeem_coupon(self, code):
        """Mark a coupon as used."""
        coupon = self.collection.find_one({"code": code})
        if not coupon:
            return {"status": "error", "message": "Invalid coupon code"}
        if coupon["is_used"]:
            return {"status": "error", "message": "Coupon already used"}
        
        self.collection.update_one({"code": code}, {"$set": {"is_used": True}})
        return {"status": "success", "message": "Coupon redeemed successfully"}

    def delete_expired_coupons(self):
        """Remove expired coupons from the database."""
        self.collection.delete_many({"expiry_date": {"$lt": datetime.now(IST)}})
        return {"status": "success", "message": "Expired coupons deleted"}
