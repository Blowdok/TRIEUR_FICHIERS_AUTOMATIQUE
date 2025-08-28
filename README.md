# Trieur de Fichiers Automatique - Version 1.2 🚀

![Capture d'écran de l'application](screenshots/screenshots_sombre_clair.png)

Une application Python avec interface graphique CustomTkinter permettant de trier automatiquement les fichiers d'un dossier spécifié selon plusieurs critères (type, date, taille). **Version 1.2** avec gestion d'erreurs avancée et robustesse améliorée.

## 🌟 Fonctionnalités

- **Interface graphique moderne** développée avec CustomTkinter

  - Thème sombre par défaut avec option de basculer en mode clair
  - Boutons de couleur mauve avec texte blanc
  - Barre de progression pour suivre l'avancement du tri

- **Options de tri flexibles**

  - Tri par type de fichier (images, vidéos, documents, etc.)
  - Tri par date de création/modification
  - Tri par taille de fichier (petits, moyens, grands)

- **Organisation hiérarchique**

  - Dossiers principaux par catégorie
  - Sous-dossiers par extension (optionnel)
  - Personnalisation des noms de dossiers

- **Sécurité et configuration renforcée** ✨

  - Sauvegarde des emplacements originaux pour restauration
  - Sauvegarde des préférences utilisateur
  - Journal détaillé des opérations et erreurs
  - **🛡️ Gestion d'erreurs avancée** avec rollback automatique
  - **🔐 Vérifications de permissions** et d'espace disque
  - **📊 Logging complet** dans fichier `trieur_fichiers.log`
  - **💬 Messages d'erreur informatifs** avec conseils de résolution

- **🆕 Dernières améliorations (v1.2)**
  - Types de fichiers : rajout de Polices et extensions
  - Rajout de l'exécutable "Trieur Fichiers Auto.exe"
  - **🛡️ Robustesse** : Gestion avancée des erreurs avec rollback
  - **🔧 Fiabilité** : Vérifications de permissions et d'espace disque
  - **📱 UX améliorée** : Messages d'erreur avec emojis et conseils

## 🛡️ Robustesse et Fiabilité (Nouveau !)

Cette version apporte des **améliorations majeures** en terme de robustesse et de gestion d'erreurs :

### ✨ **Gestion d'erreurs avancée**
- **Exceptions personnalisées** : `TrieurError`, `PermissionError_Custom`, `EspaceDisqueError`
- **Rollback automatique** : En cas d'erreur critique, toutes les opérations sont automatiquement annulées
- **Messages informatifs** : Chaque erreur est accompagnée de conseils précis pour la résoudre

### 🔐 **Vérifications de sécurité**
- **Contrôle des permissions** : Vérification avant chaque opération de fichier
- **Espace disque** : Contrôle automatique de l'espace disponible (avec marge de 10%)
- **Fichiers en lecture seule** : Gestion intelligente avec tentative de modification des permissions

### 📊 **Monitoring et logs**
- **Fichier de log** : `trieur_fichiers.log` avec historique complet des opérations
- **Niveaux de logging** : INFO, WARNING, ERROR, CRITICAL pour un debugging précis
- **Interface améliorée** : Messages avec emojis et conseils pratiques

## 📋 Prérequis

- Python 3.11 ou supérieur
- CustomTkinter
- Pillow
- Permissions d'écriture sur le dossier cible

## 🚀 Installation (mode codeur)

1. Cloner le repository

Ouvrir un terminal et copier la commande :

```bash
cd Desktop
git clone https://github.com/Blowdok/TRIEUR_FICHIERS_AUTOMATIQUE.git
cd TRIEUR_FICHIERS_AUTOMATIQUE
```

2. Installer les dépendances

   ```bash
   pip install -r requirements.txt
   ```

3. Lancer l'application
   ```bash
   python trieur_fichiers_auto.py
   ```

## 🚀 Installation (mode no-codeur)

1. Cloner le repository

Ouvrir un terminal et copier la commande :

```bash
cd Desktop
git clone https://github.com/Blowdok/TRIEUR_FICHIERS_AUTOMATIQUE.git
cd TRIEUR_FICHIERS_AUTOMATIQUE
```

2. Ouvrir le dossier exe

Double clic sur le fichier Trieur Fichiers Auto.exe

Profitez!

## 📖 Utilisation

1. **Sélection du dossier source**

   - Cliquez sur "Parcourir" pour sélectionner le dossier à trier

2. **Configuration du tri**

   - Choisissez le mode de tri (par type, date ou taille)
   - Activez les options avancées si nécessaire (sous-dossiers par extension, etc.)
   - Personnalisez les noms des catégories via le bouton "Personnaliser"

3. **Lancement du tri**

   - Cliquez sur "Trier les fichiers"
   - Suivez la progression dans la barre d'état et le journal

4. **Restauration (si nécessaire)**
   - Cliquez sur "Restaurer" pour annuler le tri et remettre les fichiers à leur emplacement initial

## 🚨 Gestion des erreurs

L'application gère maintenant de façon intelligente les situations d'erreur :

### Types d'erreurs gérées
- **❌ Permissions insuffisantes** → *Solution : Exécuter en tant qu'administrateur*
- **💾 Espace disque insuffisant** → *Solution : Libérer de l'espace ou changer de destination*
- **🔒 Fichiers en lecture seule** → *Solution : L'application tente de les rendre modifiables automatiquement*
- **📁 Fichiers/dossiers introuvables** → *Solution : Vérification automatique de l'existence*

### Fonctionnalités de récupération
- **🔄 Rollback automatique** : En cas d'erreur critique, toutes les opérations sont annulées
- **📋 Messages détaillés** : Chaque erreur affiche des conseils précis pour la résoudre
- **📊 Logging complet** : Historique des opérations dans `trieur_fichiers.log`

### Interface utilisateur améliorée
- **✅ Succès** : Messages avec emojis pour les opérations réussies
- **⚠️ Avertissements** : Erreurs mineures qui n'empêchent pas le tri
- **🚨 Erreurs critiques** : Situations graves avec conseils de résolution
- **💡 Conseils** : Recommandations pratiques pour éviter les problèmes

## 📁 Structure du projet

```
TRIEUR_FICHIERS_AUTOMATIQUE/
├── trieur_fichiers_auto.py            # Script principal (v1.2)
├── test_improvements.py               # Script de test des améliorations
├── requirements.txt                   # Dépendances du projet
├── README.md                          # Documentation
├── LICENSE                            # License MIT
├── trieur_fichiers.log                # Fichier de logs (généré automatiquement)
└── exe/                               # Dossier exécutable
    └── Trieur Fichiers Auto.exe       # L'exécutable
└── screenshots/                       # Dossier captures d'écran
    └── screenshots_sombre_clair.png   # Capture d'écran pour la documentation
```

## 📝 Structure du code

Le code est organisé en deux classes principales avec des **améliorations v1.2** :

- **TrieurFichiers** : Gère la logique de tri et de restauration des fichiers

  - Détermine les types de fichiers
  - Crée la structure de dossiers
  - Déplace les fichiers avec vérifications de sécurité
  - Gère la sauvegarde et la restauration
  - **🆕 Nouvelles fonctionnalités v1.2 :**
    - Vérification des permissions (`verifier_permissions_fichier`)
    - Contrôle de l'espace disque (`verifier_espace_disque`)
    - Déplacement sécurisé (`deplacer_fichier_securise`)
    - Rollback automatique (`effectuer_rollback`)
    - Logging complet de toutes les opérations

- **ApplicationTrieurFichiers** : Gère l'interface graphique
  - Affiche les options et contrôles
  - Gère les entrées utilisateur
  - Met à jour la barre de progression
  - Affiche le journal des opérations
  - **🆕 Améliorations v1.2 :**
    - Messages d'erreur avec emojis et conseils
    - Distinction entre erreurs critiques et avertissements
    - Recommandations d'actions automatiques

## 🛠️ Personnalisation

Vous pouvez facilement étendre les fonctionnalités en modifiant :

- Les types de fichiers reconnus (TYPES_FICHIERS dans le code)
- Les catégories de taille (TAILLES_FICHIERS dans le code)
- L'apparence de l'interface graphique (couleurs, dispositions, etc.)

## 📜 Licence

Ce projet est distribué sous la licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

## 🧪 Tests et Validation

La version 1.2 inclut un système de tests pour valider la robustesse :

```bash
# Exécuter les tests des améliorations
python test_improvements.py
```

Les tests vérifient :
- ✅ Syntaxe Python correcte
- ✅ Fonctionnalités de base
- ✅ Gestion des erreurs
- ✅ Vérifications de permissions
- ✅ Contrôle d'espace disque
- ✅ Mécanisme de rollback

## 📊 Changelog v1.2

### 🆕 Nouvelles fonctionnalités
- **Gestion d'erreurs robuste** avec rollback automatique
- **Vérifications de sécurité** (permissions, espace disque)
- **Logging complet** dans fichier `trieur_fichiers.log`
- **Messages UX améliorés** avec conseils pratiques

### 🐛 Corrections de bugs
- Gestion des fichiers en lecture seule
- Prévention des crashs sur permissions insuffisantes
- Récupération automatique en cas d'erreur critique
- Validation des chemins et fichiers inexistants

### ⚡ Améliorations de performance
- Vérifications préalables avant opérations lourdes
- Optimisation de la gestion des erreurs
- Meilleur suivi de la progression

## 👥 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

### 🔧 Issues ouvertes
- Issue #2 : Validations de sécurité pour les chemins de fichiers
- Issue #3 : Optimiser les performances pour les gros volumes
- Issue #4 : Mécanisme d'annulation et suivi de progression
- Issue #5 : Tests unitaires et d'intégration
