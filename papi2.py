import asyncpg
from fastapi import FastAPI, Form, File, UploadFile, Request
from pydantic import EmailStr
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql

from termcolor import colored




print('=== papi2 backend v0.02 =======================================================')
# Load environment variables from .env file
load_dotenv()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add initital logging info
LOG_FILE = '/var/log/helpthing.log'
with open(LOG_FILE, 'a') as f:
    f.write(f'{datetime.now()} - HELPthing backend v0.01 started\n')

def print_status(message: str, status_type: str):
    colors = {'success': 'green', 'error': 'red', 'info': 'blue'}
    print(colored(message, colors.get(status_type, 'white')))

def execute_query(query: str, params: tuple):
    db_config = {
        'dbname': 'help',
        'user': 'helpthing',
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': 5432
    }

    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    except Exception as e:
        print_status(f"Database error: {str(e)}", "error")
        return None


print('*** Setting up postgres database ***')
# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pw@localhost/papi2")
print("database url: ", DATABASE_URL)

# comment pooling method
# async def get_db_connection():
#     return await app.state.db_pool.acquire()
############################# Database Operations


############################################### EXPERT
# Function to get the database connection
async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


# /v1/experts/list - GET request to list all experts in a chapter
@app.get("/v1/experts/list")
async def list_experts(chapterID: int):
    print(1)
    query = """
        SELECT * FROM tableExperts WHERE chapterID = $1
    """
    print(2)
    conn = await get_db_connection()
    print(3)
    try:
        print(f"Getting experts for chapter {chapterID}")
        rows = await conn.fetch(query, chapterID)
        print(4)
        if not rows:
            return {"status": "No experts found for the given chapter"}

        print(5)
        experts = [dict(row) for row in rows]
        return JSONResponse(content=experts)
    except Exception as e:
        return JSONResponse(content={"status": f"error {str(e)}"})
    finally:
        await conn.close()


# /v1/experts/update - POST request to update an expert record
@app.post("/v1/experts/update")
async def update_expert(chapterID: int, recno: int, name: Optional[str] = None, description: Optional[str] = None,
                        languages: Optional[str] = None, online: Optional[str] = None, price: Optional[float] = None,
                        ranking: Optional[float] = None, jobs: Optional[int] = None, type: Optional[str] = None,
                        url_image: Optional[str] = None, url_video: Optional[str] = None,
                        enabled: Optional[bool] = None):
    params = [
        name, description, languages, online, price, ranking, jobs, type, url_image, url_video, enabled
    ]
    set_clauses = [
        f"{key} = ${idx + 1}" for idx, key in enumerate([
            'name', 'description', 'languages', 'online', 'price', 'ranking', 'jobs', 'type', 'url_image', 'url_video',
            'enabled'
        ]) if params[idx] is not None
    ]
    if not set_clauses:
        return JSONResponse(content={"status": "No fields to update"})

    query = f"""
        UPDATE tableExperts
        SET {', '.join(set_clauses)}
        WHERE chapterID = ${len(set_clauses) + 1} AND id = ${len(set_clauses) + 2};
    """
    params = [param for param in params if param is not None] + [chapterID, recno]

    conn = await get_db_connection()
    try:
        result = await conn.execute(query, *params)
        if result == "UPDATE 0":
            return JSONResponse(content={"status": "failed"})
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        return JSONResponse(content={"status": f"error {str(e)}"})
    finally:
        await conn.close()


# /v1/experts/create - POST request to create a new expert record
@app.post("/v1/experts/create")
async def create_expert(chapterID: int, name: Optional[str] = None, description: Optional[str] = None,
                        languages: Optional[str] = None,
                        online: Optional[str] = None, price: Optional[float] = None, ranking: Optional[float] = None,
                        jobs: Optional[int] = None, type: Optional[str] = None, url_image: Optional[str] = None,
                        url_video: Optional[str] = None, _active: Optional[bool] = None,
                        enabled: Optional[bool] = None):
    params = [
        chapterID, name, description, languages, online, price, ranking, jobs, type, url_image, url_video, _active,
        enabled
    ]
    columns = [
        key for key, value in zip([
            'chapterID', 'name', 'description', 'languages', 'online', 'price', 'ranking', 'jobs', 'type', 'url_image',
            'url_video', '_active', 'enabled'
        ], params) if value is not None
    ]
    placeholders = [f"${idx + 1}" for idx in range(len(columns))]

    query = f"""
        INSERT INTO tableExperts ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
    """
    params = [param for param in params if param is not None]

    conn = await get_db_connection()
    try:
        await conn.execute(query, *params)
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        return JSONResponse(content={"status": f"error {str(e)}"})
    finally:
        await conn.close()


# /v1/experts/delete - POST request to delete an expert record
@app.post("/v1/experts/delete")
async def delete_expert(chapterID: int, recno: int):
    query = """
        DELETE FROM tableExperts WHERE chapterID = $1 AND id = $2
    """
    conn = await get_db_connection()
    try:
        result = await conn.execute(query, chapterID, recno)
        if result == "DELETE 0":
            return JSONResponse(content={"status": "failed"})
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        return JSONResponse(content={"status": f"error {str(e)}"})
    finally:
        await conn.close()


# /v1/experts/read - GET request to read an expert record
@app.get("/v1/experts/read")
async def read_expert(chapterID: int, recno: int):
    query = """
        SELECT * FROM tableExperts WHERE chapterID = $1 AND id = $2
    """
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(query, chapterID, recno)
        if not row:
            return JSONResponse(content={"status": "No expert found"})
        return JSONResponse(content=dict(row))
    except Exception as e:
        return JSONResponse(content={"status": f"error {str(e)}"})
    finally:
        await conn.close()



########################## chapter
########################## chapter
########################## chapter
########################## chapter
########################## chapter
########################## chapter
########################## chapter


# Create chapter
@app.put("/v1/chapters/create")
async def create_chapter(
        domainID: Optional[int] = None,
        parentID: Optional[int] = None,
        title: Optional[str] = None,
        enableVideo: Optional[int] = 0,
        enableImage: Optional[int] = 0,
        enableWiki: Optional[int] = 0,
        enableChat: Optional[int] = 0,
        enableExpert: Optional[int] = 0,
        enableAdd: Optional[int] = 0,
        playlist: Optional[str] = None,
        budget: Optional[float] = None
):
    params = [
        domainID, parentID, title, enableVideo, enableImage, enableWiki, enableChat, enableExpert, enableAdd, playlist,
        budget
    ]
    columns = [
        key for key, value in zip([
            'domainID', 'parentID', 'title', 'enableVideo', 'enableImage', 'enableWiki', 'enableChat', 'enableExpert',
            'enableAdd', 'playlist', 'budget'
        ], params) if value is not None
    ]
    placeholders = [f"%s" for _ in columns]

    query = f"""
        INSERT INTO tableChapters ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        RETURNING chapterID;
    """
    params = [param for param in params if param is not None]

    result = execute_query(query, tuple(params))
    if result:
        chapter_id = result["chapterid"]
        print_status(f"Chapter {chapter_id} created successfully.", "success")
        return JSONResponse(content={"status": f"error {str(e)}"})
    return JSONResponse(content={"status": "error", "message": "Failed to create chapter"})


# Read chapter by ID
@app.get("/v1/chapters/read")
async def get_chapter(chapter_id: int):
    query = """
        SELECT * FROM tableChapters WHERE chapterID = %s;
    """
    result = execute_query(query, (chapter_id,))
    if result:
        print_status(f"Chapter {chapter_id} retrieved successfully.", "success")
        return {"status": "success", "data": result}
    print_status(f"Chapter {chapter_id} not found.", "info")
    return JSONResponse(content={"status": "error", "message": "Chapter not found"})


# List chapters by ID
@app.get("/v1/chapters/list")
async def list_chapters(chapter_id: Optional[int] = None):
    if chapter_id is not None:
        query = """
            SELECT * FROM tableChapters WHERE chapterID = %s;
        """
        params = (chapter_id,)
    else:
        query = """
            SELECT * FROM tableChapters;
        """
        params = ()

    try:
        cursor.execute(query, params)
        chapters = cursor.fetchall()
        if chapters:
            print_status("Chapters retrieved successfully.", "success")
            return {"status": "success", "data": chapters}
        print_status("No chapters found.", "info")
        return JSONResponse(content={"status": "error", "message": "No chapters found"})
    except Exception as e:
        print_status(f"Error retrieving chapters: {str(e)}", "error")
        return JSONResponse(content={"status": f"error {str(e)}"})


# Update chapter
@app.put("/v1/chapters/update")
async def update_chapter(
        chapter_id: int,
        domainID: Optional[int] = None,
        parentID: Optional[int] = None,
        title: Optional[str] = None,
        enableVideo: Optional[int] = None,
        enableImage: Optional[int] = None,
        enableWiki: Optional[int] = None,
        enableChat: Optional[int] = None,
        enableExpert: Optional[int] = None,
        enableAdd: Optional[int] = None,
        playlist: Optional[str] = None,
        budget: Optional[float] = None
):
    params = [
        domainID, parentID, title, enableVideo, enableImage, enableWiki, enableChat, enableExpert, enableAdd, playlist,
        budget
    ]
    fields_to_update = {
        key: value for key, value in zip([
            'domainID', 'parentID', 'title', 'enableVideo', 'enableImage', 'enableWiki', 'enableChat', 'enableExpert',
            'enableAdd', 'playlist', 'budget'
        ], params) if value is not None
    }

    if not fields_to_update:
        return JSONResponse(content={"status": "error", "message": "No fields to update"})

    set_clause = ", ".join([f"{key} = %s" for key in fields_to_update.keys()])
    query = f"""
        UPDATE tableChapters
        SET {set_clause}
        WHERE chapterID = %s
        RETURNING chapterID;
    """
    params = list(fields_to_update.values()) + [chapter_id]

    result = execute_query(query, tuple(params))
    if result:
        updated_chapter_id = result["chapterid"]
        print_status(f"Chapter {updated_chapter_id} updated successfully.", "success")
        return {"status": "success", "chapterID": updated_chapter_id}
    return JSONResponse(content={"status": "error", "message": "Failed to update chapter"})


# Delete chapter
@app.delete("/v1/chapters/delete")
async def delete_chapter(chapter_id: int):
    query = """
        DELETE FROM tableChapters WHERE chapterID = %s RETURNING chapterID;
    """
    result = execute_query(query, (chapter_id,))
    if result:
        deleted_chapter_id = result["chapterid"]
        print_status(f"Chapter {deleted_chapter_id} deleted successfully.", "success")
        return {"status": "success", "chapterID": deleted_chapter_id}
    print_status(f"Chapter {chapter_id} not found.", "info")
    return JSONResponse(content={"status": "error", "message": "Chapter not found or failed to delete"})


if __name__ == '__main__':
    uvicorn.run(app, port=8000)

