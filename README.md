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

## Personnalisation

On peut renseigner la variable d’environnement `SERVICE_NAME`, qui vaut
`data-inclusion`, `mon-recap` ou `site-institutionnel` (liste définie
dans `config/settings.py`).

### Favicons

Si le dossier `statics/favicons/<SERVICE_NAME>/` existe, ses fichiers remplacent ceux du
DSFR ; sinon, ou sans `SERVICE_NAME`, c’est le favicon du DSFR. Les fichiers
statiques étant collectés au build, changer `SERVICE_NAME` nécessite un
redéploiement (un simple redémarrage ne suffit pas).

Chaque dossier contient tout ou partie de ces fichiers (les fichiers absents
restent ceux du DSFR). Pour ajouter un service, l’ajouter à
`SERVICE_NAME_CHOICES` et créer son dossier dans `favicons/`.

| Fichier                      | Format                     |
| ---------------------------- | -------------------------- |
| `favicon.svg`                | SVG                        |
| `favicon.ico`                | ICO 32×32                  |
| `apple-touch-icon.png`       | PNG 180×180                |
| `android-chrome-192x192.png` | PNG 192×192                |
| `android-chrome-512x512.png` | PNG 512×512                |
| `manifest.webmanifest`       | à fournir seulement pour changer la liste des icônes Android |

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
