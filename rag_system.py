import os
import requests
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from typing import List, Dict
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

class StockRAGSystem:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def scrape_yahoo_finance(self, stock_symbol: str) -> List[Dict]:
        """Scrape Yahoo Finance for stock news"""
        articles = []
        try:
            time.sleep(2)
            
            # Try multiple Yahoo Finance URLs for better content
            urls = [
                f"https://finance.yahoo.com/quote/{stock_symbol}/news",
                f"https://finance.yahoo.com/quote/{stock_symbol}/",
                f"https://finance.yahoo.com/news/{stock_symbol.lower()}"
            ]
            
            session = requests.Session()
            session.headers.update(self.headers)
            
            for url in urls:
                try:
                    response = session.get(url, timeout=15)
                    print(f"Yahoo Finance {url}: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for news articles with different selectors
                        selectors = [
                            '[data-testid="story-title"] a',
                            'h3[class*="title"] a',
                            'a[data-testid="story-title"]',
                            'a[class*="storylink"]',
                            'h3 a[href*="/news/"]',
                            'div[class*="news"] h3 a',
                            'li[class*="news"] a'
                        ]
                        
                        for selector in selectors:
                            links = soup.select(selector)
                            for link in links[:3]:  # Limit to 3 per selector
                                try:
                                    title = link.get_text().strip()
                                    href = link.get('href', '')
                                    
                                    if len(title) > 20 and href:
                                        # Construct full URL
                                        article_url = href if href.startswith('http') else f"https://finance.yahoo.com{href}"
                                        
                                        # Get article content
                                        content = self._get_article_content(article_url, session)
                                        
                                        articles.append({
                                            'title': title,
                                            'content': content or title,
                                            'url': article_url,
                                            'source': 'Yahoo Finance',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                except Exception:
                                    continue
                        
                        # Also look for any text content mentioning the stock
                        text_content = soup.get_text()
                        if stock_symbol in text_content:
                            # Extract relevant paragraphs
                            paragraphs = soup.find_all('p')
                            for p in paragraphs:
                                text = p.get_text().strip()
                                if len(text) > 50 and stock_symbol in text:
                                    articles.append({
                                        'title': f'{stock_symbol} Market Information',
                                        'content': text[:300],
                                        'url': url,
                                        'source': 'Yahoo Finance',
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    break
                        
                        if articles:
                            break  # Found articles, no need to try other URLs
                            
                except Exception as e:
                    print(f"Error with URL {url}: {e}")
                    continue
                        
        except Exception as e:
            print(f"Error scraping Yahoo Finance: {e}")
            
        return articles
    
    def _get_article_content(self, url: str, session: requests.Session) -> str:
        """Extract content from article URL"""
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    element.decompose()
                
                # Look for article content with common selectors
                content_selectors = [
                    'div[class*="content"] p',
                    'div[class*="body"] p',
                    'article p',
                    'div[class*="text"] p',
                    '.content p',
                    '.article-body p'
                ]
                
                content = ""
                for selector in content_selectors:
                    paragraphs = soup.select(selector)
                    if paragraphs:
                        content = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
                        break
                
                # Fallback to any paragraphs
                if not content:
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
                
                return content[:500] if content else None
                
        except Exception:
            return None
    
    def scrape_marketwatch(self, stock_symbol: str) -> List[Dict]:
        """Scrape MarketWatch for stock news"""
        articles = []
        try:
            time.sleep(2)
            
            # Try multiple MarketWatch URLs
            urls = [
                f"https://www.marketwatch.com/investing/stock/{stock_symbol.lower()}",
                f"https://www.marketwatch.com/tools/screener/stock?Symbol={stock_symbol}",
                f"https://www.marketwatch.com/search?q={stock_symbol}"
            ]
            
            session = requests.Session()
            session.headers.update(self.headers)
            
            for url in urls:
                try:
                    response = session.get(url, timeout=15)
                    print(f"MarketWatch {url}: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for news articles with various selectors
                        selectors = [
                            'h3.article__headline a',
                            'h2.article__headline a', 
                            'a[class*="headline"]',
                            'div[class*="article"] h3 a',
                            'div[class*="news"] a',
                            'a[href*="/story/"]',
                            'h3 a[href*="marketwatch.com"]'
                        ]
                        
                        for selector in selectors:
                            links = soup.select(selector)
                            for link in links[:3]:
                                try:
                                    title = link.get_text().strip()
                                    href = link.get('href', '')
                                    
                                    if len(title) > 25 and href:
                                        article_url = href if href.startswith('http') else f"https://www.marketwatch.com{href}"
                                        
                                        # Get article content
                                        content = self._get_article_content(article_url, session)
                                        
                                        articles.append({
                                            'title': title,
                                            'content': content or title,
                                            'url': article_url,
                                            'source': 'MarketWatch',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                except Exception:
                                    continue
                        
                        # Look for any relevant text content about the stock
                        text_content = soup.get_text()
                        if stock_symbol in text_content:
                            # Find sections that mention the stock
                            for section in soup.find_all(['div', 'section', 'article']):
                                section_text = section.get_text()
                                if stock_symbol in section_text and len(section_text) > 100:
                                    # Extract meaningful paragraphs
                                    paragraphs = section.find_all('p')
                                    for p in paragraphs:
                                        text = p.get_text().strip()
                                        if len(text) > 50 and stock_symbol in text:
                                            articles.append({
                                                'title': f'{stock_symbol} MarketWatch Analysis',
                                                'content': text[:400],
                                                'url': url,
                                                'source': 'MarketWatch',
                                                'timestamp': datetime.now().isoformat()
                                            })
                                            break
                                    break
                        
                        if articles:
                            break
                            
                except Exception as e:
                    print(f"Error with MarketWatch URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping MarketWatch: {e}")
            
        return articles
    
    def scrape_seeking_alpha(self, stock_symbol: str) -> List[Dict]:
        """Scrape Seeking Alpha for stock analysis"""
        articles = []
        try:
            time.sleep(3)  # Seeking Alpha might be more strict
            
            # Try multiple Seeking Alpha URLs
            urls = [
                f"https://seekingalpha.com/symbol/{stock_symbol}/analysis",
                f"https://seekingalpha.com/symbol/{stock_symbol}/news",
                f"https://seekingalpha.com/symbol/{stock_symbol}",
                f"https://seekingalpha.com/search?q={stock_symbol}"
            ]
            
            session = requests.Session()
            # Use more realistic headers for Seeking Alpha
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            for url in urls:
                try:
                    response = session.get(url, timeout=15)
                    print(f"Seeking Alpha {url}: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for articles with various selectors
                        selectors = [
                            'a[data-test-id*="post-list"]',
                            'article h2 a',
                            'h3 a[href*="/article/"]',
                            'div[class*="article"] a',
                            'a[href*="/news/"]',
                            'h2 a[href*="seekingalpha.com"]',
                            'div[class*="title"] a'
                        ]
                        
                        for selector in selectors:
                            links = soup.select(selector)
                            for link in links[:3]:
                                try:
                                    title = link.get_text().strip()
                                    href = link.get('href', '')
                                    
                                    if len(title) > 20 and href:
                                        article_url = href if href.startswith('http') else f"https://seekingalpha.com{href}"
                                        
                                        # Get article content
                                        content = self._get_article_content(article_url, session)
                                        
                                        articles.append({
                                            'title': title,
                                            'content': content or title,
                                            'url': article_url,
                                            'source': 'Seeking Alpha',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                except Exception:
                                    continue
                        
                        # Look for stock analysis content in the page
                        text_content = soup.get_text()
                        if stock_symbol in text_content:
                            # Look for analysis sections
                            for section in soup.find_all(['div', 'section', 'article']):
                                section_text = section.get_text()
                                if stock_symbol in section_text and any(word in section_text.lower() for word in ['analysis', 'outlook', 'investment', 'recommendation']):
                                    # Extract meaningful content
                                    paragraphs = section.find_all('p')
                                    for p in paragraphs:
                                        text = p.get_text().strip()
                                        if len(text) > 80 and stock_symbol in text:
                                            articles.append({
                                                'title': f'{stock_symbol} Investment Analysis - Seeking Alpha',
                                                'content': text[:400],
                                                'url': url,
                                                'source': 'Seeking Alpha',
                                                'timestamp': datetime.now().isoformat()
                                            })
                                            break
                                    break
                        
                        if articles:
                            break
                            
                except Exception as e:
                    print(f"Error with Seeking Alpha URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Seeking Alpha: {e}")
            
        return articles
    
    def _extract_article_content(self, url: str, source: str) -> str:
        """Extract content from article URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                    element.decompose()
                
                # Extract paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs[:3]])  # First 3 paragraphs
                
                return content[:500] if content else None  # Limit content length
                
        except Exception:
            return None
    
    def get_stock_news(self, stock_symbol: str) -> List[Dict]:
        """Retrieve news from all financial sources"""
        all_articles = []
        
        print(f"Scraping news for {stock_symbol}...")
        
        # Scrape from all sources
        yahoo_articles = self.scrape_yahoo_finance(stock_symbol)
        time.sleep(1)  # Be respectful to servers
        
        marketwatch_articles = self.scrape_marketwatch(stock_symbol)
        time.sleep(1)
        
        seeking_alpha_articles = self.scrape_seeking_alpha(stock_symbol)
        
        # Combine all articles
        all_articles.extend(yahoo_articles)
        all_articles.extend(marketwatch_articles)
        all_articles.extend(seeking_alpha_articles)
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicate_articles(all_articles)
        
        print(f"Found {len(unique_articles)} unique articles")
        return unique_articles
    
    def _remove_duplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Create a normalized version of the title for comparison
            normalized_title = re.sub(r'[^a-zA-Z0-9\s]', '', article['title'].lower())
            title_words = set(normalized_title.split())
            # Check if this title is too similar to any we've seen
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                if len(title_words.intersection(seen_words)) / len(title_words.union(seen_words)) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    def build_vector_index(self, documents: List[Dict]):
        """Build FAISS vector index from documents"""
        self.documents = documents
        
        if not documents:
            return
            
        # Extract text content for embedding
        texts = [f"{doc['title']} {doc['content']}" for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
    
    def retrieve_relevant_docs(self, query: str, k: int = 8) -> List[Dict]:
        """Retrieve most relevant documents for a query"""
        if not self.index or not self.documents:
            return []
            
        # Encode query
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return relevant documents
        relevant_docs = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['relevance_score'] = float(scores[0][i])
                relevant_docs.append(doc)
        
        return relevant_docs
    
    def categorize_documents(self, documents: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize documents into different sections based on content analysis"""
        categories = {
            'expert_analysis': [],
            'company_news': [],
            'financial_performance': [],
            'market_sentiment': [],
            'risk_assessment': []
        }
        
        for doc in documents:
            content_lower = f"{doc['title']} {doc['content']}".lower()
            
            # Keywords for each category
            expert_keywords = ['analysis', 'recommendation', 'outlook', 'investment', 'target price', 'rating', 'upgrade', 'downgrade', 'analyst', 'forecast']
            news_keywords = ['announced', 'launch', 'partnership', 'acquisition', 'merger', 'ceo', 'executive', 'product', 'service', 'expansion']
            financial_keywords = ['earnings', 'revenue', 'profit', 'loss', 'eps', 'quarterly', 'financial results', 'sales', 'income', 'margin']
            sentiment_keywords = ['bullish', 'bearish', 'optimistic', 'pessimistic', 'confidence', 'sentiment', 'mood', 'outlook', 'expectations']
            risk_keywords = ['risk', 'concern', 'challenge', 'threat', 'volatility', 'uncertainty', 'decline', 'drop', 'fall', 'warning']
            
            # Score each category
            scores = {
                'expert_analysis': sum(1 for keyword in expert_keywords if keyword in content_lower),
                'company_news': sum(1 for keyword in news_keywords if keyword in content_lower),
                'financial_performance': sum(1 for keyword in financial_keywords if keyword in content_lower),
                'market_sentiment': sum(1 for keyword in sentiment_keywords if keyword in content_lower),
                'risk_assessment': sum(1 for keyword in risk_keywords if keyword in content_lower)
            }
            
            # Assign to category with highest score, or default to company_news
            best_category = max(scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                categories[best_category[0]].append(doc)
            else:
                categories['company_news'].append(doc)  # Default category
        
        return categories

    def generate_categorized_analysis(self, stock_symbol: str, categorized_docs: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Generate analysis for each category"""
        analyses = {}
        sources_used = set()
        
        # Collect all sources used
        for category_docs in categorized_docs.values():
            for doc in category_docs:
                sources_used.add(doc['source'])
        
        sources_list = ", ".join(sources_used)
        
        # Category configurations
        category_configs = {
            'expert_analysis': {
                'title': 'Expert Analysis & Outlook',
                'prompt': f"Based on analyst reports and expert opinions about {stock_symbol}, provide a comprehensive expert analysis focusing on professional recommendations, target prices, ratings, and investment outlook. Include specific analyst views and price targets where mentioned.",
                'icon': '🎯'
            },
            'company_news': {
                'title': 'Latest Company News',
                'prompt': f"Based on recent company news about {stock_symbol}, summarize the most important developments, announcements, partnerships, and corporate actions. Focus on how these developments might impact the company's future.",
                'icon': '📰'
            },
            'financial_performance': {
                'title': 'Financial Performance',
                'prompt': f"Based on financial data and earnings reports for {stock_symbol}, analyze the company's financial performance including revenue, earnings, profitability metrics, and financial health indicators.",
                'icon': '📊'
            },
            'market_sentiment': {
                'title': 'Market Sentiment',
                'prompt': f"Based on market commentary about {stock_symbol}, analyze the overall market sentiment, investor confidence, and market expectations. Include any mentions of bullish/bearish sentiment.",
                'icon': '📈'
            },
            'risk_assessment': {
                'title': 'Risk Assessment',
                'prompt': f"Based on risk-related information about {stock_symbol}, identify and analyze potential risks, challenges, concerns, and threats facing the company. Include both short-term and long-term risk factors.",
                'icon': '⚠️'
            }
        }
        
        for category, docs in categorized_docs.items():
            if not docs:
                continue
                
            # Prepare context from relevant documents
            context = ""
            for doc in docs:
                context += f"Source: {doc['source']}\nHeadline: {doc['title']}\nContent: {doc['content']}\n\n"
            
            config = category_configs[category]
            prompt = f"""
            {config['prompt']}
            
            Recent Information:
            {context}
            
            Write a focused analysis (150-200 words) that synthesizes the information for this specific category. Include specific data points, quotes, and insights from the sources. Reference the sources naturally within the text.
            
            Analysis:
            """
            
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a professional financial analyst providing objective analysis based on recent news from reputable financial sources. Focus on the specific category: {config['title']}."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=250,
                    temperature=0.6
                )
                
                analysis = response.choices[0].message.content.strip()
                analyses[category] = {
                    'title': config['title'],
                    'icon': config['icon'],
                    'content': analysis
                }
                
            except Exception as e:
                analyses[category] = {
                    'title': config['title'],
                    'icon': config['icon'],
                    'content': f"Error generating analysis for this category: {str(e)}"
                }
        
        analyses['sources'] = sources_list
        return analyses
    
    def analyze_stock(self, stock_symbol: str) -> Dict:
        """Main method to analyze a stock symbol with categorized analysis"""
        # Step 1: Retrieve news from financial sources
        news_articles = self.get_stock_news(stock_symbol)
        
        if not news_articles:
            return {
                'success': False, 
                'error': f"No recent financial news found for {stock_symbol} from major financial sources. Please check the stock symbol and try again."
            }
        
        # Step 2: Build vector index
        self.build_vector_index(news_articles)
        
        # Step 3: Retrieve relevant documents
        query = f"{stock_symbol} stock financial analysis market performance earnings revenue"
        relevant_docs = self.retrieve_relevant_docs(query, k=min(len(news_articles), 12))
        
        # Step 4: Categorize documents
        categorized_docs = self.categorize_documents(relevant_docs)
        
        # Step 5: Generate categorized analysis
        categorized_analysis = self.generate_categorized_analysis(stock_symbol, categorized_docs)
        
        return {
            'success': True,
            'categories': categorized_analysis,
            'total_articles': len(news_articles),
            'relevant_articles': len(relevant_docs)
        }