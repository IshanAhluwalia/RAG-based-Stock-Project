from flask import Flask, render_template_string, request, jsonify
import os
from dotenv import load_dotenv
from rag_system import StockRAGSystem

load_dotenv()

app = Flask(__name__)

# New York Times-style HTML template
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Financial Times - Stock Analysis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Georgia', 'Times New Roman', serif;
            background: #fafafa;
            min-height: 100vh;
            color: #111;
            line-height: 1.4;
        }
        
        .newspaper-header {
            background: #fff;
            border-bottom: 3px solid #000;
            padding: 20px 0;
        }
        
        .header-top {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            margin-bottom: 10px;
        }
        
        .date-section {
            color: #666;
        }
        
        .subscription-info {
            color: #666;
        }
        
        .masthead {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .newspaper-title {
            font-family: 'Old English Text MT', 'Times New Roman', serif;
            font-size: 48px;
            font-weight: normal;
            color: #000;
            text-decoration: none;
            letter-spacing: 2px;
        }
        
        .newspaper-nav {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: center;
            gap: 30px;
            border-top: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
        }
        
        .nav-item {
            color: #000;
            text-decoration: none;
            font-size: 14px;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 5px 0;
        }
        
        .nav-item:hover {
            color: #666;
        }
        
        .search-section {
            background: #f8f8f8;
            border-top: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            padding: 30px 20px;
            text-align: center;
        }
        
        .search-title {
            font-size: 24px;
            color: #000;
            margin-bottom: 5px;
            font-weight: bold;
            font-family: 'Georgia', serif;
        }
        
        .search-subtitle {
            color: #666;
            margin-bottom: 25px;
            font-size: 14px;
            font-style: italic;
        }
        
        .search-box {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .search-input {
            padding: 12px 15px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 0;
            width: 250px;
            outline: none;
            font-family: 'Georgia', serif;
        }
        
        .search-input:focus {
            border-color: #000;
        }
        
        .search-btn {
            padding: 12px 20px;
            font-size: 16px;
            background: #000;
            color: white;
            border: none;
            border-radius: 0;
            cursor: pointer;
            font-family: 'Georgia', serif;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .search-btn:hover {
            background: #333;
        }
        
        .popular-stocks {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .stock-chip {
            background: #fff;
            color: #000;
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 0;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stock-chip:hover {
            background: #000;
            color: white;
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
            background: #fff;
        }
        
        .loading {
            background: #f8f8f8;
            padding: 40px;
            border: 1px solid #ddd;
            text-align: center;
            margin: 20px 0;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #000;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .newspaper-layout {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }
        
        .main-story {
            grid-column: 1 / 3;
            border-bottom: 3px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .main-headline {
            font-size: 36px;
            font-weight: bold;
            line-height: 1.2;
            margin-bottom: 15px;
            color: #000;
            font-family: 'Georgia', serif;
        }
        
        .main-byline {
            font-size: 14px;
            color: #666;
            margin-bottom: 20px;
            font-style: italic;
        }
        
        .article-date {
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .story-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 30px;
            margin: 20px 0;
        }
        
        .story-column {
            border-right: 1px solid #ddd;
            padding-right: 20px;
        }
        
        .story-column:last-child {
            border-right: none;
            padding-right: 0;
        }
        
        .column-header {
            font-size: 18px;
            font-weight: bold;
            color: #000;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #000;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .story-content {
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            text-align: justify;
        }
        
        .sidebar-story {
            background: #f8f8f8;
            border: 1px solid #ddd;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .sidebar-headline {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #000;
        }
        
        .sidebar-content {
            font-size: 13px;
            line-height: 1.5;
            color: #555;
        }
        
        .sources-section {
            background: #f0f0f0;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: 3px solid #000;
            margin-top: 30px;
        }
        
        .sources-title {
            font-weight: bold;
            color: #000;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .sources-list {
            color: #666;
            font-size: 12px;
            font-style: italic;
        }
        
        .stats-bar {
            background: #000;
            color: white;
            padding: 15px;
            margin: 20px 0;
            display: flex;
            justify-content: space-around;
            text-align: center;
        }
        
        .stat-item {
            flex: 1;
        }
        
        .stat-number {
            font-size: 20px;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .newspaper-layout,
            .story-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .main-story {
                grid-column: 1;
            }
            
            .story-column {
                border-right: none;
                padding-right: 0;
                border-bottom: 1px solid #ddd;
                padding-bottom: 20px;
                margin-bottom: 20px;
            }
            
            .story-column:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            
            .main-headline {
                font-size: 28px;
            }
            
            .newspaper-title {
                font-size: 32px;
            }
            
            .newspaper-nav {
                flex-wrap: wrap;
                gap: 15px;
            }
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
    <div class="newspaper-header">
        <div class="header-top">
            <div class="date-section">
                <span id="current-date"></span>
            </div>
            <div class="subscription-info">
                Financial Analysis | AI-Powered Intelligence
            </div>
        </div>
        
        <div class="masthead">
            <h1 class="newspaper-title">The Financial Times</h1>
        </div>
        
        <div class="newspaper-nav">
            <a href="#" class="nav-item">Markets</a>
            <a href="#" class="nav-item">Analysis</a>
            <a href="#" class="nav-item">Technology</a>
            <a href="#" class="nav-item">Opinion</a>
            <a href="#" class="nav-item">World</a>
            <a href="#" class="nav-item">Business</a>
        </div>
    </div>
    
    <div class="search-section">
        <h2 class="search-title">Stock Analysis Center</h2>
        <p class="search-subtitle">Get comprehensive AI analysis of any stock with real-time market data</p>
        
        <div class="search-box">
            <input type="text" id="stock" class="search-input" placeholder="Enter stock symbol" />
            <button onclick="analyze()" class="search-btn">Analyze</button>
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
        // Set current date
        document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
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
                    <p>Gathering financial intelligence from multiple sources</p>
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
                    
                    // Create newspaper-style layout
                    let html = `
                        <div class="main-story">
                            <div class="article-date">${new Date().toLocaleDateString('en-US', {
                                weekday: 'long',
                                year: 'numeric', 
                                month: 'long',
                                day: 'numeric'
                            })}</div>
                            <h1 class="main-headline">${stock} Stock Analysis: ${data.quantitative_data ? data.quantitative_data.company_name : stock}</h1>
                            <div class="main-byline">By Financial AI Analyst | Real-time market data analysis</div>
                        </div>
                    `;
                    
                    // Add quantitative data bar
                    if (data.quantitative_data) {
                        const qData = data.quantitative_data;
                        const changeColor = qData.price_change_1d >= 0 ? '#28a745' : '#dc3545';
                        const marketCapFormatted = typeof qData.market_cap === 'number' ? 
                            (qData.market_cap / 1e9).toFixed(1) + 'B' : qData.market_cap;
                        
                        html += `
                            <div class="stats-bar">
                                <div class="stat-item">
                                    <span class="stat-number" style="color: ${changeColor}">$${qData.current_price}</span>
                                    <span class="stat-label">Current Price</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number" style="color: ${changeColor}">${qData.price_change_1d > 0 ? '+' : ''}${qData.price_change_1d}%</span>
                                    <span class="stat-label">1-Day Change</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">${qData.volatility}%</span>
                                    <span class="stat-label">Volatility (Annual)</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">${marketCapFormatted}</span>
                                    <span class="stat-label">Market Cap</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">${qData.pe_ratio !== 'N/A' ? qData.pe_ratio.toFixed(1) : 'N/A'}</span>
                                    <span class="stat-label">P/E Ratio</span>
                                </div>
                            </div>
                        `;
                        
                        // Add detailed metrics section
                        html += `
                            <div style="background: #f8f8f8; padding: 20px; margin: 20px 0; border: 1px solid #ddd;">
                                <h3 style="margin-bottom: 15px; text-align: center; font-size: 18px;">Key Financial Metrics</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                    <div style="text-align: center;">
                                        <div style="font-size: 16px; font-weight: bold;">52-Week Range</div>
                                        <div style="color: #666;">$${qData.week_52_low} - $${qData.week_52_high}</div>
                                        <div style="font-size: 12px; color: ${qData.pct_from_high < -10 ? '#28a745' : '#666'};">
                                            ${qData.pct_from_high}% from high
                                        </div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 16px; font-weight: bold;">Beta</div>
                                        <div style="color: #666;">${qData.beta !== 'N/A' ? qData.beta.toFixed(2) : 'N/A'}</div>
                                        <div style="font-size: 12px; color: #999;">Market volatility</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 16px; font-weight: bold;">Dividend Yield</div>
                                        <div style="color: #666;">${qData.dividend_yield.toFixed(2)}%</div>
                                        <div style="font-size: 12px; color: #999;">Annual dividend</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 16px; font-weight: bold;">EPS</div>
                                        <div style="color: #666;">${qData.eps !== 'N/A' ? '$' + qData.eps.toFixed(2) : 'N/A'}</div>
                                        <div style="font-size: 12px; color: #999;">Earnings per share</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 16px; font-weight: bold;">Avg Volume</div>
                                        <div style="color: #666;">${(qData.volume_avg / 1e6).toFixed(1)}M</div>
                                        <div style="font-size: 12px; color: #999;">Daily trading volume</div>
                                    </div>
                                </div>
                                ${qData.sector !== 'N/A' ? `
                                    <div style="text-align: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                                        <strong>Sector:</strong> ${qData.sector} | <strong>Industry:</strong> ${qData.industry}
                                    </div>
                                ` : ''}
                            </div>
                        `;
                    } else {
                        // Fallback stats bar for news-only analysis
                        if (data.total_articles && data.relevant_articles) {
                            html += `
                                <div class="stats-bar">
                                    <div class="stat-item">
                                        <span class="stat-number">${data.total_articles}</span>
                                        <span class="stat-label">Sources Analyzed</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-number">${data.relevant_articles}</span>
                                        <span class="stat-label">Key Articles</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-number">${Object.keys(data.categories).length - 1}</span>
                                        <span class="stat-label">Analysis Sections</span>
                                    </div>
                                </div>
                            `;
                        }
                    }
                    
                    // Create three-column newspaper layout
                    html += '<div class="story-grid">';
                    
                    const categoryData = [
                        {key: 'expert_analysis', title: 'Expert Analysis', position: 'left'},
                        {key: 'financial_performance', title: 'Financial Performance', position: 'center'},
                        {key: 'company_news', title: 'Company News', position: 'right'}
                    ];
                    
                    categoryData.forEach((cat, index) => {
                        if (data.categories[cat.key]) {
                            const category = data.categories[cat.key];
                            html += `
                                <div class="story-column">
                                    <div class="column-header">${category.title}</div>
                                    <div class="story-content">${category.content}</div>
                                </div>
                            `;
                        }
                    });
                    
                    html += '</div>'; // Close story-grid
                    
                    // Add sidebar stories for remaining categories
                    const sidebarCategories = ['market_sentiment', 'risk_assessment'];
                    sidebarCategories.forEach(categoryKey => {
                        if (data.categories[categoryKey]) {
                            const category = data.categories[categoryKey];
                            html += `
                                <div class="sidebar-story">
                                    <div class="sidebar-headline">${category.title}</div>
                                    <div class="sidebar-content">${category.content}</div>
                                </div>
                            `;
                        }
                    });
                    
                    // Add sources section
                    html += `
                        <div class="sources-section">
                            <div class="sources-title">Sources</div>
                            <div class="sources-list">Analysis compiled from: ${data.categories.sources}</div>
                        </div>
                    `;
                    
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