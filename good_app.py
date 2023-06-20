from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi import Query
from faker import Faker
import uuid

app = FastAPI()

class Movie(BaseModel):
    id: str
    title: str
    year: int
    genre: str
    director: Optional[str] = None


class MovieIn(BaseModel):
    title: str
    year: int
    genre: str
    director: Optional[str] = None

class MovieUpdate(BaseModel):
    title: Optional[str]
    year: Optional[int]
    genre: Optional[str]
    director: Optional[str] = None

fake = Faker()

movies_db = []

# Генерация моковых данных фильмов
for i in range(1, 101):
    movie = Movie(
        id=str(i),
        title=fake.catch_phrase(),
        year=fake.random_int(min=1900, max=2023),
        genre=fake.random_element(elements=("Action", "Drama", "Comedy", "Sci-Fi", "Thriller")),
        director=fake.name()
    )
    movies_db.append(movie)

@app.get("/movies", response_model=List[Movie])
async def get_all_movies():
    return movies_db

@app.get("/movies/search")
async def search_movies(keyword: str = Query(...)):
    result = [movie for movie in movies_db if keyword.lower() in movie.title.lower() or keyword.lower() in movie.genre.lower() or keyword.lower() in movie.director.lower()]

    if not result:
        raise HTTPException(status_code=404, detail="No movies found")
    
    return result

@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    for movie in movies_db:
        if movie.id == str(movie_id):
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")


@app.post("/movies", response_model=Movie)
async def add_movie(movie: MovieIn):
    movie_out = Movie(id=str(len(movies_db) + 1), **movie.dict())
    movies_db.append(movie_out)
    return movie_out

@app.put("/movies/{movie_id}", response_model=Movie)
async def update_movie(movie_id: int, movie: MovieUpdate):
    for index, stored_movie in enumerate(movies_db):
        if stored_movie.id == str(movie_id):
            updated_movie = stored_movie.copy(update=movie.dict())
            movies_db[index] = updated_movie
            return updated_movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.delete("/movies/{movie_id}", response_model=Movie)
async def delete_movie(movie_id: str):
    for index, stored_movie in enumerate(movies_db):
        if stored_movie.id == str(movie_id):
            removed_movie = movies_db.pop(index)
            return removed_movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.get("/movies/query/")
async def query_movies(query: str):
    result = [movie for movie in movies_db if query in movie.title or query in movie.genre or query in movie.director]
    if not result:
        raise HTTPException(status_code=404, detail="No movies found")
    return result
