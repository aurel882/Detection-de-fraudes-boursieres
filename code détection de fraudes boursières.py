import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

tickers = ["NVDA", "AAPL", "MSFT", "TSLA"]

def compute_indicators(df):
    df["SMA_14"] = df["Close"].rolling(window=14).mean()
    df["pct_change"] = df["Close"].pct_change()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))

    ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    df["volatility_14"] = df["pct_change"].rolling(window=14).std()
    df["gap_open"] = (df["Open"] - df["Close"].shift(1)) / df["Close"].shift(1)
    df["vol_SMA_14"] = df["Volume"].rolling(window=14).mean()
    df["volume_to_volSMA"] = df["Volume"].squeeze() / df["vol_SMA_14"].squeeze()

    return df

def detect_spikes(df):
    price_threshold = df["pct_change"].std() * 3
    df["price_spike"] = df["pct_change"].abs() > price_threshold

    volume_threshold = df["Volume"].std() * 3
    df["volume_spike"] = df["Volume"] > volume_threshold

    df["both_spike"] = df["price_spike"] & df["volume_spike"]
    df["anomalie"] = "rien"
    df.loc[df["price_spike"], "anomalie"] = "prix"
    df.loc[df["both_spike"], "anomalie"] = "les deux"

    df["direction"] = np.nan
    df.loc[df["price_spike"] & (df["pct_change"] > 0), "direction"] = "hausse"
    df.loc[df["price_spike"] & (df["pct_change"] < 0), "direction"] = "baisse"

    df["direction"] = df["direction"].astype(object)

    return df

def flag_fraud(df):
    rsi_extreme = (df["RSI_14"] > 80) | (df["RSI_14"] < 20)
    volatility_high = df["volatility_14"] > (df["volatility_14"].mean() + 2 * df["volatility_14"].std())
    volume_anomaly = df["volume_to_volSMA"] > 3

    macd_abs = df["MACD"].abs()
    seuil_macd = macd_abs.mean() + 2 * macd_abs.std()
    macd_anomaly = macd_abs > seuil_macd

    conditions = rsi_extreme | volatility_high | volume_anomaly | macd_anomaly 
    df["fraud_suspicion"] = np.where(conditions, "suspect", "normal")
    return df

def plot_signals(df, ticker, export_folder):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df["Close"], label="Close", color='blue')

    plt.plot(df[df["both_spike"]].index,
             df[df["both_spike"]]["Close"],
             "mo", label="Spikes combinés")

    only_price_spikes = df["price_spike"] & ~df["both_spike"]
    plt.plot(df[only_price_spikes].index,
             df[only_price_spikes]["Close"],
             "ro", label="Spikes prix")

    plt.plot(df.index, df["SMA_14"], label="SMA 14 jours", color='green', linestyle='--')

    plt.legend()
    plt.title(f"{ticker} - Détection de hausses brutales")
    plt.xlabel("Date")
    plt.ylabel("Prix de clôture ($)")
    plt.grid(True)
    plt.tight_layout()

    # Sauvegarde dans le dossier export demandé
    plot_path = os.path.join(export_folder, f"{ticker}_fraud_detection_plot.png")
    plt.savefig(plot_path)
    plt.close()

    print(f"📈 Plot sauvegardé : {plot_path}")

# === Nouveau dossier d'export ===
export_folder = r"C:/Users/bress/DOCUMENTS/Projet pythoon"
os.makedirs(export_folder, exist_ok=True)

# === Traitement principal ===
all_anomalies = []

for ticker in tickers:
    print(f"\n📊 Traitement de l’action : {ticker}")
    df = yf.download(ticker, start="2023-01-01", end="2024-12-31")

    if df.empty:
        print(f"⚠️ Données manquantes pour {ticker}.")
        continue

    df = compute_indicators(df)
    df = detect_spikes(df)
    df = flag_fraud(df)
    plot_signals(df, ticker, export_folder)

    anomalies = df[df["anomalie"] != "rien"][[ 
        "Close", "Volume", "pct_change", "anomalie", "direction", 
        "SMA_14", "RSI_14", "MACD", "MACD_signal", "volatility_14", 
        "gap_open", "volume_to_volSMA", "fraud_suspicion"
    ]].copy()

    anomalies["pct_change"] = (anomalies["pct_change"] * 100).round(2).astype(str) + " %"
    anomalies = anomalies.reindex(anomalies["pct_change"].str.rstrip(" %").astype(float).abs().sort_values(ascending=False).index)

    anomalies["Ticker"] = ticker  # Ajout de la colonne Ticker
    all_anomalies.append(anomalies)

    print(f"\n📋 Anomalies détectées enrichies pour {ticker} :")
    print(anomalies.head(10))

    # Export CSV dans le dossier demandé
    anomalies.to_csv(os.path.join(export_folder, f"{ticker}_anomalies_enriched_with_fraud.csv"))
    print(f"📁 Export terminé : {os.path.join(export_folder, f'{ticker}_anomalies_enriched_with_fraud.csv')}")

# === Export global ===
if all_anomalies:
    df_global = pd.concat(all_anomalies)
    df_global.to_csv(os.path.join(export_folder, "global_anomalies.csv"))
    print(f"\n✅ Export global terminé : {os.path.join(export_folder, 'global_anomalies.csv')}")
else:
    print("\n❌ Aucune anomalie détectée sur l’ensemble des tickers.")
