from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, List
from database import Database
import base64
from fastapi.middleware.cors import CORSMiddleware

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)