from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
from database import Database
import base64
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class User(BaseModel):
    email: str
    fam: str
    name: str
    otc: Optional[str] = None
    phone: str


class Coords(BaseModel):
    latitude: float
    longitude: float
    height: int


class Level(BaseModel):
    winter: Optional[str] = None
    summer: Optional[str] = None
    autumn: Optional[str] = None
    spring: Optional[str] = None


class Image(BaseModel):
    title: str
    data: str  # base64 encoded image


class Pereval(BaseModel):
    user: User
    coords: Coords
    beauty_title: str
    title: str
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    levels: Level
    images: List[Image]


class PerevalUpdate(BaseModel):
    coords: Optional[Coords] = None
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    levels: Optional[Level] = None
    images: Optional[List[Image]] = None


class PerevalResponse(BaseModel):
    id: int
    beauty_title: str
    title: str
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: datetime
    user: User
    coords: Coords
    levels: Level
    status: str
    images: Optional[List[Dict]] = None


# Метод для добавления данных
@app.post("/submitData/", status_code=status.HTTP_201_CREATED)
async def submit_data(pereval: Pereval):
    with Database() as db:
        try:
            # Добавляем пользователя
            user_id = db.add_user(
                email=pereval.user.email,
                fam=pereval.user.fam,
                name=pereval.user.name,
                otc=pereval.user.otc,
                phone=pereval.user.phone
            )
            if not user_id:
                raise HTTPException(status_code=400, detail="Failed to add user")

            # Добавляем координаты
            coord_id = db.add_coords(
                latitude=pereval.coords.latitude,
                longitude=pereval.coords.longitude,
                height=pereval.coords.height
            )
            if not coord_id:
                raise HTTPException(status_code=400, detail="Failed to add coordinates")

            # Добавляем перевал
            pereval_id = db.add_pereval(
                user_id=user_id,
                coord_id=coord_id,
                beauty_title=pereval.beauty_title,
                title=pereval.title,
                other_titles=pereval.other_titles,
                connect=pereval.connect,
                levels=pereval.levels.dict()
            )
            if not pereval_id:
                raise HTTPException(status_code=400, detail="Failed to add pereval")

            # Добавляем изображения
            for image in pereval.images:
                try:
                    image_data = base64.b64decode(image.data)
                except Exception as e:
                    print(f"Error decoding image: {e}")
                    continue

                image_id = db.add_image(
                    title=image.title,
                    data=image_data
                )
                if image_id:
                    db.link_image_to_pereval(pereval_id, image_id)

            return {
                "status": "success",
                "message": "Data added successfully",
                "pereval_id": pereval_id
            }

        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Метод для получения данных по ID
@app.get("/submitData/{pereval_id}", response_model=PerevalResponse)
async def get_pereval(pereval_id: int):
    with Database() as db:
        try:
            pereval = db.get_pereval_by_id(pereval_id)
            if not pereval:
                raise HTTPException(status_code=404, detail="Pereval not found")

            user = db.get_user_by_id(pereval['user_id'])
            coords = db.get_coords_by_id(pereval['coord_id'])
            levels = db.get_level_by_id(pereval['level_id'])
            images = db.get_images_for_pereval(pereval_id)

            return {
                "id": pereval['id'],
                "beauty_title": pereval['beauty_title'],
                "title": pereval['title'],
                "other_titles": pereval['other_titles'],
                "connect": pereval['connect'],
                "add_time": pereval['add_time'],
                "user": {
                    "email": user['email'],
                    "fam": user['fam'],
                    "name": user['name'],
                    "otc": user['otc'],
                    "phone": user['phone']
                },
                "coords": {
                    "latitude": coords['latitude'],
                    "longitude": coords['longitude'],
                    "height": coords['height']
                },
                "levels": {
                    "winter": levels['winter'],
                    "summer": levels['summer'],
                    "autumn": levels['autumn'],
                    "spring": levels['spring']
                },
                "status": pereval['status'],
                "images": [{"title": img['title'], "id": img['id']} for img in images] if images else None
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Метод для обновления данных
@app.patch("/submitData/{pereval_id}")
async def update_pereval(pereval_id: int, pereval_update: PerevalUpdate):
    with Database() as db:
        try:
            # Проверяем статус перевала
            pereval = db.get_pereval_by_id(pereval_id)
            if not pereval:
                raise HTTPException(status_code=404, detail="Pereval not found")

            if pereval['status'] != 'new':
                return {
                    "state": 0,
                    "message": "Запись нельзя редактировать, так как она уже прошла модерацию"
                }

            # Обновляем координаты если они есть
            if pereval_update.coords:
                db.update_coords(
                    coord_id=pereval['coord_id'],
                    latitude=pereval_update.coords.latitude,
                    longitude=pereval_update.coords.longitude,
                    height=pereval_update.coords.height
                )

            # Обновляем уровень сложности если он есть
            if pereval_update.levels:
                db.update_level(
                    level_id=pereval['level_id'],
                    winter=pereval_update.levels.winter,
                    summer=pereval_update.levels.summer,
                    autumn=pereval_update.levels.autumn,
                    spring=pereval_update.levels.spring
                )

            # Обновляем основные данные перевала
            update_data = {}
            if pereval_update.beauty_title is not None:
                update_data['beauty_title'] = pereval_update.beauty_title
            if pereval_update.title is not None:
                update_data['title'] = pereval_update.title
            if pereval_update.other_titles is not None:
                update_data['other_titles'] = pereval_update.other_titles
            if pereval_update.connect is not None:
                update_data['connect'] = pereval_update.connect

            if update_data:
                db.update_pereval(pereval_id, **update_data)

            # Обновляем изображения если они есть
            if pereval_update.images:
                # Удаляем старые изображения
                db.delete_images_for_pereval(pereval_id)

                # Добавляем новые
                for image in pereval_update.images:
                    try:
                        image_data = base64.b64decode(image.data)
                    except Exception as e:
                        print(f"Error decoding image: {e}")
                        continue

                    image_id = db.add_image(
                        title=image.title,
                        data=image_data
                    )
                    if image_id:
                        db.link_image_to_pereval(pereval_id, image_id)

            return {"state": 1}
        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                "state": 0,
                "message": str(e)
            }


# Метод для получения данных по email пользователя
@app.get("/submitData/")
async def get_perevals_by_email(user_email: str = Query(..., alias="user__email")):
    with Database() as db:
        try:
            user = db.get_user_by_email(user_email)
            if not user:
                return []

            perevals = db.get_perevals_by_user_id(user['id'])
            result = []

            for pereval in perevals:
                coords = db.get_coords_by_id(pereval['coord_id'])
                levels = db.get_level_by_id(pereval['level_id'])

                result.append({
                    "id": pereval['id'],
                    "beauty_title": pereval['beauty_title'],
                    "title": pereval['title'],
                    "other_titles": pereval['other_titles'],
                    "connect": pereval['connect'],
                    "add_time": pereval['add_time'],
                    "coords": {
                        "latitude": coords['latitude'],
                        "longitude": coords['longitude'],
                        "height": coords['height']
                    },
                    "levels": {
                        "winter": levels['winter'],
                        "summer": levels['summer'],
                        "autumn": levels['autumn'],
                        "spring": levels['spring']
                    },
                    "status": pereval['status']
                })

            return result
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)