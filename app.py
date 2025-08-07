from flask import Flask, render_template_string, request, jsonify
import os
from dotenv import load_dotenv
from rag_system import StockRAGSystem

load_dotenv()

app = Flask(__name__)

# Professional news-style HTML template
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Financial News Hub - Stock Analysis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Georgia', 'Times New Roman', serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: #1a1a2e;
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .tagline {
            font-size: 14px;
            color: #ccc;
            font-style: italic;
        }
        
        .search-container {
            background: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .search-title {
            font-size: 36px;
            color: #1a1a2e;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .search-subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 18px;
        }
        
        .search-box {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .search-input {
            padding: 15px 20px;
            font-size: 18px;
            border: 3px solid #e0e0e0;
            border-radius: 8px;
            width: 300px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            border-color: #00d4ff;
            box-shadow: 0 0 15px rgba(0,212,255,0.3);
        }
        
        .search-btn {
            padding: 15px 30px;
            font-size: 18px;
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,212,255,0.4);
        }
        
        .popular-stocks {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .stock-chip {
            background: #f0f8ff;
            color: #0066cc;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            font-weight: 500;
        }
        
        .stock-chip:hover {
            background: #0066cc;
            color: white;
            transform: translateY(-1px);
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .loading {
            background: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #00d4ff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .article-container {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin: 20px 0;
            opacity: 0;
            animation: slideUp 0.6s ease forwards;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .article-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            position: relative;
        }
        
        .article-header::before {
            content: '';
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23ffffff20' viewBox='0 0 100 100'%3E%3Cpath d='M20 20h60v60H20z'/%3E%3C/svg%3E") repeat;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: 0.05;
        }
        
        .stock-symbol {
            font-size: 48px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 5px;
            position: relative;
        }
        
        .article-title {
            font-size: 24px;
            margin-bottom: 10px;
            color: #fff;
            position: relative;
        }
        
        .article-meta {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #ccc;
            position: relative;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .article-body {
            padding: 40px;
        }
        
        .analysis-text {
            font-size: 18px;
            line-height: 1.8;
            color: #333;
            text-align: justify;
            margin-bottom: 30px;
        }
        
        .category-section {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin: 20px 0;
            opacity: 0;
            animation: slideUp 0.6s ease forwards;
        }
        
        .category-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .category-icon {
            font-size: 24px;
        }
        
        .category-title {
            font-size: 20px;
            font-weight: bold;
        }
        
        .category-content {
            padding: 30px;
        }
        
        .category-text {
            font-size: 16px;
            line-height: 1.7;
            color: #333;
            text-align: justify;
        }
        
        .sources-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #00d4ff;
            margin-top: 30px;
        }
        
        .sources-title {
            font-weight: bold;
            color: #1a1a2e;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .sources-list {
            color: #666;
            font-style: italic;
        }
        
        .summary-stats {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            text-align: center;
            min-width: 120px;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .error {
            background: #fff5f5;
            color: #c53030;
            padding: 30px;
            border-radius: 15px;
            border-left: 5px solid #fc8181;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        @media (max-width: 768px) {
            .search-input { width: 100%; margin-bottom: 15px; }
            .search-box { flex-direction: column; align-items: center; }
            .stock-symbol { font-size: 36px; }
            .article-title { font-size: 20px; }
            .article-body { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <div class="logo">📊 FinanceHub</div>
                <div class="tagline">AI-Powered Market Intelligence</div>
            </div>
        </div>
    </div>
    
    <div class="search-container">
        <h1 class="search-title">Market Analysis Center</h1>
        <p class="search-subtitle">Get comprehensive AI analysis of any stock with real-time data</p>
        
        <div class="search-box">
            <input type="text" id="stock" class="search-input" placeholder="Enter stock symbol (e.g., AAPL, GOOGL)" />
            <button onclick="analyze()" class="search-btn">Analyze Stock</button>
        </div>
        
        <div class="popular-stocks">
            <div class="stock-chip" onclick="quickAnalyze('AAPL')">AAPL</div>
            <div class="stock-chip" onclick="quickAnalyze('GOOGL')">GOOGL</div>
            <div class="stock-chip" onclick="quickAnalyze('TSLA')">TSLA</div>
            <div class="stock-chip" onclick="quickAnalyze('MSFT')">MSFT</div>
            <div class="stock-chip" onclick="quickAnalyze('NVDA')">NVDA</div>
            <div class="stock-chip" onclick="quickAnalyze('AMZN')">AMZN</div>
        </div>
    </div>
    
    <div class="main-content">
        <div id="output"></div>
    </div>

    <script>
        function quickAnalyze(symbol) {
            document.getElementById('stock').value = symbol;
            analyze();
        }
        
        async function analyze() {
            const stock = document.getElementById('stock').value.trim().toUpperCase();
            if (!stock) return;
            
            // Show loading
            document.getElementById('output').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <h3>Analyzing ${stock}...</h3>
                    <p>Gathering data from Yahoo Finance, MarketWatch, and Seeking Alpha</p>
                </div>
            `;
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol: stock})
                });
                const data = await response.json();
                
                if (data.success) {
                    const currentTime = new Date().toLocaleString();
                    
                    // Create main header
                    let html = `
                        <div class="article-container">
                            <div class="article-header">
                                <div class="stock-symbol">${stock}</div>
                                <div class="article-title">Comprehensive Market Analysis</div>
                                <div class="article-meta">
                                    <div class="meta-item">
                                        <span>📅</span>
                                        <span>Updated: ${currentTime}</span>
                                    </div>
                                    <div class="meta-item">
                                        <span>🤖</span>
                                        <span>AI-Categorized Analysis</span>
                                    </div>
                                    <div class="meta-item">
                                        <span>📊</span>
                                        <span>Real-time Data</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Add summary stats
                    if (data.total_articles && data.relevant_articles) {
                        html += `
                            <div class="summary-stats">
                                <div class="stat-item">
                                    <span class="stat-number">${data.total_articles}</span>
                                    <span class="stat-label">Articles Found</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">${data.relevant_articles}</span>
                                    <span class="stat-label">Analyzed</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">${Object.keys(data.categories).length - 1}</span>
                                    <span class="stat-label">Categories</span>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Add category sections
                    const categoryOrder = ['expert_analysis', 'financial_performance', 'company_news', 'market_sentiment', 'risk_assessment'];
                    
                    categoryOrder.forEach((categoryKey, index) => {
                        if (data.categories[categoryKey]) {
                            const category = data.categories[categoryKey];
                            setTimeout(() => {
                                const categoryHtml = `
                                    <div class="category-section">
                                        <div class="category-header">
                                            <div class="category-icon">${category.icon}</div>
                                            <div class="category-title">${category.title}</div>
                                        </div>
                                        <div class="category-content">
                                            <div class="category-text">${category.content}</div>
                                        </div>
                                    </div>
                                `;
                                document.getElementById('output').innerHTML += categoryHtml;
                            }, index * 200); // Stagger animations
                        }
                    });
                    
                    // Add sources section at the end
                    setTimeout(() => {
                        const sourcesHtml = `
                            <div class="sources-section">
                                <div class="sources-title">📰 Data Sources</div>
                                <div class="sources-list">Analysis based on real-time data from: ${data.categories.sources}</div>
                            </div>
                        `;
                        document.getElementById('output').innerHTML += sourcesHtml;
                    }, categoryOrder.length * 200);
                    
                    document.getElementById('output').innerHTML = html;
                } else {
                    document.getElementById('output').innerHTML = `
                        <div class="error">
                            <h3>❌ Analysis Error</h3>
                            <p>${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                document.getElementById('output').innerHTML = `
                    <div class="error">
                        <h3>❌ Connection Error</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        
        // Allow Enter key
        document.getElementById('stock').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyze();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'No symbol provided'})
        
        # Run RAG analysis
        rag = StockRAGSystem()
        result = rag.analyze_stock(symbol)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Stock RAG Server...")
    print("📍 Open: http://127.0.0.1:7777")
    app.run(host='127.0.0.1', port=7777, debug=False, threaded=True)