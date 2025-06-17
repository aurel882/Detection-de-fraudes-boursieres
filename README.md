# Analyse et Détection d'Anomalies sur Actions Boursières

Ce projet Python permet de récupérer les données historiques de plusieurs actions (tickers), de calculer des indicateurs techniques, de détecter des hausses ou baisses brutales ainsi que des anomalies potentielles, et de générer des graphiques et rapports CSV pour faciliter l’analyse.

---

## Fonctionnalités principales

- Récupération des données boursières avec **yfinance**.
- Calcul des indicateurs techniques :
  - Moyenne mobile simple (SMA 14 jours)
  - RSI (Relative Strength Index) 14 jours
  - MACD et sa ligne signal
  - Volatilité sur 14 jours
  - Ratio volume / moyenne mobile du volume
  - Gap d’ouverture
- Détection de "spikes" (hausses/baises brutales) sur les prix et volumes.
- Identification de signaux potentiels de fraudes basés sur des seuils extrêmes d’indicateurs.
- Génération automatique de graphiques des prix avec points marquant les anomalies.
- Export des anomalies enrichies dans des fichiers CSV par ticker ainsi qu’un fichier global.

---

## Utilisation

1 - Modifier la liste des tickers dans le fichier principal si besoin :
  tickers = ["NVDA", "AAPL", "MSFT", "TSLA"]
  
2 - Modifier le dossier d’export export_folder pour indiquer où sauvegarder les résultats.

3 - Lancer le script

Le script téléchargera les données entre le 01/01/2023 et le 31/12/2024, calculera les indicateurs, détectera les anomalies, générera les graphiques, et exportera les fichiers CSV dans le dossier spécifié.

## Résultats 
-Pour chaque ticker, un fichier CSV avec les anomalies détectées et leurs indicateurs calculés.

-Un fichier CSV global regroupant toutes les anomalies détectées sur tous les tickers.

-Des graphiques PNG illustrant les prix et points d’anomalies.

## Explications techniques

### Indicateurs calculés :
-SMA_14 : Moyenne mobile simple sur 14 jours

-RSI_14 : Indice de force relative sur 14 jours

-MACD : Différence entre EMA 12 et EMA 26

-MACD_signal : EMA 9 de la MACD

-volatility_14 : Écart-type du pourcentage de variation sur 14 jours

-volume_to_volSMA : ratio entre volume du jour et moyenne mobile 14 jours du volume

### Détection des anomalies :

-Spikes prix et volume définis par seuils à 3 écarts-types.

-Suspicion de fraude marquée si RSI extrême, volatilité élevée, volume anormal ou MACD anormal.

## Auteurs 

Aurélien Bresson

## Licence 

Ce projet est sous licence MIT.

