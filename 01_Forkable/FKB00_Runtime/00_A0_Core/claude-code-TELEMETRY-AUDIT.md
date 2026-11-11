# Audit télémétrie — claude-code (D-N048 V3b, variante D12)

**Fork :** `Amdkn/claude-code`, gel `0ed9469`. **Amont sans licence libre** (`LICENSE.md` = « © Anthropic PBC. All rights reserved », API GitHub `license: null`). **Variante D12 : scan de référence seulement — aucun code amont exécuté, aucun identifiant, aucune copie.**

## 1. Scan statique

- **Aucun SDK télémétrie tiers dans ce dépôt** (pas de PostHog / Segment / Sentry / Mixpanel / Amplitude dans un manifeste de dépendances — il n'y a pas de `package.json` à la racine : ce dépôt est la documentation, les exemples, les hooks et les plugins du CLI, pas le code source du CLI lui-même, distribué par installateur / npm `@anthropic-ai/claude-code`).
- **115 fichiers** contiennent un mot-clé du champ lexical télémétrie (scan `posthog|segment|mixpanel|amplitude|sentry|telemetry|analytics|datadog|bugsnag`) — la quasi-totalité est de la documentation ou des tests : `CHANGELOG.md`, `feed.xml`, `examples/settings/README-hipaa.md`, les hooks d'exemple `mods/agents-md/hooks/telemetry/` et le mod `mods/telemetry/`.
- **Un seul appel réseau de télémétrie dans le dépôt**, dans le mod d'exemple `mods/telemetry/` (voir §2). Aucun autre `fetch(` / appel HTTP sortant dans `mods/` hors documentation et types.
- **Position publique de l'amont** (`README.md`, section « Data collection, usage, and retention ») : « When you use Claude Code, we collect feedback, which includes usage data (such as code acceptance or rejections), associated conversation data, and user feedback submitted via the `/bug` command » — renvoi aux politiques de données et aux Commercial Terms of Service.

## 2. Ce que l'amont ferait

Le mod `mods/telemetry/` (README dédié, hooks d'exemple) décrit le mécanisme de télémétrie du CLI, tel que documenté par l'amont :

- **Événements** : `$.telemetry.log({ event, props })` (une ligne par événement, préfixe `tengu_plugin_<event>`) et `$.telemetry.mark({ feature, kind, reason?, props? })` (marque d'usage, `tengu_feature_<kind>`). Gate `telemetry.*` : seuls les plugins intégrés au CLI sont servis, les autres sont refusés.
- **Envoi** : les lignes partent par lots — **un POST vers `https://api.anthropic.com/api/event_logging/v2/batch`** (fichier `mods/telemetry/hooks/entries/ingest-url.ts`), avec le credential de la session (`$.session.authorize()`), quelques secondes après la première ligne, ou à 100 lignes, ou à la fin de session ; un lot refusé (erreur serveur, timeout, rate limit) est retenté une fois.
- **Contenu d'une ligne** (documenté dans le README du mod) : id d'événement, id d'appareil de l'installation, ids du compte connecté (config globale du CLI), id de session, modèle, type de client, point d'entrée, interactivité, bloc `env` (plateforme et architecture via un probe `uname`, terminal, shell, gestionnaires de paquets et runtimes, CI et GitHub Actions, conteneur distant, déploiement, distribution et noyau Linux, WSL, contrôle de version du répertoire, version du moteur), hash du remote du dépôt. Rien de libre : noms d'événements et clés en snake_case, valeurs = nombre fini, booléen ou choix dans une liste fermée ; `mark` accepte `ok`, `sad` ou `bad` (raison exigée sur les deux derniers).
- **Interrupteurs documentés (lu avant chaque lot ; si illisibles, rien n'est envoyé)** : `DISABLE_TELEMETRY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DO_NOT_TRACK`, exécution de test, fournisseur tiers (Bedrock, Vertex, Foundry et similaires), passerelle cloud, déploiement avec sa propre URL OAuth. Exemple de settings HIPAA : `CLAUDE_CODE_ENABLE_TELEMETRY: "1"` (opt-in explicite dans cet exemple) et envoi OpenTelemetry vers le collecteur de l'opérateur avec textes de prompts/réponses et contenus d'outils coupés.

## 3. Position clean-room (D12)

- **L'adapter A'Space ne reprend rien de ce mécanisme** : il ne contient aucun appel réseau, aucun SDK, aucune clé, aucun endpoint. Le faux (mock) local utilisé par le smoke test n'émet aucun trafic (vérifié par inspection : aucun `socket` / `urllib` / `requests` dans le code de l'adapter).
- **Le contrat décrit l'interface documentée uniquement** (commande `claude`, modes de permission documentés, clés de settings nommées dans les exemples, événements `telemetry.log` / `telemetry.mark` et interrupteurs) — il ne réimplémente pas le CLI et n'envoie rien vers `api.anthropic.com` ni ailleurs.
- **Repli suppression nommé** : si Anthropic s'oppose à la référence ou si une licence apparaît qui l'exige, le fork `Amdkn/claude-code` est supprimé ; l'adapter clean-room, œuvre propre, reste la propriété d'A'Space et ne dépend d'aucun fichier amont.

## Conclusion

**Télémétrie réelle dans l'amont, documentée par l'amont lui-même** : collecte d'usage et de conversations (déclaration README), ingest `api.anthropic.com/api/event_logging/v2/batch`, interrupteurs `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` / `DO_NOT_TRACK` lus avant chaque lot. **Télémétrie zéro dans l'adaptation** : le contrat clean-room et son faux local n'émettent rien, par construction (aucun code réseau dans l'adapter).
