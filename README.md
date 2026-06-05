Crypto Market Data & Analytics Application

A full-stack application for tracking, analyzing, and generating trading signals on cryptocurrency market data. The backend is built with Python (FastAPI, SQLAlchemy, Pandas, NumPy) and automatically ingests live price and volume data for the top 10 crypto assets from the CoinGecko public API every 15 minutes via APScheduler. Data is persisted in SQLite and exposed through a set of async REST endpoints covering market snapshots, historical records, analytics, and strategy execution.

The analytics module computes per-asset price change, volume change, and momentum scores over a configurable lookback window. The strategy module implements two rule-based signal generators — Moving Average Crossover and Momentum Threshold — each returning BUY / SELL / HOLD signals with human-readable reasoning. Strategies are isolated pure functions registered in a central registry, making them easy to test and extend.

The frontend is a responsive single-page React application (no build step required) with three views: a live markets table with per-asset price charts, an analytics dashboard with a bar chart comparison, and a strategy panel where users can configure and trigger signal generation interactively.

---


