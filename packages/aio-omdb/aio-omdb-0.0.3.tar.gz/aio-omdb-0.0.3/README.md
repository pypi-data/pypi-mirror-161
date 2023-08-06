# aio-omdb
Asyncronous and synchronous Python clients for OMDb ([the Open Movie Database](https://www.omdbapi.com)).

## Usage

```python
from aio_omdb.client import AsyncOMDBClient, SyncOMDBClient

OMDB_API_KEY = '...'  # Get your key from OMDB

a_client = AsyncOMDBClient(api_key=OMDB_API_KEY)
s_client = SyncOMDBClient(api_key=OMDB_API_KEY)

# Client provides the following methods:

# Get by IMDB ID
await a_client.get_by_id('tt1000252')
s_client.get_by_id('tt1000252')

# Get by exact title
await a_client.get_by_id('Rome, open city')
s_client.get_by_id('Rome, open city')

# Search title by a word or phrase
await a_client.search('Spock')
s_client.search('Spock')
```

The following exceptions may be raised:
- `aio_omdb.exc.InvalidAPIKey`: if an invalid API key is used;
- `aio_omdb.exc.MovieNotFound`: if no movie can be found in `get_by_id` or `get_by_title`.


## Testing

1. Install the `testing` extras

```bash
pip install -Ue .[testing]
```

2. Create file `.env` in the project root and put your OMDb API key there:

```
OMDB_API_KEY=<your API key>
```

3. Run tests

```bash
make test
```

Enjoy!
