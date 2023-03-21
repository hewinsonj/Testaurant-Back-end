# Notes

[These were the steps](https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html) I followed to clear the migration issues, you hopefully won't have to do that in the future.

* I followed `Scenario 2`

# Steps to Run For First Time (use this to update README later)

* install docker-desktop
* then within this repo run the following:
```shell
docker-compose build testaurant_api
```

*_NOTE_* Here, `testaurant_api` refers to the name of the docker-compose service defined in our `docker-compose.yml` file.

* afterwards, run the following in your terminal to spin up your new containers:
```shell
docker-compose up
```

* create your django superuser by running the script:
```shell
./docker/create-superuser.sh
```

*_NOTE_:* If your migrations don't run on the very first time, just exit (`Control + C`) and re-run `docker-compose up`

## Common/Useful Docker Commands

* `docker-compose up` : Bring up the environment
* `docker-compose down` : Spin it back down
* `docker-compose up -d && docker-compose logs -f` : Run the env in the background, output logs in the foreground
* `docker exec -it testaurant_api /bin/bash` : Access the `testaurant_api` container
* `docker-compose restart testaurant-api` : Restart the `testaurant-api` container

## Installing Prettier

* follow official [prettier instructions](https://prettier.io/docs/en/install.html)
* inside the front end repo, run
  ```shell
  npm install --save-dev --save-exact prettier
  ```
* then create your config file for prettier (lookup recommended config/settings, tweak to however you like!)
  ```shell
  echo {}> .prettierrc.json
  ```

  *_NOTE:_* (might have to rename to `.prettierrc` instead of the json file dpeending on your editor config)
* finally make a `.prettierignore` file and put in the recommended ignored files