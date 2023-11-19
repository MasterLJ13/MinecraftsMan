# MinecraftsMan
## What does our application do?
With our application you can query craftsmen in your area that get sorted by a ranking formula. 
With a Check24 like webpage you can see the result on your devices.

## How to deploy
Deploy the frontend and backend docker container by executing the following command:
```bash
docker-compose up --build
```
There will be two running docker containers. One for the frontend and one for the backend.

The benchmarking request: \
`GET /craftsmen?postalcode={postalcode}` and `PATCH /craftman/{craftman_id}` should be performed on 
`http://localhost:1234`. 

The frontend is reachable at `http://localhost:3000`.