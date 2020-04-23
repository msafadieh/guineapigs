# guineapigs

A web app to log the food I give to my guineapigs.

## Setup

```
git clone https://git.mha.md/mhmd/guineapigs.git
python -m venv .env
source .env/bin/activate
pip install -r requirements
```

## Deploy

Run using guincorn

```
gunicorn latenight:app
```

I recommend serving through nginx.

## License

AGPL
