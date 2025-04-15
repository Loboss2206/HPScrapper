# Bot Hyperplanning Scrapper
Le script discord_bot_scrapper permet de lancer un bot Discord qui enverra un message sur un salon Discord pour avertir à chaque nouvelle note ajoutée dans Hyperplanning.

## Prérequis
Créez un fichier credentials.txt contenant :

- Ligne 1 : votre login Hyperplanning

- Ligne 2 : votre mot de passe Hyperplanning

Créez un fichier tokens.txt contenant :

- Ligne 1 : le token privé de votre bot Discord

- Ligne 2 : l’ID du salon sur lequel envoyer les messages

### 🔧 Avec Docker
- Construire l’image :

```bash
docker build -t hp-scrapper .
```

- Lancer le conteneur :

```bash
docker run --rm -it \
  -v $(pwd)/credentials.txt:/app/credentials.txt:ro \
  -v $(pwd)/tokens.txt:/app/tokens.txt:ro \
  hp-scrapper
```

### 🐍 Sans Docker
- Installer les dépendances :

```bash
pip install -r requirements.txt
```

- Lancer le script :

```bash
python discord_bot_scrapper.py
```

## 🙏 Remerciements
Merci à [@FlorianLatapie](https://github.com/FlorianLatapie) pour son travail préliminaire qui m’a permis de gagner du temps.
