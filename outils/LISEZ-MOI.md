# Outils de construction du site VCA

Le site publié (dossier `docs/`) est fabriqué automatiquement à partir des données de l'ancien WordPress.

## Fichiers
- `contenu_wordpress.json` : articles, pages, services, formations et liste des images de l'ancien site (extraits de la base de données).
- `structure_pages.json` : structure des pages (données Elementor) de l'accueil, À propos, Contact, Agenda, etc.
- `extraire_base.py` : extrait `contenu_wordpress.json` depuis le fichier `.sql` (non publié ici : il contient des données privées).
- `construire_site.py` : génère tout le site statique (pages, articles, images, style).

## Pour régénérer le site
1. Placer les images reçues (zips `AAAA_MM.zip`) dans le dossier d'envoi, comme avant.
2. Lancer `python3 construire_site.py` : le site est créé dans `dist2/`.
3. Copier `dist2/` dans `docs/` (en gardant le fichier `CNAME`), puis publier.

Remarque : les chemins du script pointent vers l'environnement de travail d'origine. Il faut les adapter (variables `U08`, `REPO`, `U` en haut du script) pour l'utiliser ailleurs.

## À ne jamais publier ici
Les fichiers `.sql` (adresses e-mail et mots de passe chiffrés des utilisateurs de l'ancien site).
