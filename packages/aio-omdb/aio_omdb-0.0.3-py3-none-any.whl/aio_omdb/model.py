from typing import Optional

import attr


@attr.s(frozen=True, auto_attribs=True)
class Rating:
    source: str
    value: str


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class SearchResultItem:
    title: str
    imdb_id: str
    type: str
    year: Optional[str]
    poster: Optional[str]


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Movie:
    title: str
    imdb_id: str
    type: str
    year: Optional[str] = None
    rated: Optional[str] = None
    released: Optional[str] = None
    runtime: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    writer: Optional[str] = None
    actors: Optional[str] = None
    plot: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    awards: Optional[str] = None
    poster: Optional[str] = None
    ratings: list[Rating] = attr.ib(factory=list)
    metascore: Optional[str] = None
    imdb_rating: Optional[str] = None
    imdb_votes: Optional[str] = None
    dvd: Optional[str] = None
    box_office: Optional[str] = None
    production: Optional[str] = None
    website: Optional[str] = None

    def _as_list(self, value: Optional[str]) -> Optional[list[str]]:
        if value is None:
            return None
        return value.split(', ')

    @property
    def director_list(self) -> Optional[list[str]]:
        return self._as_list(self.director)

    @property
    def writer_list(self) -> Optional[list[str]]:
        return self._as_list(self.writer)

    @property
    def actors_list(self) -> Optional[list[str]]:
        return self._as_list(self.actors)

    @property
    def language_list(self) -> Optional[list[str]]:
        return self._as_list(self.language)

    @property
    def country_list(self) -> Optional[list[str]]:
        return self._as_list(self.country)
