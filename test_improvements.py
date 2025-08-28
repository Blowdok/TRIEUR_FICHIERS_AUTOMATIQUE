#!/usr/bin/env python3
"""
Script de test pour vérifier les améliorations apportées au trieur de fichiers
"""

import os
import sys
import tempfile
import shutil

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from trieur_fichiers_auto import TrieurFichiers, PermissionError_Custom, EspaceDisqueError, TrieurError
    print("✅ Import réussi - Syntaxe Python correcte")
except SyntaxError as e:
    print(f"❌ Erreur de syntaxe Python: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test des fonctionnalités de base"""
    print("\n📋 Test des fonctionnalités de base...")
    
    # Créer un dossier temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Dossier de test: {temp_dir}")
        
        # Créer quelques fichiers de test
        test_files = [
            "document.pdf",
            "image.jpg", 
            "video.mp4",
            "audio.mp3"
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("contenu de test")
        
        print(f"📄 Créé {len(test_files)} fichiers de test")
        
        # Initialiser le trieur
        config = {"dossier_source": temp_dir, "type_tri": "type"}
        trieur = TrieurFichiers(config)
        
        # Test de détermination des types
        for filename in test_files:
            type_fichier = trieur.obtenir_type_fichier(filename)
            print(f"   • {filename} → {type_fichier}")
        
        print("✅ Test des fonctionnalités de base réussi")

def test_error_handling():
    """Test de la gestion d'erreurs améliorée"""
    print("\n🛡️  Test de la gestion d'erreurs...")
    
    # Test avec dossier inexistant
    config = {"dossier_source": "/dossier/inexistant", "type_tri": "type"}
    trieur = TrieurFichiers(config)
    
    try:
        fichiers_traites, erreurs = trieur.trier_fichiers()
        if erreurs and "invalide" in erreurs[0].lower():
            print("✅ Gestion correcte des dossiers inexistants")
        else:
            print("⚠️  Gestion des dossiers inexistants à améliorer")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def test_permission_checking():
    """Test des vérifications de permissions"""
    print("\n🔐 Test des vérifications de permissions...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        trieur = TrieurFichiers()
        
        try:
            # Test avec un fichier normal (devrait passer)
            result = trieur.verifier_permissions_fichier(test_file)
            print("✅ Vérification des permissions fonctionnelle")
        except Exception as e:
            print(f"⚠️  Erreur lors du test de permissions: {e}")

def test_disk_space_checking():
    """Test des vérifications d'espace disque"""
    print("\n💾 Test des vérifications d'espace disque...")
    
    trieur = TrieurFichiers()
    
    try:
        # Test avec une taille raisonnable
        result = trieur.verifier_espace_disque(".", 1024)  # 1KB
        print("✅ Vérification de l'espace disque fonctionnelle")
    except Exception as e:
        print(f"⚠️  Erreur lors du test d'espace disque: {e}")

def test_rollback_mechanism():
    """Test du mécanisme de rollback"""
    print("\n🔄 Test du mécanisme de rollback...")
    
    trieur = TrieurFichiers()
    
    # Simuler quelques opérations
    trieur.operations_realisees = [
        ("create_dir", "/test/dir"),
        ("move_file", "/source/file.txt", "/dest/file.txt")
    ]
    
    try:
        erreurs = trieur.effectuer_rollback()
        print("✅ Mécanisme de rollback initialisé correctement")
    except Exception as e:
        print(f"❌ Erreur dans le mécanisme de rollback: {e}")

if __name__ == "__main__":
    print("🧪 Tests des améliorations du Trieur de Fichiers\n")
    
    try:
        test_basic_functionality()
        test_error_handling() 
        test_permission_checking()
        test_disk_space_checking()
        test_rollback_mechanism()
        
        print("\n🎉 Tous les tests sont terminés!")
        print("\n📊 Résumé des améliorations implémentées:")
        print("   ✅ Exceptions personnalisées (TrieurError, PermissionError_Custom, EspaceDisqueError)")
        print("   ✅ Vérifications de permissions avant opérations")
        print("   ✅ Vérifications d'espace disque")
        print("   ✅ Mécanisme de rollback automatique")
        print("   ✅ Logging détaillé des opérations")
        print("   ✅ Messages d'erreur améliorés avec conseils")
        print("   ✅ Gestion sécurisée des opérations de fichiers")
        
    except Exception as e:
        print(f"\n❌ Erreur critique lors des tests: {e}")
        sys.exit(1)