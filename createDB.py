import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Check if required environment variables are set
def check_env_variables():
    required_vars = ['DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Perform the check
check_env_variables()

# Database connection parameters
db_config = {
    'dbname': 'help',
    'user': 'helpthing',
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': 5432
}

def create_table():
    try:
        # Establish connection to the database
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS tableUsers (
            userID        SERIAL PRIMARY KEY,
            token         BIGINT,
            isCreator     INT DEFAULT 0,
            hasDomain     INT DEFAULT 0,
            domain        VARCHAR(100),
            domainID      INT DEFAULT 0,
            balance       NUMERIC,
            ccNumber      VARCHAR(30),
            ccValid       VARCHAR(30),
            ccState       INT DEFAULT 0,              -- credit card validity status
            bankName      VARCHAR(100),
            bankIban      VARCHAR(30),
            likes         JSON              -- JSON structure for chapterID and likes
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'tableUsers' created successfully or already exists.")


        #drop table tableHelpitems
        if False:
            cursor.execute("DROP TABLE IF EXISTS tableHelpitems;")
            connection.commit()
            print("Table 'tableHelpitems' dropped successfully.")

        # Create table tableHelpitems
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS tableHelpitems (
            itemID        SERIAL PRIMARY KEY,
            creatorID     INT,   --  reference to creator in tableUsers
            ownerID       INT,   --  reference to owner in tableUsers
            chapterID     INT,   --  reference to tableChapter
            kind          INT DEFAULT 0,                                 -- 1=video, 2=image, 3=text
            state         INT DEFAULT 0,
            voteup        INT DEFAULT 0,                       -- Count of upvotes
            votedown      INT DEFAULT 0,                       -- Count of downvotes
            uploadstate   INT DEFAULT 0,                                 -- Tracks if item requires upload to host
            QR            VARCHAR(100),
            title         VARCHAR(100),
            description   VARCHAR(100),
            language      VARCHAR(100),
            imagefn       VARCHAR(100),
            imageid       VARCHAR(100),
            videofn       VARCHAR(100),                        -- URL or path to video file
            videoid       VARCHAR(100),                        -- cloudflare ID
            host          VARCHAR(100),                        -- e.g., s001.helpthing.com
            content       TEXT,
            price         NUMERIC,
            budget        NUMERIC                              -- Domain owner budget; if 0, item becomes premium
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'tableHelpitems' created successfully or already exists.")

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS tableChapters (
            chapterID     SERIAL PRIMARY KEY,
            domainID      INT ,  --key to domain ID in tableUsers, if applicable
            parentID      INT,                                  -- ID of the parent chapter, if applicable
            title         VARCHAR(100),
            enableVideo   INT DEFAULT 0,                        -- Flag to enable/disable video content
            enableImage   INT DEFAULT 0,                        -- Flag to enable/disable image content
            enableWiki    INT DEFAULT 0,                        -- Flag to enable/disable wiki content
            enableChat    INT DEFAULT 0,                        -- Flag to enable/disable chat functionality
            enableExpert  INT DEFAULT 0,                        -- Flag to enable/disable expert content
            enableAdd     INT DEFAULT 0,                        -- Flag to allow users to add content
            playlist      TEXT,                                 -- Default playlist for the chapter
            budget        NUMERIC                               -- Budget for chapter; if 0, it becomes premium
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'tableChapters' created successfully or already exists.")

        create_table_query = '''
        CREATE TABLE tableExperts (
            id SERIAL PRIMARY KEY,
            chapterID INTEGER,              --to  chapterID in tableChapters
            userID INTEGER,                 -- to userID in tableUsers
            name VARCHAR(255) NOT NULL,
            description TEXT,    
            schedule TEXT,                  -- future
            languages VARCHAR(255),         -- Comma separated list of languages  -- You could use an array if you prefer: TEXT[]
            online VARCHAR(10),             -- Enum-like column for status
            price NUMERIC(10, 2),           -- Price per minute with 2 decimal places
            ranking DECIMAL(2, 1),          -- Rating from 0 to 5 stars, allowing 1 decimal place
            jobs INTEGER DEFAULT 0,         -- Number of jobs completed, defaulting to 0
            type VARCHAR(10),               -- Type of expert: real, bot, or AI
            url_image VARCHAR(128),         -- URL of the title image
            url_video VARCHAR(128),         -- future
            _active BOOLEAN DEFAULT TRUE,   -- Indicates if the entry is active  -- URL of the video    _active BOOLEAN DEFAULT TRUE,  -- Indicates if the entry is active
            _cdt TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation date and time
        );

        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'tableExperts' created successfully or already exists.")


    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while creating the table: {error}")

    finally:
        # Close the cursor and the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    create_table()
