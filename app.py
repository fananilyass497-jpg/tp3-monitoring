import logging

from flask import Flask
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

REQUETES = Counter(
    "app_requetes_total",
    "Nombre total de requetes recues par l'application",
    ["route"],
)
ERREURS = Counter(
    "app_erreurs_total",
    "Nombre total d'erreurs simulees par l'application",
)


@app.route("/")
def accueil():
    REQUETES.labels(route="/").inc()
    app.logger.info("Requete sur /")
    return "Bonjour, application supervisee !"


@app.route("/erreur")
def erreur():
    REQUETES.labels(route="/erreur").inc()
    ERREURS.inc()
    app.logger.error("Une erreur simulee s'est produite")
    return "Erreur simulee", 500


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
