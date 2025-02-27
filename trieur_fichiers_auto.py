import os
import shutil
import json
import datetime
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from typing import Dict, List, Tuple
import threading

# Dictionnaire des types de fichiers par extension
TYPES_FICHIERS = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico"],
    "Vidéos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2"],
    "Programmes": [".exe", ".msi", ".app", ".apk", ".bat", ".sh", ".dmg", ".deb", ".rpm"],
    "Code": [".py", ".java", ".js", ".html", ".css", ".php", ".c", ".cpp", ".h", ".cs", ".json", ".xml"]
}

# Catégories de taille de fichiers (en octets)
TAILLES_FICHIERS = {
    "Petits": (0, 1024 * 1024),  # 0 - 1 Mo
    "Moyens": (1024 * 1024, 50 * 1024 * 1024),  # 1 Mo - 50 Mo
    "Grands": (50 * 1024 * 1024, float('inf'))  # Plus de 50 Mo
}

# Configuration par défaut
CONFIG_PAR_DEFAUT = {
    "theme": "dark",
    "dossier_source": "",
    "type_tri": "type",
    "noms_dossiers": {k: k for k in TYPES_FICHIERS.keys()},
    "tailles_fichiers": {k: k for k in TAILLES_FICHIERS.keys()},
    "sous_dossiers_par_extension": True
}


class TrieurFichiers:
    """Classe principale pour la gestion du tri des fichiers"""
    
    def __init__(self, config: Dict = None):
        """
        Initialise l'outil de tri des fichiers avec la configuration spécifiée
        :param config: Dictionnaire de configuration
        """
        self.config = config or CONFIG_PAR_DEFAUT.copy()
        self.dossier_source = self.config.get("dossier_source", "")
        self.sauvegarde = {}  # Pour stocker les emplacements originaux des fichiers

    def obtenir_type_fichier(self, fichier: str) -> str:
        """
        Détermine le type d'un fichier en fonction de son extension
        :param fichier: Chemin du fichier
        :return: Type du fichier ou "Autres" si inconnu
        """
        _, extension = os.path.splitext(fichier.lower())
        for type_fichier, extensions in TYPES_FICHIERS.items():
            if extension in extensions:
                return self.config["noms_dossiers"].get(type_fichier, type_fichier)
        return "Autres"

    def obtenir_categorie_taille(self, taille: int) -> str:
        """
        Détermine la catégorie de taille d'un fichier
        :param taille: Taille du fichier en octets
        :return: Catégorie de taille
        """
        for categorie, (min_taille, max_taille) in TAILLES_FICHIERS.items():
            if min_taille <= taille < max_taille:
                return self.config["tailles_fichiers"].get(categorie, categorie)
        return "Autres"

    def obtenir_categorie_date(self, date_timestamp: float) -> str:
        """
        Détermine la catégorie de date d'un fichier
        :param date_timestamp: Timestamp de la date de modification du fichier
        :return: Catégorie de date (ex: "2023-01")
        """
        date = datetime.datetime.fromtimestamp(date_timestamp)
        return f"{date.year}-{date.month:02d}"

    def creer_dossier_destination(self, fichier: str) -> str:
        """
        Détermine le dossier de destination pour un fichier selon le mode de tri
        :param fichier: Chemin du fichier
        :return: Chemin du dossier de destination
        """
        chemin_complet = os.path.join(self.dossier_source, fichier)
        
        if not os.path.isfile(chemin_complet):
            return None
            
        type_tri = self.config.get("type_tri", "type")
        
        if type_tri == "type":
            type_fichier = self.obtenir_type_fichier(fichier)
            dossier_destination = os.path.join(self.dossier_source, type_fichier)
            
            # Création de sous-dossiers par extension si activé
            if self.config.get("sous_dossiers_par_extension", True):
                _, extension = os.path.splitext(fichier.lower())
                extension = extension[1:]  # Supprimer le point
                if extension:
                    dossier_destination = os.path.join(dossier_destination, extension)
        
        elif type_tri == "date":
            date_modif = os.path.getmtime(chemin_complet)
            categorie_date = self.obtenir_categorie_date(date_modif)
            dossier_destination = os.path.join(self.dossier_source, "Par Date", categorie_date)
        
        elif type_tri == "taille":
            taille = os.path.getsize(chemin_complet)
            categorie_taille = self.obtenir_categorie_taille(taille)
            dossier_destination = os.path.join(self.dossier_source, "Par Taille", categorie_taille)
        
        else:
            return None
            
        return dossier_destination

    def sauvegarder_emplacement_original(self, fichier: str, chemin_destination: str):
        """
        Enregistre l'emplacement original d'un fichier pour permettre la restauration
        :param fichier: Nom du fichier
        :param chemin_destination: Chemin de destination du fichier
        """
        chemin_complet = os.path.join(self.dossier_source, fichier)
        chemin_destination_complet = os.path.join(chemin_destination, fichier)
        self.sauvegarde[chemin_destination_complet] = chemin_complet

    def trier_fichiers(self, callback=None) -> Tuple[int, List[str]]:
        """
        Trie les fichiers selon le mode spécifié
        :param callback: Fonction de rappel pour mettre à jour la progression
        :return: Tuple (nombre de fichiers traités, liste des erreurs)
        """
        if not self.dossier_source or not os.path.isdir(self.dossier_source):
            return 0, ["Dossier source invalide"]
            
        fichiers = [f for f in os.listdir(self.dossier_source) 
                   if os.path.isfile(os.path.join(self.dossier_source, f))]
        
        if not fichiers:
            return 0, ["Aucun fichier trouvé dans le dossier"]
            
        self.sauvegarde = {}  # Réinitialiser la sauvegarde
        erreurs = []
        fichiers_traites = 0
        
        # Créer un fichier de sauvegarde avant de commencer
        sauvegarde_path = os.path.join(self.dossier_source, ".trieur_sauvegarde.json")
        
        for i, fichier in enumerate(fichiers):
            try:
                # Ignorer les fichiers cachés et le fichier de sauvegarde
                if fichier.startswith('.') or fichier == ".trieur_sauvegarde.json":
                    continue
                    
                dossier_destination = self.creer_dossier_destination(fichier)
                
                if not dossier_destination:
                    continue
                    
                # Créer le dossier de destination s'il n'existe pas
                os.makedirs(dossier_destination, exist_ok=True)
                
                chemin_source = os.path.join(self.dossier_source, fichier)
                chemin_destination = os.path.join(dossier_destination, fichier)
                
                # Gérer les doublons
                if os.path.exists(chemin_destination):
                    base, extension = os.path.splitext(fichier)
                    nouveau_nom = f"{base}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
                    chemin_destination = os.path.join(dossier_destination, nouveau_nom)
                
                # Sauvegarder l'emplacement original
                self.sauvegarder_emplacement_original(fichier, dossier_destination)
                
                # Déplacer le fichier
                shutil.move(chemin_source, chemin_destination)
                fichiers_traites += 1
                
                # Mise à jour de la progression
                if callback:
                    callback(i + 1, len(fichiers))
                    
            except Exception as e:
                erreurs.append(f"Erreur avec {fichier}: {str(e)}")
        
        # Enregistrer la sauvegarde une fois le tri terminé
        with open(sauvegarde_path, 'w') as f:
            json.dump(self.sauvegarde, f)
            
        return fichiers_traites, erreurs

    def restaurer_fichiers(self, callback=None) -> Tuple[int, List[str]]:
        """
        Restaure les fichiers à leur emplacement d'origine et supprime les dossiers créés
        :param callback: Fonction de rappel pour mettre à jour la progression
        :return: Tuple (nombre de fichiers restaurés, liste des erreurs)
        """
        sauvegarde_path = os.path.join(self.dossier_source, ".trieur_sauvegarde.json")
        
        if not os.path.isfile(sauvegarde_path):
            return 0, ["Aucune sauvegarde trouvée"]
            
        with open(sauvegarde_path, 'r') as f:
            sauvegarde = json.load(f)
            
        if not sauvegarde:
            return 0, ["Sauvegarde vide"]
            
        erreurs = []
        fichiers_restaures = 0
        dossiers_crees = set()
        
        items = list(sauvegarde.items())
        
        # Première étape: restaurer les fichiers
        for i, (chemin_actuel, chemin_original) in enumerate(items):
            try:
                if os.path.isfile(chemin_actuel):
                    # Créer le dossier d'origine si nécessaire
                    os.makedirs(os.path.dirname(chemin_original), exist_ok=True)
                    
                    # Mémoriser le dossier parent pour suppression ultérieure
                    dossier_parent = os.path.dirname(chemin_actuel)
                    dossiers_crees.add(dossier_parent)
                    
                    # Déplacer le fichier à son emplacement d'origine
                    shutil.move(chemin_actuel, chemin_original)
                    fichiers_restaures += 1
                
                # Mise à jour de la progression
                if callback:
                    callback(i + 1, len(items))
                    
            except Exception as e:
                erreurs.append(f"Erreur lors de la restauration: {str(e)}")
        
        # Deuxième étape: supprimer les dossiers créés (du plus profond au moins profond)
        dossiers_a_supprimer = sorted(dossiers_crees, key=lambda x: x.count(os.sep), reverse=True)
        
        # Récupérer tous les dossiers de catégories possibles selon le type de tri
        dossiers_categories = []
        
        # Dossiers de type
        for categorie in self.config.get("noms_dossiers", {}).values():
            dossiers_categories.append(os.path.join(self.dossier_source, categorie))
        
        # Ajouter le dossier "Autres" qui est utilisé pour les fichiers sans type reconnu
        dossiers_categories.append(os.path.join(self.dossier_source, "Autres"))
        
        # Dossiers de date et taille
        dossiers_categories.append(os.path.join(self.dossier_source, "Par Date"))
        dossiers_categories.append(os.path.join(self.dossier_source, "Par Taille"))
        
        # Ajouter les dossiers de catégories à la liste à supprimer
        for dossier in dossiers_categories:
            if os.path.isdir(dossier):
                dossiers_a_supprimer.append(dossier)
        
        # Supprimer les dossiers vides
        for dossier in dossiers_a_supprimer:
            try:
                # Vérifier que le dossier existe et est sous le dossier source
                if os.path.isdir(dossier) and dossier.startswith(self.dossier_source):
                    # Vérifier si le dossier est vide
                    if not os.listdir(dossier):
                        os.rmdir(dossier)
                    else:
                        # Tenter de supprimer récursivement les dossiers vides
                        for root, dirs, files in os.walk(dossier, topdown=False):
                            if not files and not dirs:
                                try:
                                    os.rmdir(root)
                                except:
                                    pass
            except Exception as e:
                erreurs.append(f"Erreur lors de la suppression du dossier {dossier}: {str(e)}")
        
        # Supprimer le fichier de sauvegarde après restauration
        try:
            os.remove(sauvegarde_path)
        except:
            pass
            
        return fichiers_restaures, erreurs


class ApplicationTrieurFichiers(ctk.CTk):
    """Classe principale pour l'interface graphique de l'application"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("Trieur de Fichiers Automatique")
        self.geometry("1000x700")
        
        # Centrer la fenêtre
        width = 1000
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        
        # Initialisation des variables
        self.dossier_source_var = tk.StringVar(value="")
        self.type_tri_var = tk.StringVar(value="type")
        self.theme_var = tk.StringVar(value="dark")
        
        # Chargement de la configuration
        self.config = self.charger_config()
        
        # Appliquer le thème
        self.appliquer_theme(self.config.get("theme", "dark"))
        
        # Initialisation du trieur
        self.trieur = TrieurFichiers(self.config)
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Création de l'interface
        self.creer_interface()
        
        # Mise à jour initiale
        self.mise_a_jour_interface()

    def charger_config(self) -> Dict:
        """
        Charge la configuration depuis un fichier
        :return: Dictionnaire de configuration
        """
        chemin_config = os.path.join(os.path.expanduser("~"), ".trieur_fichiers_config.json")
        
        if os.path.isfile(chemin_config):
            try:
                with open(chemin_config, 'r') as f:
                    config = json.load(f)
                return config
            except:
                pass
                
        return CONFIG_PAR_DEFAUT.copy()

    def sauvegarder_config(self):
        """
        Sauvegarde la configuration actuelle
        """
        chemin_config = os.path.join(os.path.expanduser("~"), ".trieur_fichiers_config.json")
        
        # Mettre à jour la configuration avec les valeurs actuelles
        self.config["dossier_source"] = self.dossier_source_var.get()
        self.config["type_tri"] = self.type_tri_var.get()
        self.config["theme"] = self.theme_var.get()
        
        try:
            with open(chemin_config, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")

    def appliquer_theme(self, theme: str):
        """
        Applique le thème spécifié
        :param theme: "dark" ou "light"
        """
        self.theme_var.set(theme)
        
        if theme == "dark":
            ctk.set_appearance_mode("dark")
            self.couleur_bouton = "#8A2BE2"  # Violet
        else:
            ctk.set_appearance_mode("light")
            self.couleur_bouton = "#9370DB"  # Violet plus clair
            
        ctk.set_default_color_theme("blue")  # Base thème customtkinter

    def creer_interface(self):
        """
        Crée les éléments de l'interface graphique
        """
        # Frame du haut pour les options principales
        frame_options = ctk.CTkFrame(self)
        frame_options.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame_options.grid_columnconfigure(1, weight=1)
        
        # Sélection du dossier
        ctk.CTkLabel(frame_options, text="Dossier source:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        frame_dossier = ctk.CTkFrame(frame_options)
        frame_dossier.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        frame_dossier.grid_columnconfigure(0, weight=1)
        
        self.entry_dossier = ctk.CTkEntry(frame_dossier, textvariable=self.dossier_source_var)
        self.entry_dossier.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_parcourir = ctk.CTkButton(
            frame_dossier, 
            text="Parcourir", 
            command=self.selectionner_dossier,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 15, "bold")
        )
        self.btn_parcourir.grid(row=0, column=1, padx=5, pady=5)
        
        # Type de tri
        ctk.CTkLabel(frame_options, text="Type de tri:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        frame_type_tri = ctk.CTkFrame(frame_options)
        frame_type_tri.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.radio_type = ctk.CTkRadioButton(
            frame_type_tri, 
            text="Par type", 
            variable=self.type_tri_var, 
            value="type"
        )
        self.radio_type.grid(row=0, column=0, padx=20, pady=5)
        
        self.radio_date = ctk.CTkRadioButton(
            frame_type_tri, 
            text="Par date", 
            variable=self.type_tri_var, 
            value="date"
        )
        self.radio_date.grid(row=0, column=1, padx=20, pady=5)
        
        self.radio_taille = ctk.CTkRadioButton(
            frame_type_tri, 
            text="Par taille", 
            variable=self.type_tri_var, 
            value="taille"
        )
        self.radio_taille.grid(row=0, column=2, padx=20, pady=5)
        
        # Thème
        ctk.CTkLabel(frame_options, text="Thème:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        frame_theme = ctk.CTkFrame(frame_options)
        frame_theme.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.radio_theme_dark = ctk.CTkRadioButton(
            frame_theme, 
            text="Mode sombre", 
            variable=self.theme_var, 
            value="dark",
            command=lambda: self.appliquer_theme("dark")
        )
        self.radio_theme_dark.grid(row=0, column=0, padx=20, pady=5)
        
        self.radio_theme_light = ctk.CTkRadioButton(
            frame_theme, 
            text="Mode clair", 
            variable=self.theme_var, 
            value="light",
            command=lambda: self.appliquer_theme("light")
        )
        self.radio_theme_light.grid(row=0, column=1, padx=20, pady=5)
        
        # Configuration avancée (Accordéon)
        self.frame_config_avancee = ctk.CTkFrame(self)
        self.frame_config_avancee.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.frame_config_avancee.grid_columnconfigure(0, weight=1)
        
        # Bouton pour ouvrir/fermer les options avancées
        self.btn_toggle_avance = ctk.CTkButton(
            self.frame_config_avancee,
            text="▼ Configuration avancée",
            command=self.toggle_config_avancee,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 15, "bold")
        )
        self.btn_toggle_avance.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Options avancées (initialement cachées)
        self.frame_options_avancees = ctk.CTkFrame(self.frame_config_avancee)
        self.frame_options_avancees.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.frame_options_avancees.grid_columnconfigure(1, weight=1)
        
        # Option sous-dossiers par extension
        self.var_sous_dossiers = tk.BooleanVar(value=self.config.get("sous_dossiers_par_extension", True))
        self.check_sous_dossiers = ctk.CTkCheckBox(
            self.frame_options_avancees,
            text="Créer des sous-dossiers par extension",
            variable=self.var_sous_dossiers
        )
        self.check_sous_dossiers.grid(row=0, column=0, padx=5, pady=5, sticky="w", columnspan=2)
        
        # Personnalisation des noms
        ctk.CTkLabel(self.frame_options_avancees, text="Personnalisation des noms:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        
        self.btn_personnaliser = ctk.CTkButton(
            self.frame_options_avancees,
            text="Personnaliser",
            command=self.ouvrir_personnalisation,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 15, "bold")
        )
        self.btn_personnaliser.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        
        # Masquer les options avancées initialement
        self.frame_options_avancees.grid_remove()
        self.config_avancee_visible = False
        
        # Barre de progression
        self.frame_progression = ctk.CTkFrame(self)
        self.frame_progression.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.frame_progression.grid_columnconfigure(0, weight=1)
        
        self.progressbar = ctk.CTkProgressBar(self.frame_progression)
        self.progressbar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.progressbar.set(0)
        
        self.label_statut = ctk.CTkLabel(self.frame_progression, text="En attente")
        self.label_statut.grid(row=1, column=0, padx=10, pady=5)
        
        # Zone de log
        self.frame_log = ctk.CTkFrame(self)
        self.frame_log.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.frame_log.grid_columnconfigure(0, weight=1)
        self.frame_log.grid_rowconfigure(0, weight=1)
        
        self.text_log = ctk.CTkTextbox(self.frame_log,
                                       wrap=tk.WORD,
                                       font=("Arial", 19)
        )
        self.text_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.text_log.configure(state="disabled")
        
        # Boutons d'action
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.btn_trier = ctk.CTkButton(
            self.frame_actions,
            text="Trier les fichiers",
            command=self.lancer_tri,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 15, "bold")
            
        )
        self.btn_trier.grid(row=0, column=0, padx=10, pady=10)
        
        self.btn_restaurer = ctk.CTkButton(
            self.frame_actions,
            text="Restaurer",
            command=self.restaurer_fichiers,
            fg_color=self.couleur_bouton,
            text_color="white",
            state="disabled",
            font=("Arial", 15, "bold")
        )
        self.btn_restaurer.grid(row=0, column=1, padx=10, pady=10)
        
        self.btn_reinitialiser = ctk.CTkButton(
            self.frame_actions,
            text="Réinitialiser",
            command=self.reinitialiser,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 15, "bold")
        )
        self.btn_reinitialiser.grid(row=0, column=2, padx=10, pady=10)

    def toggle_config_avancee(self):
        """
        Affiche ou masque les options avancées
        """
        if self.config_avancee_visible:
            self.frame_options_avancees.grid_remove()
            self.btn_toggle_avance.configure(text="▼ Configuration avancée")
        else:
            self.frame_options_avancees.grid()
            self.btn_toggle_avance.configure(text="▲ Configuration avancée")
            
        self.config_avancee_visible = not self.config_avancee_visible

    def ouvrir_personnalisation(self):
        """
        Ouvre la fenêtre de personnalisation des noms
        """
        fenetre_perso = ctk.CTkToplevel(self)
        fenetre_perso.title("Personnalisation des noms")
        fenetre_perso.geometry("500x400")
        fenetre_perso.grab_set()  # Rendre la fenêtre modale
        
        # Centrer la fenêtre
        width = 500
        height = 400
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        fenetre_perso.geometry(f"{width}x{height}+{x}+{y}")
        
        # Créer un frame avec scrollbar
        frame_principal = ctk.CTkFrame(fenetre_perso)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer un scrollable frame
        frame_scroll = ctk.CTkScrollableFrame(frame_principal)
        frame_scroll.pack(fill=tk.BOTH, expand=True)
        
        entries = {}
        row = 0
        
        # Créer des entrées pour les types de fichiers
        ctk.CTkLabel(frame_scroll, text="Noms des catégories de fichiers").grid(
            row=row, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )
        row += 1
        
        for type_fichier in TYPES_FICHIERS.keys():
            ctk.CTkLabel(frame_scroll, text=f"{type_fichier}:").grid(
                row=row, column=0, padx=5, pady=5, sticky="w"
            )
            
            nom_actuel = self.config.get("noms_dossiers", {}).get(type_fichier, type_fichier)
            entry = ctk.CTkEntry(frame_scroll)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, nom_actuel)
            
            entries[f"type_{type_fichier}"] = entry
            row += 1
        
        # Séparateur
        ctk.CTkLabel(frame_scroll, text="").grid(row=row, column=0, columnspan=2)
        row += 1
        
        # Créer des entrées pour les catégories de taille
        ctk.CTkLabel(frame_scroll, text="Noms des catégories de taille").grid(
            row=row, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )
        row += 1
        
        for categorie in TAILLES_FICHIERS.keys():
            ctk.CTkLabel(frame_scroll, text=f"{categorie}:").grid(
                row=row, column=0, padx=5, pady=5, sticky="w"
            )
            
            nom_actuel = self.config.get("tailles_fichiers", {}).get(categorie, categorie)
            entry = ctk.CTkEntry(frame_scroll)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, nom_actuel)
            
            entries[f"taille_{categorie}"] = entry
            row += 1
        
        # Boutons de validation
        frame_boutons = ctk.CTkFrame(fenetre_perso)
        frame_boutons.pack(fill=tk.X, padx=10, pady=10)
        
        def sauvegarder_personnalisation():
            # Mettre à jour la configuration avec les valeurs saisies
            noms_dossiers = {}
            tailles_fichiers = {}
            
            for cle, entry in entries.items():
                valeur = entry.get().strip()
                if not valeur:
                    continue
                    
                if cle.startswith("type_"):
                    type_fichier = cle[5:]  # Enlever "type_"
                    noms_dossiers[type_fichier] = valeur
                elif cle.startswith("taille_"):
                    categorie = cle[7:]  # Enlever "taille_"
                    tailles_fichiers[categorie] = valeur
            
            self.config["noms_dossiers"] = noms_dossiers
            self.config["tailles_fichiers"] = tailles_fichiers
            
            # Mettre à jour le trieur
            self.trieur.config = self.config
            
            # Sauvegarder la configuration
            self.sauvegarder_config()
            
            # Fermer la fenêtre
            fenetre_perso.destroy()
        
        btn_annuler = ctk.CTkButton(
            frame_boutons, 
            text="Annuler", 
            command=fenetre_perso.destroy,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 14, "bold")
        )
        btn_annuler.pack(side=tk.LEFT, padx=10, pady=10)
        
        btn_sauvegarder = ctk.CTkButton(
            frame_boutons, 
            text="Sauvegarder", 
            command=sauvegarder_personnalisation,
            fg_color=self.couleur_bouton,
            text_color="white",
            font=("Arial", 14, "bold")
        )
        btn_sauvegarder.pack(side=tk.RIGHT, padx=10, pady=10)

    def selectionner_dossier(self):
        """
        Ouvre une boîte de dialogue pour sélectionner un dossier
        """
        dossier = filedialog.askdirectory(title="Sélectionner un dossier à trier")
        
        if dossier:
            self.dossier_source_var.set(dossier)
            self.config["dossier_source"] = dossier
            self.trieur.dossier_source = dossier
            self.mise_a_jour_interface()
            self.sauvegarder_config()

    def mise_a_jour_interface(self):
        """
        Met à jour l'état des boutons et widgets selon l'état actuel
        """
        dossier = self.dossier_source_var.get()
        
        if dossier and os.path.isdir(dossier):
            self.btn_trier.configure(state="normal")
            
            # Vérifier si une sauvegarde existe
            sauvegarde_path = os.path.join(dossier, ".trieur_sauvegarde.json")
            if os.path.isfile(sauvegarde_path):
                self.btn_restaurer.configure(state="normal")
            else:
                self.btn_restaurer.configure(state="disabled")
        else:
            self.btn_trier.configure(state="disabled")
            self.btn_restaurer.configure(state="disabled")

    def ajouter_log(self, message: str):
        """
        Ajoute un message au log
        :param message: Message à ajouter
        """
        self.text_log.configure(state="normal")
        self.text_log.insert(tk.END, f"{message}\n")
        self.text_log.see(tk.END)
        self.text_log.configure(state="disabled")
        self.update()

    def maj_progression(self, actuel: int, total: int):
        """
        Met à jour la barre de progression
        :param actuel: Position actuelle
        :param total: Total à atteindre
        """
        if total > 0:
            self.progressbar.set(actuel / total)
            self.label_statut.configure(text=f"Progression: {actuel}/{total} fichiers")
        else:
            self.progressbar.set(0)
            self.label_statut.configure(text="Aucun fichier à traiter")
        self.update()

    def lancer_tri(self):
        """
        Lance le processus de tri des fichiers
        """
        dossier = self.dossier_source_var.get()
        
        if not dossier or not os.path.isdir(dossier):
            self.ajouter_log("Erreur: Veuillez sélectionner un dossier valide.")
            return
            
        # Mettre à jour la configuration
        self.config["type_tri"] = self.type_tri_var.get()
        self.config["sous_dossiers_par_extension"] = self.var_sous_dossiers.get()
        self.trieur.config = self.config
        
        # Désactiver les boutons pendant le traitement
        self.btn_trier.configure(state="disabled")
        self.btn_restaurer.configure(state="disabled")
        self.btn_reinitialiser.configure(state="disabled")
        
        # Réinitialiser la barre de progression
        self.progressbar.set(0)
        self.label_statut.configure(text="Préparation du tri...")
        
        # Nettoyer le log
        self.text_log.configure(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.configure(state="disabled")
        
        # Ajouter un message de début
        self.ajouter_log(f"Début du tri des fichiers dans {dossier}...\n")
        self.ajouter_log(f"\nMode de tri: {self.type_tri_var.get()}")
        
        # Lancer le tri dans un thread pour ne pas bloquer l'interface
        def executer_tri():
            try:
                fichiers_traites, erreurs = self.trieur.trier_fichiers(
                    callback=self.maj_progression
                )
                
                # Afficher les résultats
                self.ajouter_log(f"\nTri terminé!\n {fichiers_traites} fichiers traités.")
                
                if erreurs:
                    self.ajouter_log("\nErreurs rencontrées:")
                    for erreur in erreurs:
                        self.ajouter_log(f"- {erreur}")
                
                # Mettre à jour l'interface
                self.after(100, self.mise_a_jour_interface)
                
            except Exception as e:
                self.ajouter_log(f"\nErreur lors du tri: {str(e)}")
            finally:
                # Réactiver les boutons
                self.btn_trier.configure(state="normal")
                self.btn_reinitialiser.configure(state="normal")
                
                # Sauvegarder la configuration
                self.sauvegarder_config()
        
        # Lancer dans un thread séparé
        thread = threading.Thread(target=executer_tri)
        thread.daemon = True
        thread.start()

    def restaurer_fichiers(self):
        """
        Restaure les fichiers à leur emplacement d'origine
        """
        dossier = self.dossier_source_var.get()
        
        if not dossier or not os.path.isdir(dossier):
            self.ajouter_log("Erreur: Aucun dossier de sauvegarde trouvé.")
            return
            
        # Désactiver les boutons pendant le traitement
        self.btn_trier.configure(state="disabled")
        self.btn_restaurer.configure(state="disabled")
        self.btn_reinitialiser.configure(state="disabled")
        
        # Réinitialiser la barre de progression
        self.progressbar.set(0)
        self.label_statut.configure(text="Préparation de la restauration...")
        
        # Nettoyer le log
        self.text_log.configure(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.configure(state="disabled")
        
        # Ajouter un message de début
        self.ajouter_log(f"Début de la restauration des fichiers dans {dossier}...")
        
        # Lancer la restauration dans un thread
        def executer_restauration():
            try:
                fichiers_restaures, erreurs = self.trieur.restaurer_fichiers(
                    callback=self.maj_progression
                )
                
                # Afficher les résultats
                self.ajouter_log(f"\nRestauration terminée!\n {fichiers_restaures} fichiers restaurés.")
                
                if erreurs:
                    self.ajouter_log("\nErreurs rencontrées:")
                    for erreur in erreurs:
                        self.ajouter_log(f"- {erreur}")
                
                # Mettre à jour l'interface
                self.after(100, self.mise_a_jour_interface)
                
            except Exception as e:
                self.ajouter_log(f"\nErreur lors de la restauration: {str(e)}")
            finally:
                # Réactiver les boutons
                self.btn_trier.configure(state="normal")
                self.btn_reinitialiser.configure(state="normal")
        
        # Lancer dans un thread séparé
        thread = threading.Thread(target=executer_restauration)
        thread.daemon = True
        thread.start()

    def reinitialiser(self):
        """
        Réinitialise l'application pour sélectionner un nouveau dossier
        """
        self.dossier_source_var.set("")
        self.trieur.dossier_source = ""
        self.config["dossier_source"] = ""
        self.sauvegarder_config()
        
        # Réinitialiser l'interface
        self.progressbar.set(0)
        self.label_statut.configure(text="En attente")
        
        self.text_log.configure(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.configure(state="disabled")
        
        self.btn_trier.configure(state="disabled")
        self.btn_restaurer.configure(state="disabled")
        
        self.ajouter_log("Application réinitialisée...\n"
                         "\nVeuillez sélectionner un nouveau dossier à trier en cliquant sur le bouton Parcourir.")


def main():
    """
    Fonction principale pour lancer l'application
    """
    app = ApplicationTrieurFichiers()
    app.mainloop()


if __name__ == "__main__":
    main()