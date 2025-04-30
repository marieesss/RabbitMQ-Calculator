# Projet RabbitMQ Calculator

RabbitMQ Calculator est un projet fonctionnant avec RabbitMQ avec un producteur et quatre consommateurs.
Chacun d'entre eux (consumer) ayant la responsabilité du traitement d'un type de calcul (add, sub, mul, div)

## Démarrage
Pré-requis : avoir Docker installé et prêt à l'emploi

Après avoir cloné le répertoire dans l'endroit de votre choix, éxecuter la commande à la racine
```bash
docker compose up --build
```

## Visionnage des logs
Le contenaire worker_logs contient la trace des calculs effectués par les workers

## Effectué une requête manuelle
Pour pousser un type de rêquete manuellement 
```bash
curl --location 'http://localhost:8000/' \
--header 'Content-Type: application/json' \
--data '{
    "operation" : "all"
}'
```
### Remarque : 
- n1 et n2 sont toujours aléatoires
- Type d'opération accepté : addition / multiplication / soustraction / division / all

## Rapport 
