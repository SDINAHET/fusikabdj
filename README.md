# Refonte du site web de l'entreprise FUSIKAB DJ

## Objectif du projet

Ce projet consiste à refondre entièrement le site web de l'entreprise **FUSIKAB DJ** afin de moderniser son apparence, améliorer l'expérience utilisateur, et intégrer de nouvelles fonctionnalités.

## Structure du projet

### Répertoires principaux

- **static/** : Contient les ressources statiques comme les fichiers CSS, JavaScript, et les images.
  - **css/** : Feuilles de style pour les différentes pages et sections.
  - **js/** : Scripts JavaScript pour les fonctionnalités dynamiques.
  - **images/** : Images utilisées sur le site.
  - **gallery/** : Images spécifiques pour les galeries.

- **templates/** : Contient les fichiers HTML pour les différentes pages du site.
  - **partenaire/** : Pages dédiées aux partenaires.

### Fichiers principaux

- **app.py** : Point d'entrée principal de l'application.
- **run.py** : Script pour exécuter le projet.
- **README.md** : Documentation du projet.

## Fonctionnalités prévues

1. **Page d'accueil** :
   - Présentation de l'entreprise.
   - Accès rapide aux services et galeries.

2. **Galerie d'images** :
   - Affichage interactif des photos.
   - Fonctionnalité de zoom et de navigation.

3. **Section partenaires** :
   - Présentation des partenaires de l'entreprise.
   - Informations détaillées et galeries associées.

4. **Services** :
   - Description des prestations proposées par FUSIKAB DJ.
   - Formulaire de contact pour les demandes.

5. **Mentions légales et politiques** :
   - Pages dédiées aux mentions légales, politique de confidentialité, et cookies.

## Instructions pour le développement

1. **Installation** :
   - Assurez-vous d'avoir Python installé.
   - Créez un environnement virtuel avec `python3 -m venv venv`.
   - Activez l'environnement virtuel avec :
     - **Linux / macOS** : `source venv/bin/activate`
     - **Windows (PowerShell)** : `venv\Scripts\Activate.ps1`
   - Installez les dépendances nécessaires avec `pip3 install -r requirements.txt`.

2. **Exécution** :
   - Lancez le projet avec `python3 run.py`.

3. **Personnalisation** :
   - Modifiez les fichiers dans `templates/` pour changer le contenu des pages.
   - Ajoutez ou modifiez les styles dans `static/css/`.

4. **Ajout de contenu** :
   - Ajoutez des images dans les répertoires appropriés sous `static/images/` ou `static/gallery/`.
   - Ajoutez de nouvelles pages HTML dans `templates/`.

## Contribution

Si vous souhaitez contribuer à ce projet :
1. Forkez le dépôt.
2. Créez une branche pour vos modifications.
3. Soumettez une pull request.
