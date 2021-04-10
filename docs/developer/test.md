# Test

Awsume uses `pytest` as its test runner. It makes use of the `pytest.ini` configuration file, and contains all unit tests under the `test/unit` directory. The file structure of the `tests/unit` directory tries to closely match that of the project root directory itself, prepending `test_` to the file names.

For mocking, the built in `unittest.mock` is used extensively.

A pipenv script has been defined to run the tests and collect code coverage.
