import types

from app.main import app


def register_and_login(client):
    user = {"name": "Alice", "email": "alice@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=user).status_code == 201
    login = client.post("/auth/login", data={"username": user["email"], "password": user["password"]})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_book_crud_and_analytics(client):
    create = client.post("/books", json={
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "genre": "Software",
        "published_year": 2017,
        "average_rating": 0.0,
        "description": "Architecture patterns and design principles"
    })
    assert create.status_code == 201
    book_id = create.json()["id"]

    read = client.get(f"/books/{book_id}")
    assert read.status_code == 200
    assert read.json()["title"] == "Clean Architecture"

    update = client.put(f"/books/{book_id}", json={"genre": "Computer Science"})
    assert update.status_code == 200
    assert update.json()["genre"] == "Computer Science"

    analytics = client.get("/analytics/genre-distribution")
    assert analytics.status_code == 200
    assert analytics.json()[0]["count"] == 1

    delete = client.delete(f"/books/{book_id}")
    assert delete.status_code == 204


def test_review_requires_auth_and_updates_average(client):
    headers = register_and_login(client)
    book = client.post("/books", json={
        "title": "Deep Work",
        "author": "Cal Newport",
        "genre": "Productivity",
        "published_year": 2016,
        "average_rating": 0.0,
        "description": "Focus and concentration"
    }).json()

    unauth = client.post("/reviews", json={"book_id": book["id"], "rating": 5, "comment": "Great"})
    assert unauth.status_code == 401

    review = client.post("/reviews", headers=headers, json={"book_id": book["id"], "rating": 5, "comment": "Great"})
    assert review.status_code == 201
    review_id = review.json()["id"]

    book_after = client.get(f"/books/{book['id']}")
    assert book_after.json()["average_rating"] == 5.0

    updated = client.put(f"/reviews/{review_id}", headers=headers, json={"rating": 4})
    assert updated.status_code == 200
    assert updated.json()["rating"] == 4

    recommendations = client.get("/analytics/recommendations/1")
    assert recommendations.status_code == 200


def test_openapi_uses_framework_default_generation(client):
    assert isinstance(app.openapi, types.MethodType)
    assert app.openapi.__self__ is app

    schema = client.get(app.openapi_url).json()
    assert schema["openapi"] == app.openapi()["openapi"]
