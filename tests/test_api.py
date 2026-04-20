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
    recommendation_candidate = client.post("/books", json={
        "title": "The Focus Formula",
        "author": "Jordan Pace",
        "genre": "Productivity",
        "published_year": 2019,
        "average_rating": 4.7,
        "ratings_count": 80000,
        "language_code": "eng",
        "source": "goodbooks-10k",
        "description": "Popular productivity title"
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
    recommendation_payload = recommendations.json()
    assert "rationale" in recommendation_payload
    assert recommendation_payload["preference_summary"][0]["genre"] == "Productivity"
    assert recommendation_payload["recommendations"][0]["id"] == recommendation_candidate["id"]
    assert recommendation_payload["recommendations"][0]["score"] > 0
    assert recommendation_payload["recommendations"][0]["reasons"]


def test_book_filters_sorting_and_empty_update_validation(client):
    client.post("/books", json={
        "title": "Python Patterns",
        "author": "Alex Dev",
        "genre": "Software",
        "published_year": 2020,
        "average_rating": 4.6,
        "description": "Design patterns in Python"
    })
    client.post("/books", json={
        "title": "Quiet Focus",
        "author": "Alex Writer",
        "genre": "Productivity",
        "published_year": 2018,
        "average_rating": 3.8,
        "description": "Deep concentration strategies"
    })
    client.post("/books", json={
        "title": "Data Stories",
        "author": "Jamie Analyst",
        "genre": "Data",
        "published_year": 2024,
        "average_rating": 4.9,
        "description": "Analytics storytelling"
    })

    filtered = client.get("/books", params={
        "search": "Alex",
        "min_rating": 4.0,
        "sort_by": "average_rating",
        "sort_order": "desc",
    })
    assert filtered.status_code == 200
    payload = filtered.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Python Patterns"

    metadata_filtered = client.get("/books", params={
        "language_code": "eng",
        "source": "goodbooks-10k",
        "min_ratings_count": 1000,
    })
    assert metadata_filtered.status_code == 200
    assert metadata_filtered.json() == []

    paged = client.get("/books", params={"sort_by": "published_year", "sort_order": "asc", "skip": 1, "limit": 1})
    assert paged.status_code == 200
    assert len(paged.json()) == 1
    assert paged.json()[0]["title"] == "Python Patterns"

    create = client.post("/books", json={
        "title": "Refactoring APIs",
        "author": "Mia Engineer",
        "genre": "Software",
        "published_year": 2022,
        "average_rating": 0.0,
        "ratings_count": 2500,
        "isbn13": "9780134757599",
        "language_code": "eng",
        "source": "goodbooks-10k",
        "description": "API improvement techniques"
    })
    book_id = create.json()["id"]
    empty_update = client.put(f"/books/{book_id}", json={})
    assert empty_update.status_code == 400

    metadata_check = client.get("/books", params={"source": "goodbooks-10k", "language_code": "eng", "min_ratings_count": 2000})
    assert metadata_check.status_code == 200
    assert metadata_check.json()[0]["isbn13"] == "9780134757599"

    sorted_by_popularity = client.get("/books", params={"sort_by": "ratings_count", "sort_order": "desc", "limit": 1})
    assert sorted_by_popularity.status_code == 200
    assert sorted_by_popularity.json()[0]["ratings_count"] == 2500


def test_duplicate_review_for_same_book_is_rejected(client):
    headers = register_and_login(client)
    book = client.post("/books", json={
        "title": "API Security",
        "author": "Sam Secure",
        "genre": "Security",
        "published_year": 2025,
        "average_rating": 0.0,
        "description": "Protecting modern APIs"
    }).json()

    first_review = client.post("/reviews", headers=headers, json={"book_id": book["id"], "rating": 5, "comment": "Very useful"})
    assert first_review.status_code == 201

    duplicate_review = client.post("/reviews", headers=headers, json={"book_id": book["id"], "rating": 4, "comment": "Second review"})
    assert duplicate_review.status_code == 409


def test_review_filters_permissions_and_user_profile(client):
    alice_headers = register_and_login(client)
    bob = {"name": "Bob", "email": "bob@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=bob).status_code == 201
    bob_login = client.post("/auth/login", data={"username": bob["email"], "password": bob["password"]})
    bob_headers = {"Authorization": f"Bearer {bob_login.json()['access_token']}"}

    book_one = client.post("/books", json={
        "title": "Advanced APIs",
        "author": "Dana Architect",
        "genre": "Software",
        "published_year": 2023,
        "average_rating": 0.0,
        "description": "Building resilient APIs"
    }).json()
    book_two = client.post("/books", json={
        "title": "Learning SQL",
        "author": "Chris Query",
        "genre": "Data",
        "published_year": 2021,
        "average_rating": 0.0,
        "description": "SQL foundations"
    }).json()

    review_one = client.post("/reviews", headers=alice_headers, json={"book_id": book_one["id"], "rating": 5, "comment": "Excellent"})
    assert review_one.status_code == 201
    review_two = client.post("/reviews", headers=alice_headers, json={"book_id": book_two["id"], "rating": 4, "comment": "Great intro"})
    assert review_two.status_code == 201

    filtered_reviews = client.get("/reviews", params={"user_id": 1, "min_rating": 5})
    assert filtered_reviews.status_code == 200
    assert len(filtered_reviews.json()) == 1
    assert filtered_reviews.json()[0]["rating"] == 5

    forbidden_update = client.put(f"/reviews/{review_one.json()['id']}", headers=bob_headers, json={"rating": 1})
    assert forbidden_update.status_code == 403

    empty_review_update = client.put(f"/reviews/{review_one.json()['id']}", headers=alice_headers, json={})
    assert empty_review_update.status_code == 400

    profile = client.get("/analytics/user-profile/1")
    assert profile.status_code == 200
    profile_json = profile.json()
    assert profile_json["review_count"] == 2
    assert profile_json["preferred_genres"][0]["genre"] == "Software"
    assert len(profile_json["recent_reviews"]) == 2

    me = client.get("/users/me", headers=alice_headers)
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"


def test_metadata_analytics_endpoints(client):
    client.post("/books", json={
        "title": "Data Warehouse",
        "author": "Ana Data",
        "genre": "Data",
        "published_year": 2022,
        "average_rating": 4.6,
        "ratings_count": 12000,
        "language_code": "eng",
        "source": "goodbooks-10k",
        "description": "Analytics engineering guide"
    })
    client.post("/books", json={
        "title": "Hidden Signals",
        "author": "Leo Reader",
        "genre": "Mystery",
        "published_year": 2014,
        "average_rating": 3.7,
        "ratings_count": 3000,
        "language_code": "spa",
        "source": "manual",
        "description": "Mystery novel"
    })
    client.post("/books", json={
        "title": "Legend Falls",
        "author": "Mira Tale",
        "genre": "Fantasy",
        "published_year": 2008,
        "average_rating": 4.8,
        "ratings_count": 64000,
        "language_code": "eng",
        "source": "goodbooks-10k",
        "description": "Fantasy epic"
    })

    languages = client.get("/analytics/language-distribution")
    assert languages.status_code == 200
    assert languages.json()[0]["language_code"] == "eng"

    sources = client.get("/analytics/source-distribution")
    assert sources.status_code == 200
    assert sources.json()[0]["source"] == "goodbooks-10k"

    rating_bands = client.get("/analytics/rating-bands")
    assert rating_bands.status_code == 200
    bands = {item["band"]: item["count"] for item in rating_bands.json()}
    assert bands["4_5_and_above"] == 2
    assert bands["3_to_4"] == 1

    author_performance = client.get("/analytics/author-performance")
    assert author_performance.status_code == 200
    assert author_performance.json()[0]["average_rating"] >= author_performance.json()[-1]["average_rating"]

    decade_distribution = client.get("/analytics/publication-decade-distribution")
    assert decade_distribution.status_code == 200
    decades = {item["decade"]: item["count"] for item in decade_distribution.json()}
    assert decades["2000s"] == 1
    assert decades["2010s"] == 1
    assert decades["2020s"] == 1


def test_auth_validation_and_duplicate_registration(client):
    short_password = client.post("/auth/register", json={
        "name": "Tiny Password",
        "email": "tiny@example.com",
        "password": "short",
    })
    assert short_password.status_code == 422

    user = {"name": "Repeat User", "email": "repeat@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=user).status_code == 201
    duplicate = client.post("/auth/register", json=user)
    assert duplicate.status_code == 400


def test_openapi_uses_framework_default_generation(client):
    assert isinstance(app.openapi, types.MethodType)
    assert app.openapi.__self__ is app

    schema = client.get(app.openapi_url).json()
    assert schema["openapi"] == app.openapi()["openapi"]
