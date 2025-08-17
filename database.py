import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

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
                    winter_level, summer_level, autumn_level, spring_level, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'new')
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

    def get_pereval_by_id(self, pereval_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = sql.SQL("""
                SELECT * FROM pereval_added WHERE id = %s
            """)
            self.cursor.execute(query, (pereval_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting pereval by id: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = sql.SQL("""
                SELECT * FROM users WHERE id = %s
            """)
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None

    def get_coords_by_id(self, coord_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = sql.SQL("""
                SELECT * FROM coords WHERE id = %s
            """)
            self.cursor.execute(query, (coord_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting coordinates by id: {e}")
            return None

    def get_level_by_id(self, level_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = sql.SQL("""
                SELECT * FROM levels WHERE id = %s
            """)
            self.cursor.execute(query, (level_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting level by id: {e}")
            return None

    def get_images_for_pereval(self, pereval_id: int) -> Optional[List[Dict[str, Any]]]:
        try:
            query = sql.SQL("""
                SELECT i.id, i.title 
                FROM images i
                JOIN pereval_images pi ON i.id = pi.image_id
                WHERE pi.pereval_id = %s
            """)
            self.cursor.execute(query, (pereval_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting images for pereval: {e}")
            return None

    def update_coords(self, coord_id: int, latitude: float, longitude: float, height: int) -> bool:
        try:
            query = sql.SQL("""
                UPDATE coords 
                SET latitude = %s, longitude = %s, height = %s
                WHERE id = %s
            """)
            self.cursor.execute(query, (latitude, longitude, height, coord_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating coordinates: {e}")
            self.conn.rollback()
            return False

    def update_level(self, level_id: int, winter: str, summer: str, autumn: str, spring: str) -> bool:
        try:
            query = sql.SQL("""
                UPDATE levels 
                SET winter = %s, summer = %s, autumn = %s, spring = %s
                WHERE id = %s
            """)
            self.cursor.execute(query, (winter, summer, autumn, spring, level_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating level: {e}")
            self.conn.rollback()
            return False

    def update_pereval(self, pereval_id: int, **kwargs) -> bool:
        if not kwargs:
            return False

        try:
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(pereval_id)

            query = sql.SQL(f"""
                UPDATE pereval_added 
                SET {set_clause}
                WHERE id = %s
            """)
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating pereval: {e}")
            self.conn.rollback()
            return False

    def delete_images_for_pereval(self, pereval_id: int) -> bool:
        try:
            # Сначала получаем ID изображений для этого перевала
            self.cursor.execute("SELECT image_id FROM pereval_images WHERE pereval_id = %s", (pereval_id,))
            image_ids = [row[0] for row in self.cursor.fetchall()]

            if image_ids:
                # Удаляем связи
                self.cursor.execute("DELETE FROM pereval_images WHERE pereval_id = %s", (pereval_id,))
                # Удаляем сами изображения
                self.cursor.execute("DELETE FROM images WHERE id IN %s", (tuple(image_ids),))
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting images for pereval: {e}")
            self.conn.rollback()
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            query = sql.SQL("""
                SELECT * FROM users WHERE email = %s
            """)
            self.cursor.execute(query, (email,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def get_perevals_by_user_id(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        try:
            query = sql.SQL("""
                SELECT * FROM pereval_added WHERE user_id = %s
            """)
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting perevals by user id: {e}")
            return None