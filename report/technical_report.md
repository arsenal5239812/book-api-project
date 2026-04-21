# Technical Report

## 1. Project overview
This coursework implements a SQL-backed FastAPI application for book metadata, reviews, analytics, recommendation, and similar-book discovery. The starting point matched the module's suggested idea of a book metadata and recommendation API, but the final system was extended beyond basic CRUD in three ways:

- integration of the public `goodbooks-10k` dataset
- an explainable recommendation and discovery layer
- a provenance and AI-transparency model for reader trust preferences

Repository and deliverable links:
- GitHub repository: <https://github.com/arsenal5239812/book-api-project>
- API documentation PDF: <https://github.com/arsenal5239812/book-api-project/blob/main/docs/api_documentation.pdf>
- Presentation slides: <https://github.com/arsenal5239812/book-api-project/blob/main/slides/book_api_project_slides.pptx>

## 2. Technology stack and rationale
The implementation uses Python, FastAPI, SQLAlchemy, Alembic, JWT authentication, and SQLite/PostgreSQL.

FastAPI was chosen because it supports rapid API development, strong request validation through Pydantic, and automatic OpenAPI generation, which is useful both for development and for coursework documentation. SQLAlchemy was selected because the project needed structured relational modelling together with custom query logic for analytics, recommendation, and provenance-aware filtering.

SQLite is the default local database because it is simple to run during development and oral demonstration. PostgreSQL remains the more production-style option for hosted deployment. JWT authentication was used because it is lightweight, widely recognised, and suitable for a stateless API with protected review operations.

Alembic was introduced once the schema became more complex. Early development could rely on direct table creation, but later changes added richer metadata and provenance fields to the `Book` model. Alembic therefore became the cleaner way to manage schema evolution and defend database design choices.

## 3. Architecture and design
The codebase is separated into models, schemas, routers, configuration, scripts, and migrations. This structure was intentionally chosen so that:

- models define the relational structure
- schemas control request and response validation
- routers contain HTTP behaviour
- configuration remains separate from business logic
- scripts handle operational tasks such as dataset import
- migrations provide reproducible schema change management

This modular approach made the project easier to extend. For example, the provenance layer required changes across the data model, validation layer, analytics, recommendation logic, and tests, but these changes remained manageable because the codebase already had clear boundaries.

## 4. Public dataset integration
The main public dataset is `goodbooks-10k`, referenced through both Kaggle and the upstream project source:

- [Kaggle goodbooks-10k](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k)
- [Upstream source](https://github.com/zygmuntz/goodbooks-10k)

The importer processes `books.csv`, `tags.csv`, and `book_tags.csv`. It maps tag information into coursework-friendly genres and stores additional metadata such as `ratings_count`, `isbn13`, `language_code`, and `source`. This was important because a tiny hand-written dataset would not have supported meaningful filtering, analytics, or recommendation behaviour.

The public dataset also shaped a key design decision: it provides book metadata and reader signals, but it does not provide provenance or AI-transparency labels. Instead of pretending those fields already exist in the dataset, the project treats public catalogue metadata and governance-style provenance metadata as separate layers.

## 5. Advanced features
The strongest extension beyond a standard book API is the provenance and AI-transparency model. Books can now store:

- `origin_type`
- `source_platform`
- `original_language`
- `translation_status`
- `creation_disclosure`
- `disclosure_source`
- `moderation_status`
- `ai_risk_score`
- `provenance_notes`

These fields support provenance-aware filtering and analytics, but more importantly they feed into recommendation and similar-book discovery. The recommendation endpoint combines user review history, genre affinity, language affinity, average rating, popularity, and provenance metadata. It also supports a `content_preference` parameter with values such as `human_only`, `allow_ai_assisted`, and `any`.

This design choice was deliberate. Rather than claiming that the system can automatically determine whether content is AI-generated, the API implements a governance-oriented approach: provenance disclosure, moderation status, risk signalling, and reader choice.

The same idea was then extended into `GET /books/{book_id}/similar`, which provides provenance-aware similar-book discovery. This endpoint uses similarity factors such as genre, language, publication era, origin type, translation status, disclosure type, moderation state, and AI risk score. As a result, the project supports both personalised recommendation and title-based exploration.

## 6. Security, testing, and engineering quality
The project includes practical engineering safeguards rather than only minimal coursework functionality. Examples include:

- password hashing before persistence
- JWT bearer-token authentication
- protected review creation, editing, and deletion
- ownership checks for user-generated reviews
- duplicate-review prevention
- rejection of empty update payloads
- conventional HTTP status codes such as `401`, `403`, `404`, `409`, and `422`

Testing was treated as part of the design process, not as an afterthought. The test suite covers CRUD, authentication, ownership rules, analytics, provenance updates, recommendation modes, similar-book discovery, importer behaviour, and Alembic migration smoke validation. This matters because the project evolved substantially over time; regression risk increased as each advanced feature was added.

At the time of final preparation, the local automated suite contains fifteen passing tests. Those tests are not limited to happy-path behaviour. They also check:

- duplicate review rejection
- empty update rejection
- unauthorised access
- provenance-filter correctness
- preference-aware differences in recommendation and discovery
- migration success on a clean database

This level of test coverage was important because the project theme became more ambitious than a typical coursework CRUD API. Once provenance-aware discovery and migration-driven schema control were introduced, the project needed stronger regression protection to remain credible.

Alembic also strengthened the engineering quality of the submission. Instead of rebuilding the database manually after every schema change, the project now uses a migration workflow that better reflects real API development practice.

## 7. API documentation and presentation strategy
The supporting deliverables were designed to reinforce the implementation rather than exist separately from it. FastAPI's OpenAPI generation made it possible to keep the API documentation aligned with the actual endpoints, while the manually prepared PDF documentation adds curated examples, authentication guidance, error-code explanations, and coverage of the most distinctive endpoints such as provenance updates and similar-book discovery.

The oral presentation strategy also follows the technical design of the project. Instead of demonstrating every endpoint, the presentation is built around one coherent live pathway:

1. show public dataset integration
2. show provenance metadata being applied to a title
3. show provenance-aware filtering and analytics
4. show recommendation with reader content preference
5. finish with provenance-aware similar-book discovery

This presentation design is intentional. It highlights the strongest originality in the project and makes it easier to defend design choices during Q&A because every major component appears in a single narrative flow.

## 8. Version control and iterative development
Version control was treated as part of the project evidence, not just a storage mechanism. The public GitHub repository records a sequence of changes from an earlier baseline API into the final provenance-aware discovery platform. This matters because the brief explicitly states that examiners will inspect commit history and version-control practice.

The commit history demonstrates that the project evolved in stages rather than appearing as a single final upload. Earlier iterations focused on getting the core API running locally with authentication, reviews, and testing. Later commits introduced dataset integration, recommendation improvements, provenance metadata, migration support, and final submission materials. This staged development makes it easier to explain design decisions in the oral examination because each significant feature can be linked to an identifiable phase of development.

This iterative workflow also reduced risk. By committing after major milestones and repeatedly re-running tests, the project was less likely to break silently while new features were added. In practice, version control supported both traceability and confidence: traceability for the examiners, and confidence for the student during refactoring and feature expansion.

## 9. Key endpoint evidence
Although the API contains a broad range of endpoints, a smaller subset best demonstrates the project’s technical quality and originality:

- `GET /books` shows advanced filtering, sorting, pagination, and provenance-aware search
- `PUT /books/{book_id}/provenance` demonstrates the governance metadata layer
- `GET /analytics/recommendations/{user_id}` shows explainable, preference-aware recommendation
- `GET /books/{book_id}/similar` demonstrates provenance-aware discovery
- provenance analytics endpoints show how the API supports transparency reporting rather than only CRUD operations

This subset is important because it shows how the project moved from a basic database-backed API to a more coherent trust-aware discovery system. In other words, the strongest evidence of quality is not any single endpoint, but the way these endpoints work together: public dataset import, provenance update, provenance filtering, recommendation, discovery, and analytics all reinforce the same design theme.

## 10. Trade-offs and rejected alternatives
An important part of the implementation was deciding what not to build. Two alternatives were considered but deliberately not adopted in the final version.

The first was a machine-learning-based recommendation engine. A collaborative-filtering or embedding-based approach could have looked more advanced on the surface, but it would also have made the system harder to explain, test, and defend in a short oral exam. The final recommendation approach is therefore heuristic and explainable. This was a conscious trade-off: lower algorithmic complexity, but higher interpretability, easier testing, and a clearer link between reader preference and recommendation outcome.

The second was a direct “AI-generated content detector”. That idea was rejected because the available public dataset does not provide ground-truth labels for AI-generated or AI-assisted books, and any strong claim of automatic detection would therefore have been difficult to justify. The implemented provenance model is more defensible: it records disclosure, moderation state, and risk signals rather than claiming perfect classification. This trade-off made the project more realistic and aligned better with the available evidence.

These choices reflect a broader engineering principle in the project: prefer systems that can be clearly justified, demonstrated, and maintained over features that appear sophisticated but cannot be defended rigorously.

## 11. Challenges, limitations, and future work
The main challenge was keeping the project coherent while extending it beyond a standard book API. The solution was to keep a modular structure, centralise configuration, grow the tests alongside the feature set, and introduce Alembic once schema evolution became substantial.

Another challenge was the mismatch between the public dataset and the provenance concept. `goodbooks-10k` does not contain AI-transparency or moderation labels, so the project had to represent those as additional curated metadata instead of forcing unsupported claims from the dataset.

Current limitations remain:

- provenance metadata is curated through the API rather than inferred automatically
- recommendation is heuristic rather than machine-learning based
- platform-of-origin defaults during import can still be improved
- SQLite is best for local development, while PostgreSQL would be better for full deployment

Future work would include richer tag-overlap similarity, user-saved discovery preferences, stronger import defaults for provenance, and deployment on PostgreSQL.

## 12. Conclusion
The final project is stronger than a basic CRUD coursework API because it combines public dataset integration, explainable recommendation, provenance-aware discovery, and production-minded engineering practices. The result is a coherent theme: helping readers discover books while also respecting trust, moderation, and content-origin preferences.

## Appendix A. GenAI declaration and analysis
Generative AI was used as a development support tool for ideation, debugging, implementation refinement, testing ideas, documentation drafting, and feature exploration. It was not used as a substitute for understanding the system. Final design choices, scope control, integration decisions, and validation remained the student's responsibility.

The most valuable uses of GenAI were:

- exploring alternative recommendation and discovery designs
- refining the provenance and AI-transparency concept into a defendable API feature
- identifying useful edge cases and test scenarios
- restructuring documentation into clearer submission-ready materials

This aligns with the brief's expectation that stronger projects use GenAI thoughtfully and creatively rather than only for low-level code generation.

## Appendix B. Example GenAI conversation excerpts

The brief describes conversation logs as an appendix, so the examples below show representative excerpts from the development dialogue rather than only a summary list.

### B.1 Dataset discovery and selection
**User:** "I want to introduce a real public book dataset; please help me find one on Kaggle."

**Assistant:** Recommended `goodbooks-10k` as the best fit because it matched the project structure, supported analytics and recommendation, and had a cleaner scope for coursework than larger book datasets.

**Outcome:** The project adopted `goodbooks-10k`, added importer support, and documented both the Kaggle page and upstream source.

### B.2 Provenance and AI-transparency design
**User:** Proposed a trust-oriented classification idea based on whether readers may want to distinguish fully human works from AI-assisted or AI-generated content, especially in web-novel ecosystems.

**Assistant:** Suggested avoiding a hard "AI detector" claim and instead implementing a provenance and disclosure model with moderation status, AI-risk signalling, reader filtering, and recommendation preferences.

**Outcome:** The final API added provenance fields, provenance analytics, `content_preference` recommendation modes, and provenance-aware similar-book discovery.

### B.3 Engineering hardening
**User:** Asked whether Alembic was worth introducing once the schema had evolved repeatedly.

**Assistant:** Explained that Alembic was no longer unnecessary overhead because the project had moved beyond a simple early-stage schema and would benefit from migration-driven evolution.

**Outcome:** Alembic configuration, an initial migration, and migration smoke tests were added to the repository.

### B.4 Submission preparation
**User:** Requested API documentation, technical report, and slides for final submission.

**Assistant:** Helped convert existing project knowledge into submission-ready documentation, while keeping the oral presentation focused on originality, engineering quality, and the strongest demo path.

**Outcome:** The repository now contains API documentation, this report, and presentation slides aligned with the final project version.
