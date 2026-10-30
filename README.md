# TP 3 — Monitoring et observabilité

Ce projet supervise une application Flask avec Prometheus et Grafana. Prometheus collecte les compteurs toutes les 5 secondes, Grafana charge automatiquement le tableau de bord et Prometheus déclenche une alerte si l’application reste arrêtée pendant 15 secondes.

## Architecture

- Flask écoute sur le port 5000 et expose les mesures à l’adresse /metrics.
- Prometheus écoute sur le port 9090, collecte les mesures et évalue la règle d’alerte.
- Grafana écoute sur le port 3000 et affiche les mesures de Prometheus.

## Démarrage

Prérequis : Docker Desktop installé et démarré.

Dans PowerShell, depuis ce dossier :

    docker compose config
    docker compose up -d --build
    docker compose ps

Pages à ouvrir :

- Application : http://localhost:5000
- Mesures brutes : http://localhost:5000/metrics
- Cibles Prometheus : http://localhost:9090/targets
- Alertes Prometheus : http://localhost:9090/alerts
- Grafana : http://localhost:3000 (identifiant admin, mot de passe admin)

La source Prometheus et le tableau de bord sont préconfigurés. Dans Grafana, ouvrir Dashboards, puis le dossier TP Monitoring et le tableau Supervision application. Les panneaux affichent le débit de requêtes, le nombre d’erreurs et l’état UP/DOWN de l’application.

## Générer du trafic et lire les journaux

Depuis PowerShell :

    1..30 | ForEach-Object { curl.exe -s http://localhost:5000/ > $null }
    1..10 | ForEach-Object { curl.exe -s http://localhost:5000/erreur > $null }

Les appels à /erreur renvoient volontairement HTTP 500. Voir les journaux avec :

    docker compose logs app

Pour les suivre en direct :

    docker compose logs -f app

## Requêtes PromQL

Dans http://localhost:9090, essayer :

- up : 1 signifie que la cible est joignable.
- app_requetes_total : compteur total, avec une série par route.
- app_erreurs_total : nombre total d’erreurs simulées.
- rate(app_requetes_total[1m]) : débit récent de requêtes par seconde.
- sum by (route) (rate(app_requetes_total[1m])) : débit affiché dans le premier panneau Grafana.

## Vérifier l’alerte

1. Ouvrir http://localhost:9090/alerts et vérifier que ApplicationArretee est Inactive.
2. Lancer docker compose stop app.
3. Actualiser /targets : la cible doit passer à DOWN.
4. Après environ 15 secondes, actualiser /alerts : l’alerte doit passer à Firing.
5. Lancer docker compose start app et attendre le retour à UP, puis Inactive.

## Résultats vérifiés

- docker compose config : configuration valide.
- promtool check config et promtool check rules : configuration Prometheus et règle d’alerte valides.
- Après génération du trafic, Prometheus a remonté 30 requêtes sur /, 10 sur /erreur, 10 erreurs et up=1.
- Les journaux contenaient 30 lignes INFO et 10 lignes ERROR.
- L’API Grafana a confirmé la source Prometheus et le tableau Supervision application avec ses trois panneaux.
- Pendant l’arrêt de Flask, ApplicationArretee est passée à Firing. Après le redémarrage, la cible est revenue à up=1 et l’alerte a disparu.

## Nettoyage

    docker compose down

Les fichiers restent disponibles et la stack peut être reconstruite avec docker compose up -d --build.

## Réponses et bilan du TP

Le monitoring répond à la question « est-ce que le service fonctionne et y a-t-il une anomalie ? ». L’observabilité exploite plusieurs signaux pour expliquer l’origine de cette anomalie : les métriques montrent ce qui évolue, les journaux donnent le contexte et les traces permettent de suivre une requête entre plusieurs services.

Dans ce TP, Flask expose les mesures et écrit les journaux, Prometheus collecte les mesures et applique la règle d’alerte, et Grafana rend les mesures lisibles dans un tableau de bord. La supervision est décrite dans des fichiers versionnables, ce qui rend le déploiement reproductible.
