# Stock Analysis RAG System

A real-time stock analysis system that scrapes financial news from Yahoo Finance, MarketWatch, and Seeking Alpha, then uses RAG (Retrieval-Augmented Generation) to provide comprehensive AI-powered investment analysis.

## Files

### Core System
- **`rag_system.py`** - Main RAG system with web scraping and AI analysis
- **`requirements.txt`** - Python dependencies
- **`.env`** - Environment variables (contains your OpenAI API key)

### User Interfaces
- **`desktop_app.py`** - Desktop GUI application (recommended)
- **`flask_app.py`** - Web application (if you prefer browser interface)
- **`templates/index.html`** - Web interface HTML

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the desktop app:**
   ```bash
   python desktop_app.py
   ```

3. **Or run the web app:**
   ```bash
   python flask_app.py
   ```
   Then open http://127.0.0.1:9000

## Features

- ✅ Real-time scraping from Yahoo Finance, MarketWatch, Seeking Alpha
- ✅ RAG-powered analysis using most relevant financial information  
- ✅ AI-generated comprehensive paragraph analysis
- ✅ Professional investment language with source attribution
- ✅ Current stock prices, earnings data, and market sentiment

## Usage

Enter any stock symbol (e.g., GOOG, AAPL, TSLA) and get instant analysis based on the latest financial news!