## Automatic cloud run deployment

The action example in this folder automatically deploys the KrakenD gateway to Google Cloud Run. This is done with
secrets of the action's repository.

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
        uses: f1betting/OpenAPItoKrakenD@v1
        with:
          input-folder: specs
          name: "krakend_test_gateway"
          stackdriver-project-id: ${{secrets.GOOGLE_PROJECT_ID}}

  build:
    needs: [ convert ]
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - uses: 'actions/checkout@v3'
      - name: Download KrakenD configuration
        uses: actions/download-artifact@v2
        with:
          name: krakend-config

      - uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: ${{secrets.GOOGLE_ACCOUNT_CREDENTIALS}}

      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v1'

      - name: 'Use gcloud CLI'
        run: 'gcloud builds submit --tag gcr.io/${{secrets.GOOGLE_PROJECT_ID}}/${{secrets.GOOGLE_SERVICE_NAME}} . --timeout 3600'

      - uses: 'google-github-actions/deploy-cloudrun@v1'
        with:
          image: gcr.io/${{secrets.GOOGLE_PROJECT_ID}}/${{secrets.GOOGLE_SERVICE_NAME}}
          service: ${{secrets.GOOGLE_SERVICE_NAME}}
          region: europe-west1
````