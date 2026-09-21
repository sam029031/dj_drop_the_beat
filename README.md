# DJ Drop the Beat
**DJ 器材預購與入門學習平台**

A full-stack web platform where DJ-gear enthusiasts can pre-order equipment and learn the basics — built with **FastAPI** and **MySQL**. A server-rendered storefront with cart & checkout, user accounts, an admin back office, and course & contest sign-ups.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

DJ Drop the Beat is an e-commerce + learning site for DJ equipment. Visitors browse and search gear (controllers, audio interfaces, cables, music), add items to a cart and check out, sign up for beginner courses and contests, and track their orders; an admin back office manages the catalog and registrations. Built as the final project for the Internet Systems Design course.

## Features

- **Storefront** — category browsing, search, and product detail pages across DDJ controllers, audio interfaces, wires, and music.
- **Cart & checkout** — add to cart, place orders, and view order history.
- **Accounts** — registration and login with Argon2 password hashing and JWT-based sessions.
- **Courses & contests** — sign-up flows with registration management.
- **Admin back office** — manage the catalog, courses, contests, and registrations.
- **Server-rendered** with Jinja2 templates and static assets; MySQL persistence through SQLAlchemy.

## Tech stack

FastAPI · SQLAlchemy 2.0 · PyMySQL · Pydantic v2 · Argon2 (argon2-cffi / passlib) · PyJWT · Jinja2 · Uvicorn. Deployable to Railway.

## Project structure

```
app/
├── core/        # config, database, middleware
├── models/      # SQLAlchemy models: ddj, audio, music, wire, cart, order, course, contest, user, ...
├── routers/     # home, auth, category, search, detail, cart, checkout, course, contest, contact, admin, orders
├── schemas/     # Pydantic schemas
└── services/    # business logic (auth, ...)
templates/       # Jinja2 templates
static/          # CSS / JS / images
sql/             # schema & seed SQL
main.py          # FastAPI entry point
```

## Getting started

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

# configure environment
cp .env.example .env        # then edit the DB credentials
```

Then start the dev server:

```bash
uvicorn main:app --reload
```

and open <http://127.0.0.1:8000>. With no environment configured, local development falls back to a XAMPP MySQL `dj_platform` database on `127.0.0.1:3306`.

## Deployment

Configured for **Railway** (`runtime.txt`). `app/core/config.py` reads the standard `MYSQL*` / `DATABASE_URL` environment variables Railway provides, so set those on the service and deploy.

## Author

**Wei-Pei Chen (陳暐培)** — Dept. of Management Information Systems, National Chung Hsing University. Internet Systems Design course project.

## License

Released under the [MIT License](LICENSE).
