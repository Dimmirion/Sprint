import pytest
from database import Database


def test_add_user():
    with Database() as db:
        user_id = db.add_user(
            email="test_db@example.com",
            fam="Тестов",
            name="БД",
            otc="Тест",
            phone="+79990001122"
        )
        assert user_id is not None

        user = db.get_user_by_id(user_id)
        assert user["email"] == "test_db@example.com"


def test_add_pereval():
    with Database() as db:
        user_id = db.add_user(
            email="pereval_test@example.com",
            fam="Тестов",
            name="Перевал",
            otc="Тест",
            phone="+79990001133"
        )

        coord_id = db.add_coords(
            latitude=45.1111,
            longitude=90.1111,
            height=1500
        )

        pereval_id = db.add_pereval(
            user_id=user_id,
            coord_id=coord_id,
            beauty_title="пер. тест",
            title="Тест БД",
            other_titles="Тестовый перевал",
            connect="",
            levels={"winter": "1A", "summer": "1A", "autumn": "1A", "spring": "1A"}
        )

        assert pereval_id is not None

        pereval = db.get_pereval_by_id(pereval_id)
        assert pereval["title"] == "Тест БД"