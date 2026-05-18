#!/usr/bin/env python3
"""
AI HOT Dashboard - Data Fetcher
从多个权威来源实时抓取 AI 资讯
"""

import asyncio
import aiohttp
import feedparser
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import ssl
import certifi

# 禁用SSL验证（某些旧服务器需要）
ssl._create_default_https_context = ssl._create_unverified_context

class AIFeedsFetcher:
    def __init__(self):
        self.results = {
            "models": [],
            "products": [],
            "biz": [],
            "industry": [],
            "paper": [],
            "tips": []
        }

    async def fetch_url(self, session, url, timeout=15):
        """异步获取URL内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                print(f"HTTP {response.status} for {url}")
                return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_date(self, date_str: str) -> str:
        """提取日期字符串"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        if "今天" in date_str or "today" in date_str.lower():
            return "今天"
        elif "昨天" in date_str or "yesterday" in date_str.lower():
            return "昨天"
        elif "小时" in date_str or "hour" in date_str.lower():
            return "今天"
        elif "分钟" in date_str or "min" in date_str.lower():
            return "今天"
        else:
            # 尝试解析日期
            try:
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    return date_str
                elif re.match(r'\d+月\d+日', date_str):
                    month = int(re.search(r'(\d+)月', date_str).group(1))
                    day = int(re.search(r'(\d+)日', date_str).group(1))
                    return f"{month}月{day}日"
            except:
                pass
            return date_str if date_str else "未知"

    async def fetch_aihot_api(self, session):
        """获取 AIHOT API 数据"""
        print("📡 正在获取 AIHOT API 数据...")

        # AI 模型发布
        models_url = "https://aihot.virxact.com/api/public/items?mode=selected&category=ai-models&take=20"
        content = await self.fetch_url(session, models_url)

        if content:
            try:
                data = json.loads(content)
                items = data.get("items", []) or data.get("data", []) if isinstance(data, dict) else data

                for item in items:
                    if len(self.results["models"]) >= 15:
                        break
                    title = item.get("title", "")
                    summary = item.get("summary", "") or item.get("content", "")
                    url = item.get("url", "") or item.get("link", "")
                    source = item.get("source", "AIHOT")
                    created_at = item.get("publishedAt", "") or item.get("created_at", "") or item.get("published", "")

                    self.results["models"].append({
                        "title": title[:200],
                        "summary": summary[:300] if summary else "",
                        "url": url,
                        "source": source,
                        "time": self.extract_date(created_at)
                    })
            except json.JSONDecodeError as e:
                print(f"AIHOT models JSON解析错误: {e}")

        # AI 产品发布
        product_url = "https://aihot.virxact.com/api/public/items?mode=selected&category=ai-products&take=20"
        content = await self.fetch_url(session, product_url)

        if content:
            try:
                data = json.loads(content)
                items = data.get("items", []) or data.get("data", []) if isinstance(data, dict) else data

                for item in items:
                    if len(self.results["products"]) >= 15:
                        break
                    title = item.get("title", "")
                    summary = item.get("summary", "") or item.get("content", "")
                    url = item.get("url", "") or item.get("link", "")
                    source = item.get("source", "AIHOT")
                    created_at = item.get("publishedAt", "") or item.get("created_at", "") or item.get("published", "")

                    self.results["products"].append({
                        "title": title[:200],
                        "summary": summary[:300] if summary else "",
                        "url": url,
                        "source": source,
                        "time": self.extract_date(created_at)
                    })
            except json.JSONDecodeError as e:
                print(f"AIHOT products JSON解析错误: {e}")

        # 行业动态
        industry_url = "https://aihot.virxact.com/api/public/items?mode=selected&category=industry&take=30"
        content = await self.fetch_url(session, industry_url)

        if content:
            try:
                data = json.loads(content)
                items = data.get("items", []) or data.get("data", []) if isinstance(data, dict) else data

                for item in items:
                    title = item.get("title", "")
                    summary = item.get("summary", "") or item.get("content", "")
                    url = item.get("url", "") or item.get("link", "")
                    source = item.get("source", "AIHOT")
                    created_at = item.get("publishedAt", "") or item.get("created_at", "") or item.get("published", "")

                    # 商业化关键词
                    biz_keywords = ["融资", "估值", "IPO", "收购", " revenue", "funding", "valuation",
                                   "acquisition", "商业化", "收入", "盈利", "亿美元", " billion"]
                    # 模型关键词
                    model_keywords = ["模型", "model", "发布", "release", "launch", "GPT", "Claude",
                                     "Gemini", "Llama", "上线"]

                    # 判断类别
                    is_biz = any(kw.lower() in title.lower() + summary.lower() for kw in biz_keywords)
                    is_model = any(kw.lower() in title.lower() for kw in model_keywords)

                    if is_biz and len(self.results["biz"]) < 15:
                        self.results["biz"].append({
                            "title": title[:200],
                            "summary": summary[:300] if summary else "",
                            "url": url,
                            "source": source,
                            "time": self.extract_date(created_at)
                        })
                    elif is_model and len(self.results["models"]) < 15:
                        self.results["models"].append({
                            "title": title[:200],
                            "summary": summary[:300] if summary else "",
                            "url": url,
                            "source": source,
                            "time": self.extract_date(created_at)
                        })
                    elif len(self.results["industry"]) < 15:
                        self.results["industry"].append({
                            "title": title[:200],
                            "summary": summary[:300] if summary else "",
                            "url": url,
                            "source": source,
                            "time": self.extract_date(created_at)
                        })
            except json.JSONDecodeError as e:
                print(f"AIHOT industry JSON解析错误: {e}")

        # 论文研究
        paper_url = "https://aihot.virxact.com/api/public/items?mode=selected&category=paper&take=20"
        content = await self.fetch_url(session, paper_url)

        if content:
            try:
                data = json.loads(content)
                items = data.get("items", []) or data.get("data", []) if isinstance(data, dict) else data

                for item in items:
                    if len(self.results["paper"]) >= 15:
                        break
                    title = item.get("title", "")
                    summary = item.get("summary", "") or item.get("content", "")
                    url = item.get("url", "") or item.get("link", "")
                    source = item.get("source", "AIHOT")
                    created_at = item.get("publishedAt", "") or item.get("created_at", "") or item.get("published", "")

                    self.results["paper"].append({
                        "title": title[:200],
                        "summary": summary[:300] if summary else "",
                        "url": url,
                        "source": source,
                        "time": self.extract_date(created_at)
                    })
            except json.JSONDecodeError as e:
                print(f"AIHOT paper JSON解析错误: {e}")

    async def fetch_product_hunt(self, session):
        """获取 Product Hunt RSS"""
        print("🛍️ 正在获取 Product Hunt RSS...")

        rss_url = "https://www.producthunt.com/feed"

        try:
            async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=20),
                                  headers={'User-Agent': 'Mozilla/5.0'}) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)

                    for entry in feed.entries[:50]:
                        title = entry.get("title", "")
                        summary = entry.get("summary", "") or entry.get("description", "")
                        # 清理HTML标签
                        summary = re.sub(r'<[^>]+>', '', summary)[:300]
                        link = entry.get("link", "")

                        # 分类
                        ai_keywords = ["AI", "artificial intelligence", "machine learning", "LLM",
                                      "GPT", "agent", "automation", "生成", "智能"]
                        is_ai = any(kw.lower() in title.lower() for kw in ai_keywords)

                        if is_ai and len(self.results["products"]) < 30:
                            self.results["products"].append({
                                "title": title[:200],
                                "summary": summary,
                                "url": link,
                                "source": "Product Hunt",
                                "time": "今日"
                            })
        except Exception as e:
            print(f"Product Hunt 获取失败: {e}")

    async def fetch_hackernews(self, session):
        """获取 Hacker News AI 相关内容"""
        print("📰 正在获取 Hacker News...")

        hn_url = "https://hnrss.org/frontpage"

        try:
            async with session.get(hn_url, timeout=aiohttp.ClientTimeout(total=15),
                                  headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)

                    ai_keywords = ["AI", "artificial intelligence", "OpenAI", "GPT", "Claude",
                                  "machine learning", "deep learning", "neural", "LLM", "Anthropic",
                                  "Google", "model", "agent"]

                    for entry in feed.entries[:30]:
                        title = entry.get("title", "")
                        summary = entry.get("summary", "")
                        summary = re.sub(r'<[^>]+>', '', summary)[:300]
                        link = entry.get("link", "")

                        if any(kw.lower() in title.lower() for kw in ai_keywords):
                            if len(self.results["industry"]) < 15:
                                self.results["industry"].append({
                                    "title": title[:200],
                                    "summary": summary,
                                    "url": link,
                                    "source": "Hacker News",
                                    "time": self.extract_date(str(entry.get("published", "")))
                                })
        except Exception as e:
            print(f"Hacker News 获取失败: {e}")

    async def fetch_techcrunch(self, session):
        """获取 TechCrunch AI 新闻"""
        print("📰 正在获取 TechCrunch...")

        tc_url = "https://techcrunch.com/feed/"

        try:
            async with session.get(tc_url, timeout=aiohttp.ClientTimeout(total=15),
                                  headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)

                    ai_keywords = ["AI", "artificial intelligence", "OpenAI", "GPT", "machine learning",
                                  "Anthropic", "startup", "funding", "valuation", "融资", "估值"]

                    for entry in feed.entries[:20]:
                        title = entry.get("title", "")
                        summary = entry.get("summary", "")
                        summary = re.sub(r'<[^>]+>', '', summary)[:300]
                        link = entry.get("link", "")

                        if any(kw.lower() in title.lower() for kw in ai_keywords):
                            if len(self.results["biz"]) < 10:
                                self.results["biz"].append({
                                    "title": title[:200],
                                    "summary": summary,
                                    "url": link,
                                    "source": "TechCrunch",
                                    "time": "今日"
                                })
        except Exception as e:
            print(f"TechCrunch 获取失败: {e}")

    async def fetch_arxiv(self, session):
        """获取arXiv AI论文"""
        print("📄 正在获取arXiv论文...")

        arxiv_url = "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&max_results=10&sortBy=submittedDate&sortOrder=descending"

        try:
            content = await self.fetch_url(session, arxiv_url)
            if content:
                # 简单解析atom feed
                entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)

                for entry in entries[:8]:
                    title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                    summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                    link_match = re.search(r'<id>(.*?)</id>', entry)

                    if title_match:
                        title = title_match.group(1).strip().replace('\n', ' ')
                        summary = summary_match.group(1).strip().replace('\n', ' ')[:300] if summary_match else ""
                        link = link_match.group(1) if link_match else ""

                        self.results["paper"].append({
                            "title": title[:200],
                            "summary": summary,
                            "url": link,
                            "source": "arXiv",
                            "time": "今日"
                        })
        except Exception as e:
            print(f"arXiv 获取失败: {e}")

    async def run(self):
        """运行所有抓取任务"""
        print("🚀 AI HOT 数据抓取开始...")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)

        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                self.fetch_aihot_api(session),
                self.fetch_product_hunt(session),
                self.fetch_hackernews(session),
                self.fetch_techcrunch(session),
                self.fetch_arxiv(session)
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

        print("-" * 50)
        print("📊 抓取结果统计:")
        print(f"   🤖 模型发布: {len(self.results['models'])} 条")
        print(f"   🛍️ 产品发布: {len(self.results['products'])} 条")
        print(f"   💰 AI 商业化: {len(self.results['biz'])} 条")
        print(f"   📈 行业动态: {len(self.results['industry'])} 条")
        print(f"   📄 论文研究: {len(self.results['paper'])} 条")
        print(f"   💡 技巧观点: {len(self.results['tips'])} 条")
        print("✅ 抓取完成!")

        return self.results

def save_results(results: Dict, filepath: str = "data/latest.json"):
    """保存结果到JSON文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 数据已保存到: {filepath}")

async def main():
    fetcher = AIFeedsFetcher()
    results = await fetcher.run()
    save_results(results)
    return results

if __name__ == "__main__":
    asyncio.run(main())
