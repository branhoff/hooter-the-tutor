1. Install Google Cloud CLI
https://cloud.google.com/sdk/docs/install#deb
2. Register your Docker container as an artifact in Google Cloud's "Artifact Registery"
https://cloud.google.com/artifact-registry
3. Deploy on Google Cloud Run
https://cloud.google.com/run?hl=en


Build the image from the project root
```shell
docker build . -t hooter-the-tutor-image
```

Tag the image with google cloud artifact registry url
```shell
docker tag hooter-the-tutor-image us-west1-docker.pkg.dev/light-sunlight-430106-u1/hooter-the-tutor/hooter-the-tutor:latest
```

Push the local image to the artifact registry
```shell
docker push us-west1-docker.pkg.dev/light-sunlight-430106-u1/hooter-the-tutor/hooter-the-tutor:latest
```

Run the container in Google Cloud Run
