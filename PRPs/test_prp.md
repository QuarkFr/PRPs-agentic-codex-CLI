name: "PRP de test du runner Codex"
description: |
  PRP minimaliste utilisé pour valider que le script `PRPs/scripts/prp_runner.py`
  (driver Codex CLI) fonctionne en modes interactif, json et stream-json.

---

## Goal

**Feature Goal**: Valider le passage de prompt et la sortie du runner.

**Deliverable**: Exécution sans erreur et messages de confirmation visibles côté agent.

**Success Definition**: L'agent confirme avoir lu ce PRP et affiche "PRP TEST OK".

## User Persona (if applicable)

**Target User**: Développeur testant l’intégration Codex CLI.

**Use Case**: Sanity-check du pipeline PRP → runner → CLI.

**User Journey**: Lancer le runner avec ce PRP et observer la sortie.

**Pain Points Addressed**: Tester sans modifier le code ni dépendre de services externes.

## Why

- Permet de tester rapidement `prp_runner.py` sans toucher au code.
- Sert d’exemple de PRP simple compatible avec le flux Codex.
- Réduit le bruit: aucune création de fichier ni appel réseau requis.

## What

L’agent doit:
- Lire ce PRP et confirmer la compréhension.
- Ne créer/modifier aucun fichier.
- Afficher "PRP TEST OK" dans sa sortie.

### Success Criteria

- [ ] L’agent imprime "PRP TEST OK".
- [ ] Aucune erreur n’est rapportée par le runner.
- [ ] Aucun fichier du repo n’est modifié.

## All Needed Context

### Documentation & References

```yaml
- file: PRPs/scripts/prp_runner.py
  why: Runner Python à tester (driver Codex par défaut)
  gotcha: Utiliser --driver/--output-format selon le mode de test
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: Ce PRP est un test sans I/O; ne pas créer/modifier de fichiers.
# CRITICAL: Ne pas effectuer d’appels réseau ni lancer de serveurs.
```

## Implementation Blueprint

```yaml
Task 1: Confirmer lecture du PRP
  - ACTION: Afficher un court résumé de ce PRP

Task 2: Imprimer le message de validation
  - ACTION: Afficher exactement "PRP TEST OK"

Task 3: Conclure proprement
  - ACTION: Signaler DONE/terminé sans modification de code
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
echo "Validation syntaxe/style simulée: OK"
```

### Level 2: Unit Tests (Component Validation)

```bash
python - << 'PY'
print("Validation unitaire simulée: OK")
PY
```

### Level 3: Integration Testing (System Validation)

```bash
echo "Validation intégration simulée: OK"
```

### Level 4: Creative & Domain-Specific Validation

```bash
echo "Validation spécifique simulée: OK"
```

## Final Validation Checklist

- [ ] Message "PRP TEST OK" présent dans la sortie de l’agent
- [ ] Aucune écriture disque ni réseau
- [ ] Aucune erreur remontée par le runner

