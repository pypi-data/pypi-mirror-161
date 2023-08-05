import unittest
import pandas
import mock

from dslibrary.utils.connect import _process_params, dataframe_to_sql, db_conn_flavor, connect_psycopg2, \
    connect_to_database, enquote_sql_identifier, connect_bigquery


class TestConnect(unittest.TestCase):
    def test__process_params(self):
        r = _process_params("mysql://u:p@host:1234/database", extra=1)
        assert r == {
            'host': 'host',
            'port': 1234,
            'database': 'database',
            'username': 'u',
            'password': 'p',
            'extra': 1
        }, r
        r = _process_params("xyz://u@host")
        assert r == {
            'host': 'host',
            'port': None,
            'database': '',
            'username': 'u',
            'password': ''
        }, r
        r = _process_params("sqlite:path/to/file")
        assert r == {
            'host': '',
            'port': None,
            'database': 'path/to/file',
            'username': '',
            'password': ''
        }, r
        r = _process_params("x://host/db", database="db2")
        assert r == {
            'host': 'host',
            'port': None,
            'database': 'db2',
            'username': '',
            'password': ''
        }, r

    def test_dataframe_to_sql(self):
        df = pandas.DataFrame({"x": [1, 2, 3], "y": [1.0, 2.0, 4.0], "z": ["one", "two", "three"]})
        sqls = list(dataframe_to_sql(df, "t1"))
        self.assertEqual(sqls, [
            ('DROP TABLE IF EXISTS t1', []),
            ('CREATE TABLE IF NOT EXISTS t1 (x INTEGER, y DOUBLE PRECISION, z VARCHAR(8))', []),
            ('INSERT INTO t1 (x, y, z) VALUES (%s, %s, %s), (%s, %s, %s), (%s, %s, %s)', [1, 1.0, 'one', 2, 2.0, 'two', 3, 4.0, 'three'])
        ])

    def test_dataframe_to_sql__bigquery(self):
        df = pandas.DataFrame({"x": [1, 2, 3], "y": [1.0, 2.0, 4.0], "z": ["one", "two", "three"]})
        sqls = list(dataframe_to_sql(df, "t1", flavor="bigquery"))
        self.assertEqual(sqls, [
            ('DROP TABLE IF EXISTS t1', []),
            ('CREATE TABLE IF NOT EXISTS t1 (x INT64, y NUMERIC, z STRING(8))', []),
            ('INSERT INTO t1 (x, y, z) VALUES (%s, %s, %s), (%s, %s, %s), (%s, %s, %s)', [1, 1.0, 'one', 2, 2.0, 'two', 3, 4.0, 'three'])
        ])

    def test_enquote_sql_identifier(self):
        # no flavor
        self.assertEqual('a', enquote_sql_identifier("a"))
        self.assertEqual('"a 1"', enquote_sql_identifier("a 1"))
        self.assertEqual('"a!"', enquote_sql_identifier("a!"))
        self.assertEqual('a.b', enquote_sql_identifier("a.b"))
        self.assertEqual('a."b!"', enquote_sql_identifier("a.b!"))
        # postgres
        self.assertEqual('a', enquote_sql_identifier("a", flavor="postgres"))
        self.assertEqual('"A"', enquote_sql_identifier("A", flavor="postgres"))
        # mysql
        self.assertEqual('a', enquote_sql_identifier("a", flavor="mysql"))
        self.assertEqual('A', enquote_sql_identifier("A", flavor="mysql"))
        self.assertEqual('`A!`', enquote_sql_identifier("A!", flavor="mysql"))

    def test_db_conn_flavor(self):
        # artificially set property
        class A(object):
            _flavor = "xyz"
        self.assertEqual(db_conn_flavor(A()), "xyz")
        # name of class
        class MyPostGresDriver(object):
            pass
        self.assertEqual(db_conn_flavor(MyPostGresDriver()), "postgres")

    def test_sniff__pg(self):
        strategy = connect_to_database("postgres://u:p@host:1234/database", sniff_only=True)
        self.assertEqual(strategy.open_args, {'dsn': 'dbname=database host=host password=p port=1234 user=u'})
        import psycopg2
        self.assertIs(strategy.opener, psycopg2.connect)

    def test_pg_2(self):
        import dslibrary
        class MyPg(object):
            def set_isolation_level(self, n):
                pass
        def conn(**kwargs):
            self.assertEqual(kwargs, {'dsn': 'dbname=postgres host=HOST password=xyz port=5432 user=postgres'})
            return MyPg()
        with mock.patch("psycopg2.connect", conn):
            c = dslibrary.get_sql_connection('postgres://HOST:5432/postgres', password="xyz", **{'username': 'postgres'})
            assert isinstance(c, MyPg)

    def test_connect_psycopg2_valid_dsn(self):
        class MyPg(object):
            def set_isolation_level(self, n):
                pass
        def conn(**kwargs):
            self.assertEqual(kwargs, {'dsn': 'dbname=db1 host=host password=p port=1234 user=u', 'service': 's1'})
            return MyPg()
        with mock.patch("psycopg2.connect", conn):
            connect_psycopg2(host="host", port=1234, username="u", password="p", database="db1", a=123, z="def",
                             service="s1")

    def test_connect_bigquery(self):
        class Col(object):
            name = "x"
        class Rows(object):
            schema = [Col()]
            pages = [[[1]]]
        class Results(object):
            def result(self, *a, **k):
                return Rows()
        class MyConn(object):
            def query(self, *a, **k):
                return Results()
        def conn(service_account: dict, **kwargs):
            self.assertEqual(service_account, {"etc": 123})
            return MyConn()
        with mock.patch("dslibrary.utils.bigq.bgq_connect", conn):
            cursor = connect_bigquery(host="", database={"etc": 123}).cursor()
            cursor.execute("SQL")
            row = cursor.fetchone()
            self.assertEqual([1], row)
