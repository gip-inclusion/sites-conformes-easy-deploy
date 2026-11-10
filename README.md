# Déploiement facile de Sites Conformes 

Ce repo permet de facilement déployer et maintenir à jour des instances de 
https://github.com/numerique-gouv/sites-conformes.

Il contient 2 branches:
- La branche `production` qui est synchronisée sur des releases de
  `sites-conformes` et qui nous sert à déployer nos instances.
- La branche `main` contient une action github qui vérifie tous les jours si un
  nouveau tag existe sur `sites-conforme`, et le cas échéant ouvre une PR pour
  mettre à jour la branche `production`.

## Projet Django

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
