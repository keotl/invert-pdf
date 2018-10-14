## Heroku deploy
```bash
sudo heroku container:push web
```
```bash
heroku container:release web
```

## Running locally
```bash
sudo docker image build .
sudo docker run -p 8080:8080 --env PORT=8080 <the_built_image_hash>
```
