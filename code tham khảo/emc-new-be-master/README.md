# How to run app (development)
`pipenv run uvicorn main:app --reload`
or `docker-compose up`
- For development:
  Create mongodb setup credentials in database/ (setup dev mongodb running in docker)
  - 4 files with content credentials you want to setup ( text content ), e.g:
    - database/.mongodb_password: password
    - database/.mongodb_root_password: rootPassword
    - database/.mongodb_root_username: infralytik_root
    - database/.mongodb_username: infralytik_u
  - give permission to database folder:
    ```
    chmod 777 -R ./database
    ```

# How to run Tests
`coverage run --source app/ -m pytest`

`coverage report -m`

`coverage html`

# Deployment:
- install docker if not available
- create .env file with variables similar to .env.example:
    - substitue these variables with mongodb username and password created above:
    ```
    MONGODB_USERNAME=infralytik_u
    MONGODB_PASSWORD=password
    ```
    - cognito credentials:
    ```
    USER_POOL_ID=us-east-1_WTXArK0yR
    VDA_ID_ATTRIBUTE=custom:vda_id
    SUPPORT_EMAIL=support@verifieddataanalytics.com
    TEMPORARY_PASWORD=123456@Emc
    ```
    - `REPORT_S3` point to main report s3
- run `docker-compose up --build -d` will start this service listening on PORT=8000 in env variable
or use script in script/deployement/production
- Commands:
  - Start deploy:
  ```
  scripts/deployment/production/start.sh
  ```
  - Stop running deployment:
  ```
  scripts/deployment/production/stop.sh
  ```
