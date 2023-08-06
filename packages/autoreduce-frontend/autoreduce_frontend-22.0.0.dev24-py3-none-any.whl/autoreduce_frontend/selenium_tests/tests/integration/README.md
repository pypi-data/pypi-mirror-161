# Running the integration tests

Running the tests has some pre-requisite steps:

1. Start a MySQL server, with a database `test_autoreduce`. This can be done by calling `make mysql-test`
or running the `Run MySQL test db` VSCode task.
    - It takes a bit to initialise the DB so if the next step fails, try again in 10-15 seconds.
2. Run the `Run REST API integration` VSCode Run & Debug task
    - The task defines the `TESTING_MYSQL_DB` environment variable, which tells the REST API to
    use an extenal MySQL database [here](https://github.com/autoreduction/autoreduce-rest-api/blob/master/autoreduce_rest_api/autoreduce_django/settings.py#L43-L53).
    - The name of the database is important here too - `test_autoreduce` is the name that is used
    once `pytest` starts executing the frontend integration tests, so that must be the name defined in the `rest-api` settings.
3. Go to an integration test and run the `Pytest - frontend integration` VSCode Run & Debug task
    - This task too defines the `TESTING_MYSQL_DB` environment variable, which makes it use a MySQL DB
