#!/usr/bin/env python3
"""AI + 网络安全 热点每日抓取 — 蒙多学习引擎 v2

多源融合：
  - aihot.virxact.com (AI 热点聚合)
  - arXiv cs.CR 最新安全论文
  - GitHub Trending (AI/ML + Security 仓库)
  - Hacker News via buzzing.cc (AI/安全过滤)

用法：
    python tools/ai-hotspot-crawler.py
"""

import json
import re
import sys
import io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "docs" / "ai-hotspots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    from scrapling.fetchers import Fetcher
    USE_SCRAPLING = True
except ImportError:
    USE_SCRAPLING = False


def _to_str(page) -> str:
    """统一 str 输出"""
    if page is None:
        return ""
    if isinstance(page, str):
        return page
    if isinstance(page, bytes):
        return page.decode('utf-8', errors='replace')
    body = getattr(page, 'body', None)
    if body is None:
        body = getattr(page, 'text', '') or str(page)
    return _to_str(body)


def _fetch(url, timeout=30):
    """统一抓取"""
    if USE_SCRAPLING:
        try:
            return _to_str(Fetcher.get(url, timeout=timeout))
        except Exception:
            pass
    try:
        import requests as req
        resp = req.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=timeout)
        resp.raise_for_status()
        return resp.text or ""
    except Exception as e:
        print(f"  [fetch err] {url}: {e}")
        return ""


# ─── 抓取器 ───

def crawl_aihot() -> list:
    """抓取 aihot.virxact.com"""
    print(f"  🔥 aihot...", end=' ')
    body = _fetch("https://aihot.virxact.com/")
    if not body:
        print("无响应")
        return []

    items = []
    # 尝试提取所有链接+文字
    # aihot 的 article 标签
    for m in re.finditer(r'<(?:article|div|li)[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>([^<]{8,200})</a>', body, re.DOTALL):
        link, title = m.group(1), m.group(2).strip()
        if title and len(title) >= 8:
            items.append({'title': title[:200], 'link': link, 'source': 'AI热点聚合'})

    # 全局兜底
    if not items:
        for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]{10,200})</a>', body):
            link, title = m.group(1), m.group(2).strip()
            skip_words = ['首页', '关于', '登录', '注册', '隐私', 'Home', 'About', 'Login', 'Skip']
            if not any(w in title for w in skip_words):
                items.append({'title': title[:200], 'link': link, 'source': 'AI热点聚合'})

    # 去重
    seen = set()
    out = []
    for h in items[:40]:
        k = h['title'][:60]
        if k not in seen:
            seen.add(k)
            out.append(h)

    print(f"{len(out)}条")
    return out


def crawl_github_trending() -> list:
    """抓 GitHub Trending 中 AI/Security 相关仓库"""
    print(f"  📦 GitHub Trending...", end=' ')

    ai_kw = ['ai', 'llm', 'ml', 'gpt', 'neural', 'transformer', 'deep', 'model',
             'agent', 'rag', 'vector', 'embedding', 'fine-tune', 'langchain',
             'openai', 'anthropic', 'claude', 'gemini', 'diffusion']
    sec_kw = ['security', 'exploit', 'vuln', 'cve', 'hack', 'pentest', 'fuzz',
              'crypto', 'reverse', 'malware', 'forensic', 'scan', 'redteam',
              'pentest', 'bugbounty', 'osint', 'forensics']

    items = []
    for lang in ['python', 'go']:
        body = _fetch(f"https://github.com/trending/{lang}?since=daily")
        if not body:
            continue

        # 提取仓库
        for m in re.finditer(
            r'<h2[^>]*>\s*<a[^>]+href="(/[^/]+/[^"]+)"[^>]*>\s*([^<]+?)\s*/\s*([^<]+?)</a>',
            body
        ):
            path, owner, repo = m.group(1), m.group(2).strip(), m.group(3).strip()
            full_name = f"{owner}/{repo}"
            combined = full_name.lower()

            tag = None
            if any(k in combined for k in ai_kw):
                tag = 'ai'
            elif any(k in combined for k in sec_kw):
                tag = 'security'
            else:
                continue

            items.append({
                'title': f"[GitHub Trend] {full_name}",
                'link': f"https://github.com{path}",
                'source': f'GitHub Trending ({lang})',
                'tag': tag,
            })

    # 去重
    seen = set()
    out = []
    for h in items[:15]:
        k = h['title'][:80]
        if k not in seen:
            seen.add(k)
            out.append(h)

    ai_n = sum(1 for h in out if h.get('tag') == 'ai')
    sec_n = sum(1 for h in out if h.get('tag') == 'security')
    print(f"{len(out)}个 (AI:{ai_n} 安全:{sec_n})")
    return out


def crawl_arxiv_cr() -> list:
    """抓取 arXiv cs.CR 最新安全论文"""
    print(f"  📄 arXiv cs.CR...", end=' ')

    body = _fetch("https://rss.arxiv.org/rss/cs.CR")
    if not body:
        print("无响应")
        return []

    titles = re.findall(r'<title[^>]*>([^<]+)</title>', body)
    links = re.findall(r'<link[^>]*>(https?://[^<]+)</link>', body)
    descs = re.findall(r'<description[^>]*>([^<]+)</description>', body)

    items = []
    for i, t in enumerate(titles[1:7]):
        link = links[i] if i < len(links) else ''
        desc = descs[i] if i < len(descs) else ''
        if not t or len(t) < 10:
            continue
        items.append({
            'title': f"[arXiv CR] {t.strip()[:180]}",
            'link': link,
            'source': 'arXiv cs.CR',
            'summary': desc.strip()[:200],
            'tag': 'security',
        })

    print(f"{len(items)}篇")
    return items


def crawl_buzzingcc() -> list:
    """抓取 Hacker News via buzzing.cc（过滤 AI+安全）"""
    print(f"  🗞️  Hacker News...", end=' ')

    body = _fetch("https://hn.buzzing.cc/")
    if not body:
        print("无响应")
        return []

    kw = ['ai', 'llm', 'gpt', 'openai', 'claude', 'model', 'agent', 'chatgpt',
          'security', 'hack', 'vuln', 'exploit', 'cve', 'breach', 'ransomware',
          'malware', 'privacy', 'encrypt', '密码', '安全', '漏洞', '模型',
          'deepseek', 'gemini', 'anthropic', 'mcp', 'rag', 'vector']

    items = []
    for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.{15,200})</a>', body):
        link, title = m.group(1), m.group(2).strip()
        title = re.sub(r'<[^>]+>', '', title)
        combined = f"{title} {link}".lower()

        if any(k in combined for k in kw) and len(title) >= 10:
            items.append({
                'title': f"[HN] {title[:180]}",
                'link': link,
                'source': 'Hacker News (buzzing.cc)',
            })

    # 去重
    seen = set()
    out = []
    for h in items[:12]:
        k = h['title'][:70]
        if k not in seen:
            seen.add(k)
            out.append(h)

    print(f"{len(out)}条")
    return out


# ─── 主流程 ───

def main():
    print("=" * 55)
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] AI + 网络安全 热点抓取")
    print("=" * 55)

    all_hotspots = []
    all_hotspots.extend(crawl_aihot())
    all_hotspots.extend(crawl_github_trending())
    all_hotspots.extend(crawl_arxiv_cr())
    all_hotspots.extend(crawl_buzzingcc())

    # 全局去重
    seen = set()
    unique = []
    for h in all_hotspots:
        k = h['title'][:60]
        if k not in seen:
            seen.add(k)
            unique.append(h)

    # 标签分配（无 tag 的自动分类）
    for h in unique:
        if 'tag' not in h:
            t = h['title'].lower()
            if any(k in t for k in ['cve', 'exploit', 'vuln', 'hack', 'malware',
                                     'ransomware', 'breach', '安全', '攻击']):
                h['tag'] = 'security'
            elif any(k in t for k in ['llm', 'gpt', 'model', 'agent', 'transformer',
                                       'ai ', 'openai', 'claude', 'deepseek']):
                h['tag'] = 'ai'
            else:
                h['tag'] = 'tech'

    ai_n = sum(1 for h in unique if h.get('tag') == 'ai')
    sec_n = sum(1 for h in unique if h.get('tag') == 'security')

    print(f"\n{'=' * 55}")
    print(f"去重总计: {len(unique)} 条 (🤖 AI: {ai_n} | 🔒 安全: {sec_n})")

    if not unique:
        print("\n  ⚠ 未抓取到热点")
        return 1

    # 保存 JSON
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "date": today,
        "sources": ["aihot.virxact.com", "arXiv cs.CR", "GitHub Trending", "Hacker News"],
        "count": len(unique),
        "ai_count": ai_n,
        "security_count": sec_n,
        "hotspots": unique,
        "crawled_at": datetime.now().isoformat()
    }

    fpath = OUTPUT_DIR / f"{today}.json"
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存: {fpath}")

    # 更新索引
    index = []
    for f in sorted(OUTPUT_DIR.glob("*.json"), reverse=True)[:30]:
        if f.name == 'index.json':
            continue
        with open(f, 'r', encoding='utf-8') as fp:
            d = json.load(fp)
        index.append({
            "date": d.get("date", f.stem),
            "count": d.get("count", 0),
            "ai_count": d.get("ai_count", 0),
            "security_count": d.get("security_count", 0),
            "file": f.name
        })

    with open(OUTPUT_DIR / "index.json", "w", encoding='utf-8') as f:
        json.dump({"updated_at": datetime.now().isoformat(), "days": index}, f, ensure_ascii=False, indent=2)
    print(f"索引已更新 ({len(index)} 天记录)")

    # 速览输出
    print(f"\n{'=' * 55}")
    print("今日速览 (Top 8 AI + Top 8 安全)")
    print(f"{'=' * 55}")

    ai = [h for h in unique if h.get('tag') == 'ai']
    sec = [h for h in unique if h.get('tag') == 'security']

    if ai:
        print(f"\n🤖 AI 前沿 ({len(ai)}条):")
        for i, h in enumerate(ai[:8], 1):
            print(f"  {i}. {h['title'][:90]}")
    if sec:
        print(f"\n🔒 网络安全 ({len(sec)}条):")
        for i, h in enumerate(sec[:8], 1):
            print(f"  {i}. {h['title'][:90]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
