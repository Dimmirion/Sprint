import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('FSTR_DB_HOST'),
                port=os.getenv('FSTR_DB_PORT'),
                dbname=os.getenv('FSTR_DB_NAME'),
                user=os.getenv('FSTR_DB_LOGIN'),
                password=os.getenv('FSTR_DB_PASS')
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def add_user(self, email: str, fam: str, name: str, otc: str, phone: str) -> Optional[int]:
        try:
            query = sql.SQL("""
                INSERT INTO users (email, fam, name, otc, phone)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """)
            self.cursor.execute(query, (email, fam, name, otc, phone))
            user_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return user_id
        except Exception as e:
            print(f"Error adding user: {e}")
            self.conn.rollback()
            return None

    def add_coords(self, latitude: float, longitude: float, height: int) -> Optional[int]:
        try:
            query = sql.SQL("""
                INSERT INTO coords (latitude, longitude, height)
                VALUES (%s, %s, %s)
                RETURNING id
            """)
            self.cursor.execute(query, (latitude, longitude, height))
            coord_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return coord_id
        except Exception as e:
            print(f"Error adding coordinates: {e}")
            self.conn.rollback()
            return None

    def add_pereval(self, user_id: int, coord_id: int, beauty_title: str, title: str,
                    other_titles: str, connect: str, levels: Dict[str, str]) -> Optional[int]:
        try:
            query = sql.SQL("""
                INSERT INTO pereval_added (
                    user_id, coord_id, beauty_title, title, other_titles, connect,
                    winter_level, summer_level, autumn_level, spring_level
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """)
            self.cursor.execute(query, (
                user_id, coord_id, beauty_title, title, other_titles, connect,
                levels.get('winter'), levels.get('summer'),
                levels.get('autumn'), levels.get('spring')
            ))
            pereval_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return pereval_id
        except Exception as e:
            print(f"Error adding pereval: {e}")
            self.conn.rollback()
            return None

    def add_image(self, title: str, data: bytes) -> Optional[int]:
        try:
            query = sql.SQL("""
                INSERT INTO images (title, data)
                VALUES (%s, %s)
                RETURNING id
            """)
            self.cursor.execute(query, (title, data))
            image_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return image_id
        except Exception as e:
            print(f"Error adding image: {e}")
            self.conn.rollback()
            return None

    def link_image_to_pereval(self, pereval_id: int, image_id: int) -> bool:
        try:
            query = sql.SQL("""
                INSERT INTO pereval_images (pereval_id, image_id)
                VALUES (%s, %s)
            """)
            self.cursor.execute(query, (pereval_id, image_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error linking image to pereval: {e}")
            self.conn.rollback()
            return False