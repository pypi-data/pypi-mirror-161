import io
import unittest
import os
import json
import mock
import tempfile
import pandas
import shutil

import dslibrary
from dslibrary.front import PARAMS_ALIAS, METRICS_ALIAS, THREAD_SPEC
from dslibrary.run_models import ModelRunner
from tests.t_utils import reset_env


class TestRunMethod(unittest.TestCase):
    """
    The ModelRunner.run_method() method lets you call your model's main method directly, for development, testing or
    hyper-parameter tuning.
    """

    def test_run_method__dsl_as_parameter(self):
        """
        A dslibrary instance is passed to the code you want to run.
        """
        def my_model(dsl):
            self.assertEqual(123, dsl.get_parameter("x"))
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.run_method(my_model)

    def test_run_method__thread_local(self):
        """
        Override spec for current thread.
        """
        def my_model(x=1):
            spec = THREAD_SPEC.value
            self.assertEqual(x, 123)
            self.assertEqual({"x": 123}, spec["parameters"])
            self.assertEqual(123, dslibrary.get_parameter("x"))
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        assert not hasattr(THREAD_SPEC, "value")
        runner.run_method(my_model)
        assert not hasattr(THREAD_SPEC, "value")

    def test_run_method__thread_local__mult(self):
        """
        Verify the point of thread-local configuration: thread safety on multiple concurrent calls.
        """
        import threading
        log = []
        def my_model(x=1):
            log.append(x)
        threads = []
        for x in range(100):
            def bg(x):
                runner = ModelRunner()
                runner.set_parameter("x", x)
                runner.run_method(my_model)
            t = threading.Thread(target=bg, args=(x,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(list(range(100)), list(sorted(log)))

    def test_run_method__alternate_approach(self):
        """
        The model can also call dslibrary.instance()
        """
        def my_model():
            dsl = dslibrary.instance()
            assert dsl.get_parameter("x") == 123
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.run_method(my_model)

    def test_run_method__params_to_method(self):
        """
        Or the parameters can just be sent to the method.
        """
        def my_model(dsl, x):
            assert x == 123
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.run_method(my_model)

    def test_params_to_method__coerce_type(self):
        """
        Type annotation is applied.
        """
        def my_model(dsl, x: int):
            assert x == 12
        runner = ModelRunner()
        runner.set_parameter("x", "12")
        runner.run_method(my_model)

    def test_kwargs_to_method(self):
        """
        Method can request that all unspecified parameters be sent in kwargs.
        """
        def my_model(dsl, x, **kwargs):
            assert x == 123
            assert kwargs["y"] == 222
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.set_parameter("y", 222)
        runner.run_method(my_model)

    def test_read_dataframe_from_specified_file_with_format(self):
        """
        The model only knows there is an input called 'input1'.  It requests that it be loaded into a dataframe.
        """
        runner = ModelRunner()
        runner.set_input("input1", os.path.dirname(__file__) + "/test_data/test1.csv", format_options={"delim_whitespace": True})
        def my_model(dsl):
            df = dsl.load_dataframe("input1")
            assert list(df.columns) == ["a", "b"], list(df.columns)
            assert list(df.a) == [1, 2]
            assert list(df.b) == [2, 4]
        runner.run_method(my_model)

    def test_write_dataframe_to_specified_file_with_format(self):
        """
        The model has an output called 'output1', and doesn't want to care where that output data should go or what
        format to use.
        """
        with tempfile.NamedTemporaryFile(suffix=".csv") as f_tmp:
            runner = ModelRunner(uri="uri", entry_point="main")
            runner.set_output("output1", f_tmp.name, format_options={"sep": "\t"})
            def my_model(dsl):
                df = pandas.DataFrame({"x": [1, 2], "y": [3, 4]})
                dsl.write_resource("output1", df)
            runner.run_method(my_model)
            df = pandas.read_csv(f_tmp.name, sep='\t')
            assert list(df.columns) == ["x", "y"]
            assert list(df.x) == [1, 2]
            assert list(df.y) == [3, 4]

    def test_model_parameter_misc(self):
        """
        The model declares the type of its parameters, and such things as default values, validation and coercion
        are taken care of.
        """
        project = tempfile.mkdtemp()
        with open(os.path.join(project, "MLProject"), 'w') as f:
            f.write("entry_points:\n  one:\n    parameters:\n      x: {type: float, default: 2}")
        # pass a parameter
        runner = ModelRunner()
        def my_model_1(dsl):
            assert dsl.get_parameter("x") == 1
        runner.set_parameter("x", 1)
        runner.run_method(my_model_1, path=project)
        # use default parameter
        runner = ModelRunner(entry_point="one")
        def my_model_2(dsl):
            assert dsl.get_parameter("x") == 2
        runner.run_method(my_model_2, path=project)
        # coercion of parameter to type declared in metadata
        runner = ModelRunner(entry_point="one")
        def my_model_3(dsl):
            assert dsl.get_parameter("x") == 1.5
        runner.set_parameter("x", "1.5")
        runner.run_method(my_model_3, path=project)
        # validation of parameter
        runner = ModelRunner(entry_point="one")
        def my_model_4(dsl):
            self.assertRaises(ValueError, lambda: dsl.get_parameter("x"))
        runner.set_parameter("x", "not numeric")
        runner.run_method(my_model_4, path=project)
        # clean up
        shutil.rmtree(project)

    def test_model_parameter_mapping(self):
        """
        Parameters are injected if they match the method's signature.  They are also coerced to the proper types.
        """
        runner = ModelRunner()
        def my_model(dsl, x: int, y: str):
            assert x == 1
            assert y == "2"
            assert dsl.get_parameter("z") == 3
        runner.set_parameter("x", 1).set_parameter("y", "2").set_parameter("z", 3)
        runner.run_method(my_model)
        runner.set_parameter("x", "1").set_parameter("y", 2).set_parameter("z", 3)
        runner.run_method(my_model)

    def test_model_parameter_json_parse_and_schema_check(self):
        """
        In addition to the very limited set of checks the MLProject file specifies, a full JSON schema can be given
        to validate more advanced structures, passed as JSON.
        """
        project = tempfile.mkdtemp()
        with open(os.path.join(project, "MLProject"), 'w') as f:
            f.write("entry_points:\n  one:\n    parameters:\n      x: {type: string, default: 2, schema: {type: object, properties: {a: {type: integer}}}}")
        runner = ModelRunner(entry_point="one")
        def my_model(dsl):
            assert dsl.get_parameter("x") == {"a": 4}
        runner.set_parameter("x", '{"a": 4}')
        runner.run_method(my_model, path=project)
        # clean up
        shutil.rmtree(project)

    def test_load_input_from_sql(self):
        """
        The caller can request that data be loaded from an SQL data source, instead of the usual CSV file.
        """
        runner = ModelRunner()
        log = []
        class Cursor(object):
            def __init__(self):
                self.description = ("a", None), ("b", None)
            def execute(self, sql, parameters=None):
                log.append(sql)
            def __iter__(self):
                return iter([(1, 2), (3, 4)])
        class Conn(object):
            def __init__(self, resource_name, username=None):
                assert username == "xyz"
                log.append(resource_name)
            def cursor(self):
                return Cursor()
            def close(self):
                log.append("close")
        def my_model_1(dsl):
            with mock.patch("dslibrary.transport.to_local.DSLibraryLocal.get_sql_connection", Conn):
                df = dsl.load_dataframe("x")
            assert list(df.columns) == ["a", "b"]
            assert list(df.a) == [1, 3]
            assert list(df.b) == [2, 4]
        runner.set_input("x", "sql:etc", sql_table="tbl1", username="xyz")
        runner.run_method(my_model_1)

    def test_log_metrics_to_csv(self):
        """
        Simple case of redirecting metrics to a CSV file.
        """
        project = tempfile.mkdtemp()
        runner = ModelRunner(uri="my_uri", run_id="run001", user="user3")
        runner.send_metrics_to("metrics.csv", format="csv")
        T = [1000]
        with mock.patch("time.time", lambda: T[0]):
            def my_model(dsl):
                dsl.log_metric("x", 123)
                T[0] += 1
                dsl.log_metric("y", 456)
            runner.run_method(my_model, path=project)
        metrics_fn = os.path.join(project, "metrics.csv")
        with open(metrics_fn, 'r') as f:
            data = f.read()
        assert data == 'uri,run_id,user,time,name,value,step\nmy_uri,run001,user3,1000,x,123,0\nmy_uri,run001,user3,1001,y,456,0\n'
        shutil.rmtree(project)

    def test_log_params_with_default_format(self):
        project = tempfile.mkdtemp()
        runner = ModelRunner(uri="my_uri", run_id="run001", user="user3")
        T = [1000]
        with mock.patch("time.time", lambda: T[0]):
            def my_model(dsl):
                dsl.log_param("a", 'one')
                T[0] += 1
                dsl.log_param("b", 222)
            runner.run_method(my_model, path=project)
        params_fn = os.path.join(project, PARAMS_ALIAS)
        with open(params_fn, 'r') as f:
            lines = f.read().strip().split("\n")
        assert json.loads(lines[0]) == {"uri": "my_uri", "run_id": "run001", "user": "user3", "time": 1000, "name": "a", "value": "one"}
        assert json.loads(lines[1]) == {"uri": "my_uri", "run_id": "run001", "user": "user3", "time": 1001, "name": "b", "value": 222}
        shutil.rmtree(project)

    def test_supply_and_capture_data(self):
        """
        You can pass in a dataframe!
        """
        def my_model(dsl):
            df = dsl.load_dataframe("input")
            dsl.log_metric("tot_before", df.x.sum())
            df.x += 1
            dsl.log_metric("tot_after", df.x.sum())
            dsl.write_resource("output", df)
        runner = ModelRunner()
        runner.set_input("input", data=pandas.DataFrame({"x": [1, 2, 3]}))
        # TODO we should probably have a global flag that captures everything, otherwise files will be created while debugging
        runner.set_output("output", capture=True)
        runner.send_metrics_to(capture=True)
        outputs = runner.run_method(my_model)
        self.assertEqual(list(outputs["output"].x), [2, 3, 4])
        metrics = outputs[METRICS_ALIAS]
        assert metrics == {'tot_before': 6, 'tot_after': 9}

    def test_named_sql_engine(self):
        """
        An SQL engine can be referenced as a named input.
        """
        def my_model(dsl):
            r = dsl.get_sql_connection("sql1")
            self.assertEqual("CONNECTION", r)
        runner = ModelRunner()
        runner.set_input("sql1", uri="postgres://host/database", username="u", password="p")
        def connect(uri, username, password, **k):
            self.assertEqual(uri, "postgres://host/database")
            self.assertEqual(username, "u")
            self.assertEqual(password, "p")
            return "CONNECTION"
        with mock.patch("dslibrary.front.connect_to_database", connect):
            runner.run_method(my_model)

    def test_named_folder_file_source(self):
        """
        A local folder that can be substituted for an s3 bucket.
        """
        def open(path, mode=None):
            self.assertEqual("/folder/file", str(path))
            return io.BytesIO(b"abc")
        with mock.patch("pathlib.Path.open", open):
            def my_model(dsl):
                r = dsl.read_resource("file", filesystem="the_files")
                self.assertEqual(b"abc", r)
            runner = ModelRunner()
            runner.set_input("the_files", uri="/folder")
            runner.run_method(my_model)

    def test_s3_folder_file_supplied(self):
        """
        An s3 bucket, filename comes from read_resource().
        """
        def open(inst, path, **kwargs):
            self.assertEqual("file", path)
            return io.BytesIO(b"abc")
        with mock.patch("dslibrary.engine_intf.S3Connection.open", open):
            def my_model(dsl):
                r = dsl.read_resource("file", filesystem="the_files")
                self.assertEqual(b"abc", r)
            runner = ModelRunner()
            runner.set_input("the_files", uri="s3://bucket", access_key="A", secret_key="S")
            runner.run_method(my_model)

    def test_s3_folder_file_part_of_spec(self):
        """
        The named source is a specific file in an s3 bucket.
        """
        def open(inst, path, mode, **kwargs):
            self.assertEqual("s3://bucket/file", path)
            return io.BytesIO(b"abc")
        with mock.patch("dslibrary.transport.to_local.DSLibraryLocal._opener", open):
            def my_model(dsl):
                r = dsl.read_resource("the_file")
                self.assertEqual(b"abc", r)
            runner = ModelRunner()
            runner.set_input("the_file", uri="s3://bucket/file", access_key="A", secret_key="S")
            runner.run_method(my_model)

    def test_sql_select__db_as_folder(self):
        """
        A local folder can substitute for a remote database.
        """
        def open(inst, path, mode, **kwargs):
            self.assertEqual("/folder/t1", path)
            return io.BytesIO(b"x\n1\n2\n30")
        with mock.patch("dslibrary.transport.to_local.DSLibraryLocal._opener", open):
            def my_model(dsl):
                df = dsl.sql_select("select x from t1", engine="the_files")
                self.assertEqual([1, 2, 30], list(df.x))
            runner = ModelRunner()
            runner.set_input("the_files", uri="/folder")
            runner.run_method(my_model)

    def tearDown(self) -> None:
        reset_env("test_run_method")
