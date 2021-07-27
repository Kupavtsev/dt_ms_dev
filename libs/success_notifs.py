import psycopg2.extras

from config import PG_LOGIN, PG_PASSWORD




try:
        conn = psycopg2.connect(
            user = PG_LOGIN,
            password = PG_PASSWORD,                           
            database = 'antipodpiska',
            host = 'localhost',                          # Development
            # host = 'db',                                # Production
            port = 5432,    
        )
except Exception as ex:
    print(' /// ----- I am unable to connect to the database ----- ///', ex)
    raise ex


cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)