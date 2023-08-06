import re
from typing import Any, ClassVar, Optional, Type, Union

import attr
from yarl import URL
from aiohttp.client import ClientSession
import requests

import aio_omdb.exc as exc
from aio_omdb.model import Movie, Rating, SearchResultItem


DEFAULT_OMDB_URL = 'http://www.omdbapi.com/'


@attr.s(kw_only=True)
class OMDBClientBase:
    base_url: str = attr.ib(default=DEFAULT_OMDB_URL)
    api_key: str = attr.ib()

    _exc_map: ClassVar[dict[re.Pattern, Type[exc.OMDBClientError]]] = {
        re.compile('Invalid API key'): exc.InvalidAPIKey,
        re.compile('Incorrect IMDb ID'): exc.MovieNotFound,
        re.compile('Movie not found'): exc.MovieNotFound,
        re.compile('The offset specified in'): exc.InvalidItemOffset,
    }

    def _make_url(self, **query: Any) -> URL:
        return URL(self.base_url) % dict(query, apikey=self.api_key, r='json')

    def _make_exception(self, error_text: str) -> exc.OMDBClientError:
        for expr, exc_cls in self._exc_map.items():
            if expr.match(error_text):
                return exc_cls(error_text)

        return exc.OMDBClientError(error_text)

    def _make_query_data(
            self,
            id: Optional[str] = None,
            title: Optional[str] = None,
            text: Optional[str] = None,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> dict:
        """
        Transform human-readable parameter names into short ones
        used by OMDB.
        """

        query: dict[str, str] = {}

        if id is not None:
            query['i'] = id
        if title is not None:
            query['t'] = title
        if text is not None:
            query['s'] = text
        if type is not None:
            query['type'] = type
        if year is not None:
            query['y'] = str(year)
        if plot is not None:
            query['plot'] = plot
        if page is not None:
            query['page'] = str(page)

        return query

    def _make_movie_obj(self, item_data: dict[str, Any]) -> Movie:
        item = Movie(
            title=item_data['Title'],
            imdb_id=item_data['imdbID'],
            year=item_data['Year'],
            type=item_data['Type'],
            rated=item_data['Rated'],
            released=item_data['Released'],
            runtime=item_data['Runtime'],
            genre=item_data['Genre'],
            director=item_data['Director'],
            writer=item_data['Writer'],
            actors=item_data['Actors'],
            plot=item_data['Plot'],
            language=item_data['Language'],
            country=item_data['Country'],
            awards=item_data['Awards'],
            poster=item_data['Poster'],
            metascore=item_data['Metascore'],
            imdb_rating=item_data['imdbRating'],
            imdb_votes=item_data['imdbVotes'],
            dvd=item_data.get('DVD'),
            box_office=item_data.get('BoxOffice'),
            production=item_data.get('Production'),
            website=item_data.get('Website'),
            ratings=[
                Rating(
                    source=rating_data['Source'],
                    value=rating_data['Value'],
                )
                for rating_data in item_data['Ratings']
            ],
        )
        return item

    def _make_search_result_item_obj(self, item_data: dict[str, Any]) -> SearchResultItem:
        item = SearchResultItem(
            title=item_data['Title'],
            imdb_id=item_data['imdbID'],
            year=item_data['Year'],
            type=item_data['Type'],
            poster=item_data['Poster'],
        )
        return item


class AsyncOMDBClient(OMDBClientBase):
    async def _make_request(self, **query: Any) -> dict[str, Any]:
        query = {key: value for key, value in query.items() if value is not None}
        url = self._make_url(**query)
        async with ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        if data['Response'] == 'False':
            error_text = data['Error']
            raise self._make_exception(error_text=error_text)

        return data

    async def get_by_id(
            self, id: str, *,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> Movie:
        query_data = self._make_query_data(id=id, type=type, year=year, plot=plot, page=page)
        data = await self._make_request(**query_data)
        return self._make_movie_obj(data)

    async def get_by_title(
            self, title: str, *,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> Movie:
        query_data = self._make_query_data(title=title, type=type, year=year, plot=plot, page=page)
        data = await self._make_request(**query_data)
        return self._make_movie_obj(data)

    async def search(
            self, text: str, *,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> list[SearchResultItem]:
        query_data = self._make_query_data(text=text, type=type, year=year, plot=plot, page=page)
        try:
            data = await self._make_request(**query_data)
        except exc.MovieNotFound:
            return []

        raw_items = data['Search']
        items = [self._make_search_result_item_obj(raw_item) for raw_item in raw_items]
        return items


class SyncOMDBClient(OMDBClientBase):
    def _make_request(self, **query: Any) -> dict[str, Any]:
        query = {key: value for key, value in query.items() if value is not None}
        url = str(self._make_url(**query))
        data = requests.get(url).json()

        if data['Response'] == 'False':
            error_text = data['Error']
            raise self._make_exception(error_text=error_text)

        return data

    def get_by_id(
            self, id: str, *,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> Movie:
        query_data = self._make_query_data(id=id, type=type, year=year, plot=plot, page=page)
        data = self._make_request(**query_data)
        return self._make_movie_obj(data)

    def get_by_title(
            self, title: str, *,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> Movie:
        query_data = self._make_query_data(title=title, type=type, year=year, plot=plot, page=page)
        data = self._make_request(**query_data)
        return self._make_movie_obj(data)

    def search(
            self, text: str, *,
            type: Optional[str] = None,
            year: Optional[Union[str, int]] = None,
            plot: Optional[str] = None,
            page: Optional[int] = None,
    ) -> list[SearchResultItem]:
        query_data = self._make_query_data(text=text, type=type, year=year, plot=plot, page=page)
        try:
            data = self._make_request(**query_data)
        except exc.MovieNotFound:
            return []

        raw_items = data['Search']
        items = [self._make_search_result_item_obj(raw_item) for raw_item in raw_items]
        return items
