# Technical Report - Book Metadata and Recommendation API

## 1. Introduction
This project is a SQL-backed RESTful API for managing books, users, and reviews, while also exposing analytics and recommendation endpoints. The goal was to build a data-driven web service that meets and exceeds the coursework requirements by combining clean CRUD design with realistic software engineering practices.

## 2. Problem selection and scope
I selected the domain of book metadata and recommendation because it provides a natural fit for relational modelling, CRUD operations, analytics, and user-personalised functionality. The project supports:
- CRUD operations for books
- user registration and login
- authenticated review creation and management
- aggregated analytics over stored book and review data
- rule-based recommendations based on a user's preferred genre

## 3. Technology stack and rationale
### FastAPI
FastAPI was selected because it is lightweight, API-first, and generates OpenAPI documentation automatically. This makes it particularly suitable for coursework where live demo quality and documentation clarity matter.

### SQLAlchemy
SQLAlchemy provides clear object-relational mapping and supports maintainable separation between data models and application logic.

### PostgreSQL
PostgreSQL is the recommended production database because the project data is relational and benefits from schema constraints, foreign keys, and strong SQL support. SQLite is retained as a local fallback for quick testing and portability.

### JWT authentication
JWT-based authentication was chosen because it represents an industry-standard pattern for stateless API security and demonstrates more advanced engineering than an entirely open API.

## 4. Architecture and design decisions
The application uses a layered structure:
- routers for endpoint definitions
- models for database entities
- schemas for request and response validation
- auth and dependency modules for security and shared logic

This modular structure improves readability, testing, and maintainability. It also supports stronger oral explanation because each responsibility is clearly separated.

## 5. Database design
The API uses three main relational entities:
- **users**: account holder information and hashed passwords
- **books**: bibliographic metadata and aggregate average rating
- **reviews**: many-to-one relationships to both users and books

This design supports both transactional CRUD operations and analytical queries. Foreign key constraints ensure referential integrity. A database-level check constraint enforces review ratings between 1 and 5.

## 6. API design choices
The API follows RESTful conventions through resource-oriented endpoints such as `/books`, `/users`, and `/reviews`. Responses are JSON-based. Status codes are intentionally aligned with HTTP conventions:
- `201` for successful creation
- `204` for deletion without body content
- `401` for failed authentication
- `403` when a user attempts to modify another user's review
- `404` when a resource does not exist

Filtering support on the books endpoint and analytics routes broaden the API beyond minimum CRUD.

## 7. Security approach
Although this coursework does not require enterprise-grade security, implementing JWT login materially improves the quality of the project. Passwords are hashed with bcrypt through Passlib. Protected routes require bearer tokens. Review ownership checks were added so that users can only update or delete their own reviews.

## 8. Testing strategy
Automated tests were written with pytest and FastAPI's TestClient. The tests cover:
- registration and login
- book CRUD
- analytics retrieval
- access control for review creation
- review updates and average rating recalculation

This test coverage demonstrates that the API behaves correctly in both happy-path and protected scenarios.

## 9. Challenges and lessons learned
One challenge was balancing project scope with demonstration value. A very small CRUD-only API would satisfy the minimum requirements but would not score highly in the oral exam. I therefore prioritised features that were easy to explain but also technically meaningful, such as authentication, analytics, modular architecture, and test automation.

Another challenge was handling derived values like average ratings. This was addressed by recalculating the aggregate rating each time a review is created, updated, or deleted.

## 10. Limitations and future work
The current recommendation engine is rule-based rather than machine-learning driven. Future extensions could include:
- collaborative filtering
- full-text search
- pagination and sorting for large datasets
- role-based access control
- containerised deployment with CI/CD
- richer analytics visualisation

## 11. Version control and deployment approach
The repository is structured to support staged commits covering project setup, models, routes, authentication, analytics, tests, and documentation. For deployment, the preferred approach is to host the API on Render or Railway with a managed PostgreSQL instance, while preserving a local SQLite fallback for exam resilience.

## 12. Generative AI declaration
I used Generative AI as a development support tool for:
- comparing suitable technology stacks
- drafting endpoint ideas
- generating initial boilerplate for documentation and import workflows
- reviewing testing coverage and report structure

All AI-generated suggestions were critically evaluated, modified, and integrated manually. Final decisions on architecture, endpoint behaviour, security, testing, and documentation were made by me. AI outputs were treated as drafts rather than authoritative solutions.

## 13. Conclusion
This API exceeds the basic pass requirements by combining a relational CRUD API with authentication, analytics, testing, and a professional documentation set. The design is deliberately chosen to support both technical quality and strong oral defence in the exam.
