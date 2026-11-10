# Déploiement facile de Sites Conformes 

Ce repo permet de facilement déployer et maintenir à jour des instances de 
https://github.com/numerique-gouv/sites-conformes.

Un projet Django minimal (`config/`) installe le paquet
[`sites-conformes`](https://pypi.org/project/sites-conformes/) via
[uv](https://docs.astral.sh/uv/).

```sh
cp .env.example .env
createdb sites_conformes
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver  # http://localhost:8000, admin sur /cms-admin/
```

## Tests et qualité

```sh
make venv     # uv sync, avec les outils de dev (ruff)
make lint     # ruff check + ruff format --check
make format   # corrige et formate le code
make test     # pytest (base PostgreSQL de DATABASE_URL, par exemple via .env)
              # la base de test est réutilisée : make test ARGS=--create-db pour la recréer
make check    # lint + tests
```

## Déploiement sur Scalingo

Le dépôt contient les fichiers attendus par Scalingo : `.buildpacks` (apt +
Python), `Aptfile` (ImageMagick pour les GIF animés), `Procfile`,
`gunicorn.conf.py` et `scalingo.json` (variables d’environnement et addon
PostgreSQL).

Le buildpack Python installe les dépendances avec uv à partir de `uv.lock`
(qui doit donc être versionné) et lance `collectstatic` pendant le build. Après
chaque déploiement, l’étape `postdeploy` applique les migrations et crée les
pages de démarrage.

Les fichiers envoyés par les utilisateurs ne survivent pas à un redéploiement :
configurer le stockage S3 (`S3_HOST`, `S3_BUCKET_NAME`, `S3_KEY_ID`,
`S3_KEY_SECRET`).
