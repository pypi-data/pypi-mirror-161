# Development notes

## Developing locally

Developing operators locally (e.g. without publishing) is a bit clunky, but hopefully this guide will be a good v0 starting point:
1. Clone [aws-mwaa-local-runner](https://github.com/aws/aws-mwaa-local-runner) and follow the installation directions. 
2. Make any necessary changes to the `airflow_mcd`.
3. Copy the package into the `dags` directory from step 1. For instance, `cp -r ~/Dev/airflow-mcd/airflow_mcd/ dags/airflow_mcd/`.
4. Replace (or append) requirements in the `dags` directory in step 1.

   At a minimum this should include the dependencies from `airflow-mcd/requirements.txt`.
5. Run Airflow. For instance, `./mwaa-local-env start`. Repeat steps 2-4 as needed.
6. Update README :)

Pro Tip - To point the `SessionHook` to our DEV endpoint you can add https://api.dev.getmontecarlo.com/graphql 
as the `Host` in your connection.

See the README.md for details on existing operator and hook usage.