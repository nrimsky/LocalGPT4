# LocalGPT4

Web app that uses your current location and various APIs to generate a short unique podcast about your local area!

## Deployment instructions

- `npm install`
- `npm run build`
- `gcloud app deploy`

## Running

- `python3 -m venv venv`
- `source venv/bin/activate`
- `gunicorn -b :8000 app:app --timeout 320 --log-level=debug`