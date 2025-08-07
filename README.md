# Financial RAG System 📊

A real-time stock analysis system that scrapes financial news from Yahoo Finance, MarketWatch, and Seeking Alpha, then uses RAG (Retrieval-Augmented Generation) to provide comprehensive AI-powered investment analysis.

![Stock Analysis Demo](https://img.shields.io/badge/demo-live-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-web%20app-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange)

## 🚀 Features

- ✅ **Real-time scraping** from Yahoo Finance, MarketWatch, and Seeking Alpha
- ✅ **RAG-powered analysis** using most relevant financial information  
- ✅ **AI-generated comprehensive analysis** with professional investment language
- ✅ **Beautiful web interface** with modern, responsive design
- ✅ **Source attribution** with transparent data sourcing
- ✅ **Quick analysis** for popular stocks (AAPL, GOOGL, TSLA, etc.)

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/IshanAhluwalia/RAG-based-Stock-Project.git
   cd RAG-based-Stock-Project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   Navigate to `http://127.0.0.1:7777`

## 🎯 Usage

1. Enter any stock symbol (e.g., AAPL, GOOGL, TSLA, MSFT, NVDA, AMZN)
2. Click "Analyze Stock" or use the quick-access buttons
3. Get comprehensive AI-powered analysis based on real-time financial news
4. View analysis with source attribution and timestamps

## 🏗️ Project Structure

```
├── app.py              # Flask web application with beautiful UI
├── rag_system.py       # Core RAG system with web scraping and AI analysis
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── .gitignore         # Git ignore file
└── .env              # Environment variables (not tracked)
```

## 🔍 How It Works

1. **Data Collection**: Scrapes real-time financial news from multiple sources
2. **Vector Indexing**: Uses FAISS and SentenceTransformers for semantic search
3. **Retrieval**: Finds most relevant articles for the queried stock
4. **Analysis Generation**: Uses OpenAI GPT-3.5 to generate comprehensive analysis
5. **Web Interface**: Presents results in a professional, news-style format

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **AI/ML**: OpenAI GPT-3.5, SentenceTransformers, FAISS
- **Web Scraping**: BeautifulSoup, Requests
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Sources**: Yahoo Finance, MarketWatch, Seeking Alpha

## 📝 Example Analysis

The system generates comprehensive paragraphs covering:
- Current market sentiment and performance
- Recent financial developments and earnings
- Investment opportunities and risks
- Professional recommendations with source attribution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. Always consult with a qualified financial advisor before making investment decisions.