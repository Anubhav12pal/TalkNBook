# Graph Report - .  (2026-05-29)

## Corpus Check
- Corpus is ~18,270 words - fits in a single context window. You may not need a graph.

## Summary
- 262 nodes · 464 edges · 21 communities detected
- Extraction: 61% EXTRACTED · 39% INFERRED · 0% AMBIGUOUS · INFERRED: 183 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `BookingCreate` - 40 edges
2. `BookingService` - 40 edges
3. `AuthService` - 22 edges
4. `UserCreate` - 19 edges
5. `UserLogin` - 19 edges
6. `UserResponse` - 19 edges
7. `BookingResponse` - 19 edges
8. `MovieService` - 11 edges
9. `Movie` - 10 edges
10. `Token` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Vite Logo SVG` --references--> `React + Vite Frontend`  [INFERRED]
  frontend/public/vite.svg → README.md
- `React Logo SVG` --references--> `React + Vite Frontend`  [INFERRED]
  frontend/src/assets/react.svg → README.md
- `Session Management` --semantically_similar_to--> `JWT Authentication`  [INFERRED] [semantically similar]
  backend/notes.md → README.md
- `Phone Authentication System` --semantically_similar_to--> `JWT Authentication`  [INFERRED] [semantically similar]
  VOICE_SETUP.md → README.md
- `uvicorn dependency` --implements--> `FastAPI Backend`  [INFERRED]
  backend/requirements.txt → README.md

## Hyperedges (group relationships)
- **Multi-Agent Routing Flow** — notes_triage_agent, notes_auth_agent, notes_booking_agent, notes_handoff_mechanism [EXTRACTED 0.90]
- **Voice Booking Pipeline** — voice_setup_retell_ai, voice_setup_websocket_endpoint, voice_setup_movie_booking_agent, readme_booking_service [EXTRACTED 0.85]
- **Backend Route-Service-Storage Flow** — readme_bookings_route, readme_booking_service, readme_bookings_json [INFERRED 0.80]

## Communities

### Community 0 - "Booking Models & Routes"
Cohesion: 0.1
Nodes (33): BookedSeatsRequest, BookedSeatsResponse, BookingCreate, BookingResponse, CancelSeatsRequest, Model for booking response., Model for getting booked seats request., Model for booked seats response. (+25 more)

### Community 1 - "Auth Endpoints"
Cohesion: 0.11
Nodes (32): get_current_user(), get_current_user_info(), login(), login_json(), Get current user information., Get the current authenticated user., Create a new user account., Login user and return access token. (+24 more)

### Community 2 - "Frontend App & API Client"
Cohesion: 0.09
Nodes (8): apiRequest(), getAuthToken(), MovieResponse, Model for movie response., get_movie(), get_movies(), Get all movies with optional filtering., Get a specific movie by ID.

### Community 3 - "Agent Architecture Concepts"
Cohesion: 0.1
Nodes (25): Style & Conventions (PEP8, Google docstrings), Authentication Agent, Booking Agent, Function Tool Adapter Pattern, Agent Handoff Mechanism, Multi-Agent System, OpenAI Agents SDK, Rationale: Agent Specialization (+17 more)

### Community 4 - "Multi-Agent Orchestration"
Cohesion: 0.13
Nodes (18): authenticate_user(), book_movie_tickets_auth(), cancel_seats_auth(), extract_session_and_book(), extract_session_and_cancel_seats(), extract_session_and_view_bookings(), get_user_bookings_auth(), logout_user() (+10 more)

### Community 5 - "Movie Service"
Cohesion: 0.21
Nodes (9): Movie, Model for movie data., MovieService, Load movies from JSON file., Get all movies.                  Returns:             List of all movies, Get a movie by its ID.                  Args:             movie_id: ID of the mo, Search movies by title.                  Args:             query: Search query, Get movies by genre.                  Args:             genre: Genre to filter b (+1 more)

### Community 6 - "Auth Service & Storage"
Cohesion: 0.14
Nodes (15): Rationale: JSON DB Choice, auth.py route, auth_service.py, bcrypt Password Hashing, JSON File Storage, JWT Authentication, movie_service.py, movies.json (+7 more)

### Community 7 - "Frontend Tooling & Rules"
Cohesion: 0.14
Nodes (15): Code Structure & Modularity Rules, Project Awareness & Context, Testing & Reliability Rules, @vitejs/plugin-react (Babel), @vitejs/plugin-react-swc (SWC), React + Vite Template, React Logo SVG, FastAPI Backend (+7 more)

### Community 8 - "Test Agent Tools"
Cohesion: 0.15
Nodes (12): book_movie_tickets(), cancel_entire_booking(), cancel_specific_seats_by_booking_id(), cancel_specific_seats_by_seat(), check_seat_availability(), get_user_bookings(), Cancel specific seats from user's bookings. Automatically finds which booking co, Cancel specific seats from a specific booking ID. Use this when user provides th (+4 more)

### Community 9 - "Working Auth Demo"
Cohesion: 0.25
Nodes (6): authenticate_user(), View bookings for authenticated user., Authenticate user with username and password., Smart booking that extracts session, movie, time, and seats from user input., smart_book_tickets(), smart_view_bookings()

### Community 10 - "Debug Test Script"
Cohesion: 0.33
Nodes (4): authenticate_user(), book_tickets_simple(), Authenticate user with username and password., Book movie tickets with explicit parameters.

### Community 11 - "Venv Activation Script"
Cohesion: 0.4
Nodes (0): 

### Community 12 - "Simple Test Script"
Cohesion: 0.5
Nodes (2): Test booking function that extracts session and books tickets., test_booking()

### Community 13 - "FastAPI Entrypoint"
Cohesion: 0.67
Nodes (0): 

### Community 14 - "Integration Notes"
Cohesion: 1.0
Nodes (1): How does intehration work with the agent and problems faced and resolved:  how t

### Community 15 - "Tailwind Config"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Vite Config"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "ESLint Config"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "PostCSS Config"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Backend Package Init"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Multipart Dependency"
Cohesion: 1.0
Nodes (1): python-multipart

## Knowledge Gaps
- **39 isolated node(s):** `How does intehration work with the agent and problems faced and resolved:  how t`, `Test booking function that extracts session and books tickets.`, `Model for user creation request.`, `Model for user login request.`, `Model for user response (without password).` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Integration Notes`** (2 nodes): `Notes.py`, `How does intehration work with the agent and problems faced and resolved:  how t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tailwind Config`** (1 nodes): `tailwind.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite Config`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ESLint Config`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PostCSS Config`** (1 nodes): `postcss.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Package Init`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Multipart Dependency`** (1 nodes): `python-multipart`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BookingCreate` connect `Booking Models & Routes` to `Auth Endpoints`, `Multi-Agent Orchestration`, `Test Agent Tools`, `Working Auth Demo`, `Debug Test Script`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Why does `BookingService` connect `Booking Models & Routes` to `Test Agent Tools`, `Working Auth Demo`, `Debug Test Script`, `Multi-Agent Orchestration`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Movie` connect `Movie Service` to `Auth Endpoints`, `Frontend App & API Client`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `BookingCreate` (e.g. with `Book movie tickets for specified seats and showtime. Seats should be comma-separ` and `Check which seats are available for a movie and showtime.`) actually correct?**
  _`BookingCreate` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `BookingService` (e.g. with `Book movie tickets for specified seats and showtime. Seats should be comma-separ` and `Check which seats are available for a movie and showtime.`) actually correct?**
  _`BookingService` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `AuthService` (e.g. with `Get the current authenticated user.` and `Create a new user account.`) actually correct?**
  _`AuthService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `UserCreate` (e.g. with `Get the current authenticated user.` and `Create a new user account.`) actually correct?**
  _`UserCreate` has 16 INFERRED edges - model-reasoned connections that need verification._