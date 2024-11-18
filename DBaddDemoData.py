import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import random
import json

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
db_config = {
    'dbname': 'help',
    'user': 'helpthing',
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': 5432
}

def generate_random_demo_data():
    """Generate random demo data for the tables."""
    # Randomly generate users
    users_data = [
        (
            random.randint(1e15, 1e16 - 1),               # token
            random.randint(0, 1),                        # isCreator
            random.randint(0, 1),                        # hasDomain
            f"domain{random.randint(1, 100)}.com" if random.randint(0, 1) else None,  # domain
            random.randint(0, 10),                       # domainID
            round(random.uniform(0, 500), 2),            # balance
            f"4{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}",  # ccNumber
            f"{random.randint(1, 12):02d}/{random.randint(23, 30)}",  # ccValid
            random.randint(0, 1),                        # ccState
            f"Bank {random.choice(['A', 'B', 'C'])}",    # bankName
            f"CY17{random.randint(1000000000000000, 9999999999999999)}",  # bankIban
            json.dumps({"likes": [random.randint(1, 10) for _ in range(random.randint(1, 5))]})  # likes
        ) for _ in range(5)
    ]

    # Randomly generate helpitems
    helpitems_data = [
        (
            random.randint(1, 5),                        # creatorID
            random.randint(1, 5),                        # ownerID
            random.randint(1, 5),                        # chapterID
            random.randint(1, 3),                        # kind
            random.randint(0, 2),                        # state
            random.randint(0, 100),                      # voteup
            random.randint(0, 50),                       # votedown
            random.randint(0, 1),                        # uploadstate
            f"QR{random.randint(1, 1000):03d}",          # QR
            f"Demo Title {random.randint(1, 100)}",      # title
            f"Description {random.randint(1, 100)}",     # description
            random.choice(['English', 'French', 'Spanish']),  # language
            f"image{random.randint(1, 100)}.jpg",        # imagefn
            f"img{random.randint(1, 100)}",              # imageid
            f"video{random.randint(1, 100)}.mp4",        # videofn
            f"vid{random.randint(1, 100)}",              # videoid
            f"s{random.randint(1, 10):03d}.helpthing.com",  # host
            "Sample content",                            # content
            round(random.uniform(0, 100), 2),            # price
            round(random.uniform(0, 100), 2)             # budget
        ) for _ in range(5)
    ]

    # Randomly generate chapters
    chapters_data = [
        (
            random.randint(1, 5),                        # domainID
            random.choice([None, random.randint(1, 5)]), # parentID
            f"Chapter {random.randint(1, 100)}",         # title
            random.randint(0, 1),                        # enableVideo
            random.randint(0, 1),                        # enableImage
            random.randint(0, 1),                        # enableWiki
            random.randint(0, 1),                        # enableChat
            random.randint(0, 1),                        # enableExpert
            random.randint(0, 1),                        # enableAdd
            f"Playlist {random.randint(1, 100)}",        # playlist
            round(random.uniform(0, 500), 2)             # budget
        ) for _ in range(5)
    ]

    # Randomly generate experts
    experts_data = [
        (
            random.randint(1, 5),                        # chapterID
            random.randint(1, 5),                        # userID
            f"Expert {random.randint(1, 100)}",          # name
            f"Expert in field {random.randint(1, 100)}", # description
            f"Mon-Fri {random.randint(8, 12)}-{random.randint(1, 5)}",  # schedule
            random.choice(['English', 'French, Spanish', 'English, Italian']),  # languages
            random.choice(['online', 'offline']),        # online
            round(random.uniform(10, 100), 2),           # price
            round(random.uniform(0, 5), 1),              # ranking
            random.randint(0, 100),                      # jobs
            random.choice(['real', 'bot', 'AI']),        # type
            f"expert{random.randint(1, 100)}.jpg",       # url_image
            f"expert{random.randint(1, 100)}.mp4",       # url_video
            random.choice([True, False])                 # _active
        ) for _ in range(5)
    ]

    return users_data, helpitems_data, chapters_data, experts_data

def insert_demo_data():
    users_data, helpitems_data, chapters_data, experts_data = generate_random_demo_data()

    try:
        # Establish connection to the database
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Insert into tableUsers
        cursor.executemany('''
            INSERT INTO tableUsers (token, isCreator, hasDomain, domain, domainID, balance, ccNumber, ccValid, ccState, bankName, bankIban, likes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', users_data)
        connection.commit()
        print("Random demo data inserted into 'tableUsers'.")

        # Insert into tableHelpitems
        cursor.executemany('''
            INSERT INTO tableHelpitems (creatorID, ownerID, chapterID, kind, state, voteup, votedown, uploadstate, QR, title, description, language, imagefn, imageid, videofn, videoid, host, content, price, budget)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', helpitems_data)
        connection.commit()
        print("Random demo data inserted into 'tableHelpitems'.")

        # Insert into tableChapters
        cursor.executemany('''
            INSERT INTO tableChapters (domainID, parentID, title, enableVideo, enableImage, enableWiki, enableChat, enableExpert, enableAdd, playlist, budget)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', chapters_data)
        connection.commit()
        print("Random demo data inserted into 'tableChapters'.")

        # Insert into tableExperts
        cursor.executemany('''
            INSERT INTO tableExperts (chapterID, userID, name, description, schedule, languages, online, price, ranking, jobs, type, url_image, url_video, _active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', experts_data)
        connection.commit()
        print("Random demo data inserted into 'tableExperts'.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while inserting demo data: {error}")

    finally:
        # Close the cursor and the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    insert_demo_data()
