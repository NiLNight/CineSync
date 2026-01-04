from pydantic import BaseModel, Field

class MovieShort(BaseModel):
    """
    Краткое представление информации о фильме.

    Attributes:
        id (int): Уникальный идентификатор фильма в TMDB.
        title (str): Название фильма.
        release_date (str | None): Дата выхода фильма. Может быть None.
        overview (str): Краткое описание сюжета. По умолчанию пустая строка.
        vote_average (float): Средняя оценка фильма.
    """
    id: int
    title: str
    release_date: str | None = None
    overview: str = Field(default="")
    vote_average: float

class MovieSearchResponse(BaseModel):
    """
    Ответ на запрос поиска фильмов.

    Attributes:
        results (list[MovieShort]): Список найденных фильмов.
    """
    results: list[MovieShort]