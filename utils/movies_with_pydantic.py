from pydantic import BaseModel, Field, field_validator
from typing import List
from enum import Enum

class Location(Enum):
    SPB = 'SPB'
    MSK = 'MSK'

class Genre(BaseModel):
    name: str

class TestMovies(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    imageUrl: str
    price: int
    description: str = Field(..., min_length=5, max_length=100)
    location: Location
    published: bool
    genreId: int


    @field_validator('imageUrl')
    def check_url_valid(cls, value):
        """
            Проверяем, есть ли https:// в поле imageUrl
        """
        if not (value.startswith('https://') or value.startswith('http://')):
            raise ValueError("Поле imageUrl должно начинаться с 'http://' или 'https://'")
        return value


class MoviesResponse(BaseModel):
    id: int
    name: str
    price: int
    description: str
    imageUrl: str = Field(..., min_length=10, max_length=100)
    location: Location
    published: bool
    genreId: int
    genre: Genre
    createdAt: str
    rating: int

class MovieListResponse(BaseModel):
    movies: List[MoviesResponse]
