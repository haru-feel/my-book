import html
import json
import os
import random
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BOOKS_SEED = [
    {
        "id": "book-1",
        "bookk_id": "6b0590cade1ad179312a4036",
        "bookk_url": "https://bookk.co.kr/bookStore/6b0590cade1ad179312a4036",
        "query": "말이 줄어든 자리에 남는 것들",
        "fallback_title": "말이 줄어든 자리에 남는 것들",
        "author": "김현승",
        "cover_url": "",
        "summary": "말의 여백과 무게가 담긴 도서입니다. 상세 페이지에서 전체 소개와 구매 정보를 확인하실 수 있습니다.",
        "toc": ["프롤로그 · 멈춤의 자리", "1장 · 조용히 쌓이는 시간", "2장 · 말의 온도와 무게", "에필로그 · 다시 걷는 걸음"],
        "excerpts": [
            "말이 줄어든 자리에 비로소 들리기 시작하는 것들이 있다.",
            "바쁘게 지나쳐 온 계절 끝에서, 나는 나에게 가장 늦게 말을 건넸다."
        ]
    },
    {
        "id": "book-2",
        "bookk_id": "67b32cdd74f2ff3eee47f6b1",
        "bookk_url": "https://bookk.co.kr/bookStore/67b32cdd74f2ff3eee47f6b1",
        "query": "멈춰서 돌아본다",
        "fallback_title": "멈춰서 돌아본다",
        "author": "김현승",
        "cover_url": "",
        "summary": "일상의 결을 멈춰서 세밀하게 들여다보는 도서입니다.",
        "toc": ["여는 글", "1부 · 스쳐 가는 풍경들", "2부 · 남겨진 문장들", "닫는 글"],
        "excerpts": [
            "완벽한 답보다 다정한 질문 하나가 하루를 버티게 할 때가 있다."
        ]
    },
    {
        "id": "book-3",
        "bookk_id": "646abe734222b24502d39197",
        "bookk_url": "https://bookk.co.kr/bookStore/646abe734222b24502d39197",
        "query": "하루가 행복할 수 있다면",
        "fallback_title": "하루가 행복할 수 있다면",
        "author": "김현승",
        "cover_url": "",
       "summary": "하루가 지나면 아는게 많아질 줄 알았는데, 하루가 지나면서 알고 싶은게 많아진다. 나이가 들면 모든게 이해될 줄 알았는데 나이가 들면서 이해해야 할 것들이 많아진다. 시간이 지나면 자연스레 바뀔 줄 알았는데...",
        "toc": ["시작하며", "첫 번째 기록", "두 번째 기록", "마치며"],
        "excerpts": [
            "조용한 기록은 시간이 흐를수록 선명한 지도가 된다."
        ]
    }
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "Referer": "https://www.naver.com/"
}


def clean_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    no_tags = re.sub(r"<[^>]+>", " ", raw_html)
    unescaped = html.unescape(no_tags)
    return re.sub(r"\s+", " ", unescaped).strip()


def fetch_html(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def parse_naver_results(page_html: str, limit: int = 6, domain_filter: str | None = None) -> list[dict]:
    """네이버 검색 HTML에서 외부 링크와 제목·요약 스니펫을 추출합니다."""
    results: list[dict] = []
    seen_urls: set[str] = set()

    # 일반 검색 결과 카드 내 링크 및 주변 텍스트 추출
    anchor_pattern = re.compile(
        r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL
    )

    for match in anchor_pattern.finditer(page_html):
        href = html.unescape(match.group(1)).strip()
        title = clean_text(match.group(2))

        if not title or len(title) < 4:
            continue
        if "naver.com" in href or "search.naver.com" in href:
            continue
        if domain_filter and domain_filter not in href:
            continue
        if href in seen_urls:
            continue

        # 링크 주변 800자 범위에서 요약 문구 추정
        start = max(0, match.start() - 200)
        end = min(len(page_html), match.end() + 800)
        context_block = clean_text(page_html[start:end])
        snippet = context_block.replace(title, "", 1).strip()
        if len(snippet) > 180:
            snippet = snippet[:180].rsplit(" ", 1)[0] + "..."

        seen_urls.add(href)
        results.append({
            "title": title,
            "snippet": snippet or "네이버 검색 결과에서 확인된 항목입니다.",
            "blogger": "네이버 블로그" if domain_filter == "blog.naver.com" else "네이버 검색",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "link": href
        })

        if len(results) >= limit:
            break

    return results


def search_naver_web(query: str, where: str = "nexearch", limit: int = 6, domain_filter: str | None = None) -> list[dict]:
    encoded_q = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where={where}&query={encoded_q}"
    try:
        page_html = fetch_html(url)
        return parse_naver_results(page_html, limit=limit, domain_filter=domain_filter)
    except Exception as e:
        print(f"[WARN] Failed to fetch Naver search ({query}, {where}): {e}")
        return []


def build_dataset() -> dict:
    os.makedirs("data", exist_ok=True)
    output_path = "data/books_data.json"
    existing_map: dict[str, dict] = {}

    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                prev = json.load(f)
                for b in prev.get("books", []):
                    if b.get("id"):
                        existing_map[b["id"]] = b
        except Exception as e:
            print(f"[WARN] Could not read existing {output_path}: {e}")

    books_output = []

    for seed in BOOKS_SEED:
        prev_book = existing_map.get(seed["id"], {})
        search_q = seed["query"] if "제목을 입력하세요" not in seed["query"] else seed["fallback_title"]

        # 1) 블로그 리뷰 수집
        blog_items = search_naver_web(
            f'"{search_q}" 후기 OR 리뷰',
            where="blog",
            limit=6,
            domain_filter="blog.naver.com"
        )
        if not blog_items:
            blog_items = search_naver_web(f'"{search_q}" 리뷰', where="nexearch", limit=6)

        time.sleep(random.uniform(1.0, 2.0))

        # 2) 언론 보도 수집
        news_items = search_naver_web(f'"{search_q}"', where="news", limit=5)

        time.sleep(random.uniform(1.0, 2.0))

        # 수집 실패 시 기존 저장된 항목 유지
        reviews = blog_items if blog_items else prev_book.get("reviews", [])
        press = news_items if news_items else prev_book.get("press", [])

        books_output.append({
            "id": seed["id"],
            "bookk_id": seed["bookk_id"],
            "bookk_url": seed["bookk_url"],
            "title": prev_book.get("title") if "제목 수정 필요" in seed["fallback_title"] and prev_book.get("title") and "제목 반영 예정" not in prev_book.get("title") else (search_q if "제목을 입력하세요" not in seed["query"] else seed["fallback_title"]),
            "author": seed["author"],
            "publisher": "부크크(bookk)",
            "pubdate": prev_book.get("pubdate", ""),
            "isbn": prev_book.get("isbn", ""),
            "cover_url": seed["cover_url"] or prev_book.get("cover_url", ""),
            "summary": seed["summary"],
            "toc": seed["toc"],
            "excerpts": seed["excerpts"],
            "reviews": reviews,
            "press": press
        })

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "books": books_output
    }


if __name__ == "__main__":
    dataset = build_dataset()
    with open("data/books_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print("Updated data/books_data.json without Naver API keys.")
