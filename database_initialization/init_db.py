"""
Setups, drops database (database, user, tables).

.. function:: setup_db(connection: aiomysql.Connection) -> None
    setup the full database with tables and user, database ready to work
.. function:: teardown_db(connection: aiomysql.Connection) -> None
    drop the full database with tables and user, database entirely deleted
.. function:: create_tables(connection: aiomysql.Connection) -> None
    create all tables for the database
.. function:: drop_tables(connection: aiomysql.Connection) -> None
    drop all tables from the database
.. function:: create_user(connection: aiomysql.Connection) -> None
    create the database user
.. function::f drop_user(connection: aiomysql.Connection) -> None
    drop the database user
.. function:: main() -> None
    use all the above functions
"""

import asyncio

import aiomysql
from loguru import logger

from core.database.models import Database, tables
from core.settings import BASE_DIR, get_config
from database_initialization import (
    generate_data,
    generate_test_data
)


USER_CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'
USER_CONFIG = get_config()
DATABASE_CONFIG = USER_CONFIG['mysql']

DB_NAME: str = DATABASE_CONFIG['database']
DB_HOST: str = DATABASE_CONFIG['host']
DB_PORT: int = int(DATABASE_CONFIG['port'])
DB_USER_NAME: str = DATABASE_CONFIG['user_name']
DB_USER_PASSWORD: str = DATABASE_CONFIG['user_password']

# data for first set up (used `root` user for creating database and user)
DB_ROOT_NAME: str = DATABASE_CONFIG['root_name']
DB_ROOT_PASSWORD: str = DATABASE_CONFIG['root_password']


async def setup_db(connection: aiomysql.Connection) -> None:
    """ Create database, tables and user """
    query_to_create_database = Database.create_database
    params = {
        'db_name': DB_NAME
    }

    query = query_to_create_database.format(**params)

    async with connection.cursor() as cursor:
        await cursor.execute(query)

    logger.success('Database is created.')

    await create_tables(connection)
    await create_user(connection)


async def teardown_db(connection: aiomysql.Connection) -> None:
    """ Drop the entire base """
    query_to_drop_database = Database.drop_database
    params = {
        'db_name': DB_NAME
    }

    query = query_to_drop_database.format(**params)

    async with connection.cursor() as cursor:
        await cursor.execute(query)

    logger.success('Database is dropped.')

    await drop_user(connection)


async def create_tables(connection: aiomysql.Connection) -> None:
    """ Create all tables in the database """
    query_to_use_database = Database.use_database
    params = {
        'db_name': DB_NAME
    }

    query_to_use_database = query_to_use_database.format(**params)

    async with connection.cursor() as cursor:
        await cursor.execute(query_to_use_database)

        for table in tables:
            query_to_create_table = table.create_table
            await cursor.execute(query_to_create_table)

    logger.success('Tables are created.')


async def drop_tables(connection: aiomysql.Connection) -> None:
    """ Drop all tables in the database """
    query_to_use_database = Database.use_database
    params = {
        'db_name': DB_NAME
    }

    query_to_use_database = query_to_use_database.format(**params)

    async with connection.cursor() as cursor:
        await cursor.execute(query_to_use_database)

        for table in tables:
            query_to_drop_table = table.drop_table
            await cursor.execute(query_to_drop_table)

    logger.success('Tables are dropped.')


async def create_user(connection: aiomysql.Connection) -> None:
    """ Create user that lead the app database """
    query_to_create_user = Database.create_user
    params = {
        'db_name': DB_NAME,
        'host': DB_HOST,
        'user_name': DB_USER_NAME,
        'user_password': DB_USER_PASSWORD
    }

    query = query_to_create_user.format(**params)

    async with connection.cursor() as cursor:
        await cursor.execute(query)

    logger.success('User is created.')


async def drop_user(connection: aiomysql.Connection) -> None:
    """ Drop user that lead the app database """
    query_to_drop_user = Database.drop_user
    params = {
        'user_name': DB_USER_NAME
    }

    query = query_to_drop_user.format(**params)

    async with connection.cursor() as cursor:
        await cursor.execute(query, params)

    logger.success('User is dropped.')


async def main() -> None:
    """ Invoke functions that operate with database """
    connection = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_ROOT_NAME,
        password=DB_ROOT_PASSWORD,
        autocommit=True
    )

    await teardown_db(connection)
    await setup_db(connection)

    # --------------------------------------------------
    # # await drop_tables(connection)
    # # await create_tables(connection)
    # # await drop_user(connection)
    # # await create_user(connection)
    # --------------------------------------------------

    # --------------------------------------------------
    # # data generating
    await generate_data.create_admin_account(connection)
    # # test data generating
    await generate_test_data.generate_test_data(connection)
    # --------------------------------------------------

    connection.close()


if __name__ == '__main__':
    asyncio.run(main())
