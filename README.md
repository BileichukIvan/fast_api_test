# Posts and Comments Management API

A FastAPI project for managing posts, comments, and users.

## Features
- JWT authentication. 
- Perspective AI for checking comments. 
- Cohere AI for auto-replying to comments. 
- CRUD implementation for posts and comments.

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/BileichukIvan/fast_api_test.git

2. **Set up the ```.env``` file Create a ```.env``` file using ```.env.template``` as an example.**

3. **Install requirements**
   ```bash
   pip install -r requirements.txt
   
4. **Migrate the database**
   ```bash
   alembic upgrade head
   
5. **Run the server**
   ```bash
   python -m uvicorn main:app --reload
   
6. **Test it via documentation Visit: ```http://127.0.0.1:8000/docs```**