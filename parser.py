import configparser
from datetime import datetime
import asyncio
import re

from telethon import TelegramClient, events
import mysql.connector

# IMPORT CONFIG FILE
settings = configparser.ConfigParser()
settings.read("config.ini")

# TELEGRAM AUTH
api_id = settings.get("TELEGRAM", "API_ID")
api_hash = settings.get("TELEGRAM", "API_HASH")
client = TelegramClient("me", api_id, api_hash)

# DB CONNECTION (MySQL)
mydb = mysql.connector.connect(
    host=settings.get("DATABASE", "HOST"),
    user=settings.get("DATABASE", "USER"),
    password="",  # if you have password, uncomment and change value with: settings.get("DATABASE", "PASSWORD"),
    database=settings.get("DATABASE", "DATABASE"),
)
mycursor = mydb.cursor()

# REGEX FOR KEYWORDS
keywordsRegex = re.compile(
    r"announcement|integrates|update|cooperation|launch|testnet|"
    r"partnership|announce|listing|listed|list|lists|airdrop|mainnet",
    re.I,
)


# OBTAINING GENERAL DATA
def get_coin_name(chat_id):
    sql = "Select name from news_coin WHERE tg_id = %s"
    tg_id = (chat_id,)
    mycursor.execute(sql, tg_id)
    return mycursor.fetchall()[0][0]


def get_info(event):
    chat_id = event.chat_id
    coin_name = get_coin_name(chat_id)  # get name of the coin
    tags = keywordsRegex.findall(event.raw_text)
    tags = list(set([str(elem.lower()) for elem in tags]))
    return coin_name, tags


# DATABASE RELATED FUNCTIONS
def get_coin_id(coin_name):
    sql = "SELECT id from news_coin WHERE name = %s"
    mycursor.execute(sql, (coin_name,))
    return mycursor.fetchall()[0][0]


def get_coin_price(coin_id):
    sql = "SELECT price from news_pricedynamic WHERE coin_id = %s"
    mycursor.execute(sql, (coin_id,))
    return mycursor.fetchall()[0][0]


def insert_tags(tags, post_id):
    for i in tags:
        sql = "SELECT id from news_tag WHERE tag = %s"
        tag = (i,)
        mycursor.execute(sql, tag)
        result = mycursor.fetchall()  # get the id of the tag
        sql = "INSERT INTO news_post_tag (post_id, tag_id) VALUES (%s, %s)"
        val = (post_id, result[0][0])
        mycursor.execute(sql, val)
        mydb.commit()  # insert m2m relation


def write_db(coin_name, tags, message):
    coin_id = get_coin_id(coin_name)
    price = get_coin_price(coin_id)
    sql = "INSERT INTO news_post (message, coin_id, date_added, price) VALUES (%s, %s, %s, %s)"
    val = (message, coin_id, datetime.now(), price)
    mycursor.execute(sql, val)
    mydb.commit()
    post_id = mycursor.lastrowid
    insert_tags(tags, post_id)
    return post_id, coin_id


# WRITING PRICE CHANGES THROUGH TIME
async def priceChange(post_id, coin_id):
    await asyncio.sleep(3600)  # price change 1hr after news
    sql = "UPDATE news_post SET price1hr = %s WHERE id = %s"
    val = (get_coin_price(coin_id), post_id)
    mycursor.execute(sql, val)
    mydb.commit()
    await asyncio.sleep(3600)  # price change 2hr after news
    sql = "UPDATE news_post SET price2hr = %s WHERE id = %s"
    val = (get_coin_price(coin_id), post_id)
    mycursor.execute(sql, val)
    mydb.commit()


# TRACK MESSAGES
@client.on(events.NewMessage)
async def my_event_handler(event):
    if not keywordsRegex.search(event.raw_text) is None:
        coin_name, tags = get_info(event)
        post_id, coin_id = write_db(coin_name, tags, event.raw_text)
        await priceChange(post_id, coin_id)


# RUNNING SCRIPT
with client:
    client.run_until_disconnected()
