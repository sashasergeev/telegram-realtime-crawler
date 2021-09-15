# Telegram real time crawler by keywords

Telegram script that takes keywords and looks through new messages of followed channels to find matches. When match is found script looks in the database to find with which object (coin) this chat id is associated, so it could make relation and write all needed data to the database.
It also tracks changes of the price in 1hr and 2hrs range.

Script should be connected to the MySQL database, in which objects data is stored and it should be connected to your telegram account, in which channels should be associated with some object in the database. It created to fill the database for arregro website.

## How to run this script
1. You need to dl/clone this repository to your device.
2. Activate your virtualenv.
3. Run ```pip install -r requirements.txt``` in your shell.
4. Fill the telegram auth and database config data in the ```config.ini``` file.
5. Run the script.

The example of how your database data should have you can find in the ```data.csv```. 

This script is made for (arregro website)[https://github.com/sashasergeev/arregro-django/].