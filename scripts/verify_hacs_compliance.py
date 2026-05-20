#!/usr/bin/env python3
"""
Script de vérification de conformité HACS.

Ce script vérifie que votre intégration est prête pour être publiée sur HACS.

Usage:
    python scripts/verify_hacs_compliance.py
"""

import json
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
INTEGRATION_DIR = PROJECT_DIR / "custom_components" / "regiedeseauxmpl"


def check_file_exists(path: Path, description: str) -> tuple[bool, str]:
    """Check if a file exists."""
    if path.exists():
        return True, f"✅ {description} : {path.relative_to(PROJECT_DIR)}"
    return False, f"❌ {description} : MANQUANT ({path.relative_to(PROJECT_DIR)})"


def check_json_file(path: Path, required_keys: list[str], description: str) -> tuple[bool, str, list[str]]:
    """Check if a JSON file exists and has required keys."""
    if not path.exists():
        return False, f"❌ {description} : MANQUANT ({path.relative_to(PROJECT_DIR)})", []
    
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            return False, f"⚠️  {description} : Champs manquants: {', '.join(missing_keys)}", missing_keys
        
        return True, f"✅ {description} : OK", []
    except json.JSONDecodeError:
        return False, f"❌ {description} : JSON invalide ({path.relative_to(PROJECT_DIR)})", []


def main():
    """Run all checks."""
    print("\n" + "="*70)
    print("VÉRIFICATION DE CONFORMITÉ HACS")
    print("="*70 + "\n")
    
    all_passed = True
    results = []
    
    # ========================================================================
    # 1. Structure du dépôt
    # ========================================================================
    print("📁 **Structure du dépôt**\n")
    
    checks = [
        (INTEGRATION_DIR, "Dossier custom_components/regiedeseauxmpl"),
        (INTEGRATION_DIR / "__init__.py", "Fichier __init__.py"),
        (INTEGRATION_DIR / "manifest.json", "Fichier manifest.json"),
        (INTEGRATION_DIR / "api.py", "Fichier api.py"),
        (INTEGRATION_DIR / "config_flow.py", "Fichier config_flow.py"),
        (INTEGRATION_DIR / "coordinator.py", "Fichier coordinator.py"),
        (INTEGRATION_DIR / "sensor.py", "Fichier sensor.py"),
        (INTEGRATION_DIR / "entity.py", "Fichier entity.py"),
        (INTEGRATION_DIR / "const.py", "Fichier const.py"),
        (INTEGRATION_DIR / "exceptions.py", "Fichier exceptions.py"),
        (INTEGRATION_DIR / "diagnostics.py", "Fichier diagnostics.py"),
        (INTEGRATION_DIR / "services.yaml", "Fichier services.yaml"),
        (INTEGRATION_DIR / "strings.json", "Fichier strings.json"),
        (INTEGRATION_DIR / "info.md", "Fichier info.md"),
        (INTEGRATION_DIR / "translations" / "fr.json", "Traduction FR"),
        (INTEGRATION_DIR / "translations" / "en.json", "Traduction EN"),
        (INTEGRATION_DIR / "brand" / "icon.svg", "Icône (brand/icon.svg)"),
        (PROJECT_DIR / "hacs.json", "Fichier hacs.json (racine)"),
        (PROJECT_DIR / "README.md", "Fichier README.md"),
        (PROJECT_DIR / "LICENSE", "Fichier LICENSE"),
        (PROJECT_DIR / "CHANGELOG.md", "Fichier CHANGELOG.md"),
        (PROJECT_DIR / "pyproject.toml", "Fichier pyproject.toml"),
        (PROJECT_DIR / ".gitignore", "Fichier .gitignore"),
    ]
    
    for path, description in checks:
        passed, message = check_file_exists(path, description)
        results.append((passed, message))
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    # ========================================================================
    # 2. Vérification manifest.json
    # ========================================================================
    print("\n📋 **Vérification manifest.json**\n")
    
    manifest_required = [
        "domain", "name", "documentation", "issue_tracker", 
        "codeowners", "version", "requirements", "iot_class",
        "integration_type", "config_flow", "license"
    ]
    
    passed, message, missing = check_json_file(
        INTEGRATION_DIR / "manifest.json",
        manifest_required,
        "manifest.json"
    )
    results.append((passed, message))
    print(f"  {message}")
    if missing:
        print(f"     Champs manquants: {', '.join(missing)}")
        all_passed = False
    
    # Vérifier la version
    try:
        with open(INTEGRATION_DIR / "manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        version = manifest.get("version", "")
        if version:
            print(f"  ✅ Version : {version}")
        else:
            print(f"  ❌ Version manquante")
            all_passed = False
    except Exception:
        pass
    
    # ========================================================================
    # 3. Vérification hacs.json
    # ========================================================================
    print("\n📋 **Vérification hacs.json**\n")
    
    hacs_required = ["name", "category", "iot_class"]
    
    passed, message, missing = check_json_file(
        PROJECT_DIR / "hacs.json",
        hacs_required,
        "hacs.json"
    )
    results.append((passed, message))
    print(f"  {message}")
    if missing:
        print(f"     Champs manquants: {', '.join(missing)}")
        all_passed = False
    
    # ========================================================================
    # 4. Vérification des tests
    # ========================================================================
    print("\n🧪 **Vérification des tests**\n")
    
    test_files = [
        PROJECT_DIR / "tests" / "conftest.py",
        PROJECT_DIR / "tests" / "test_api_auth.py",
        PROJECT_DIR / "tests" / "test_meter_index.py",
        PROJECT_DIR / "tests" / "test_coordinator.py",
        PROJECT_DIR / "tests" / "test_sensor.py",
    ]
    
    for path in test_files:
        passed, message = check_file_exists(path, f"Test {path.name}")
        results.append((passed, message))
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    # ========================================================================
    # 5. Vérification des fichiers inutiles (standalone)
    # ========================================================================
    print("\n🗑️ **Vérification des fichiers inutiles**\n")
    
    unwanted_files = [
        PROJECT_DIR / "standalone.py",
        PROJECT_DIR / "test_standalone.py",
        PROJECT_DIR / "STANDALONE_README.md",
    ]
    
    has_unwanted = False
    for path in unwanted_files:
        if path.exists():
            print(f"  ❌ Fichier standalone à supprimer : {path.relative_to(PROJECT_DIR)}")
            results.append((False, f"Supprimer {path.name}"))
            has_unwanted = True
            all_passed = False
    
    if not has_unwanted:
        print(f"  ✅ Aucun fichier standalone détecté")
        results.append((True, "Aucun fichier standalone"))
    
    # ========================================================================
    # 6. Vérification GitHub Actions
    # ========================================================================
    print("\n🚀 **Vérification GitHub Actions**\n")
    
    workflow_files = [
        PROJECT_DIR / ".github" / "workflows" / "test_and_release.yml",
        PROJECT_DIR / ".github" / "workflows" / "hacs_validation.yml",
    ]
    
    for path in workflow_files:
        passed, message = check_file_exists(path, f"Workflow {path.name}")
        results.append((passed, message))
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    # ========================================================================
    # Résumé
    # ========================================================================
    print("\n" + "="*70)
    if all_passed:
        print("✅ **TOUT EST CONFORME !**")
        print("Votre intégration est prête pour être publiée sur HACS.")
    else:
        print("❌ **CORRECTIONS NÉCESSAIRES**")
        print("Voir les erreurs ci-dessus.")
    print("="*70 + "\n")
    
    # Statistiques
    passed_count = sum(1 for p, _ in results if p)
    total_count = len(results)
    print(f"📊 Résultats : {passed_count}/{total_count} vérifications passées\n")
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
