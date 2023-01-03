## KrakenD Cloud Run service account

The action example in this folder automatically deploys the KrakenD gateway to Google Cloud Run with
the [krakend-cloud-run-service-account](https://github.com/f1betting/krakend-cloud-run-service-account) plugin. This is
done with
secrets of the action's repository.

The input folder contains the custom configuration files and an example OpenAPI specification.

### The secrets

| Secret name                | Description                                                                                                                                            |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| GOOGLE_ACCOUNT_CREDENTIALS | Your service account credentials JSON <br/>([See explanation here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating)) |
| GOOGLE_PROJECT_ID          | Your Google Cloud Project ID                                                                                                                           |
| GOOGLE_SERVICE_NAME        | The name of the Cloud Run service you wish to deploy to                                                                                                |

### The action

````yaml
name: Convert Specs to KrakenD config

on: workflow_dispatch

jobs:
  convert:
    runs-on: ubuntu-latest

    steps:
      - name: Convert specs to KrakenD config
        uses: f1betting/OpenAPItoKrakenD@v2
        with:
          input-folder: input

  build:
    needs: [ convert ]
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - uses: 'actions/checkout@v3'

      - name: Download KrakenD configuration
        uses: actions/download-artifact@v3
        with:
          name: krakend-config

      - name: Download krakend-cloud-run-service-account plugin
        uses: robinraju/release-downloader@v1.7
        with:
          repository: "f1betting/krakend-cloud-run-service-account"
          latest: true
          fileName: "cloud-run-service-account.so"
          out-file-path: "./config/plugins"

      - name: Authenticate Google SDK
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: ${{secrets.GOOGLE_ACCOUNT_CREDENTIALS}}

      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v1'

      - name: 'Build docker-image and submit to GCR'
        run: 'gcloud builds submit --tag eu.gcr.io/${{secrets.GOOGLE_PROJECT_ID}}/${{secrets.GOOGLE_SERVICE_NAME}} . --timeout 3600'

  deploy:
    needs: [ convert, build ]
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - uses: 'actions/checkout@v3'

      - name: Authenticate Google SDK
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: ${{secrets.GOOGLE_ACCOUNT_CREDENTIALS}}

      - name: Deploy to Google Cloud Run
        uses: 'google-github-actions/deploy-cloudrun@v1'
        with:
          image: eu.gcr.io/${{secrets.GOOGLE_PROJECT_ID}}/${{secrets.GOOGLE_SERVICE_NAME}}
          service: ${{secrets.GOOGLE_SERVICE_NAME}}
          region: europe-west1
````