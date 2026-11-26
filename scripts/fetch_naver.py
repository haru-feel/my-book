import html
import json
import os
import re
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
        "summary": "여백과 사유가 담긴 첫 번째 도서입니다. 부크크 상세 페이지에서 전체 소개와 구매 정보를 확인하실 수 있습니다.",
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
        "summary": "일상의 결을 세밀하게 들여다보는 두 번째 도서입니다.",
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
        "summary": "깊은 호흡으로 읽어 내려가는 세 번째 도서입니다.",
        "toc": ["시작하며", "첫 번째 기록", "두 번째 기록", "마치며"],
        "excerpts": [
            "조용한 기록은 시간이 흐를수록 선명한 지도가 된다."
        ]
    }
]


def clean_html(raw_text: str) -> str:
    if not raw_text:
        return ""
    no_tags = re.sub(r"<[^>]+>", "", raw_text)
    return html.unescape(no_tags).strip()


def naver_search(endpoint: str, query: str, display: int = 6, sort: str = "sim") -> dict:
    client_id = os.environ.get("NAVER_CLIENT_ID", "").strip()
    client_secret = os.environ.get("NAVER_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return {"items": []}

    params = urllib.parse.urlencode({
        "query": query,
        "display": display,
        "sort": sort
    })
    url = f"https://openapi.naver.com/v1/search/{endpoint}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARN] Naver API error ({endpoint}, {query}): {e}")
        return {"items": []}


def build_dataset() -> dict:
    os.makedirs("data", exist_ok=True)
    existing_map = {}
    output_path = "data/books_data.json"

    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                prev = json.load(f)
                for b in prev.get("books", []):
                    existing_map[b.get("id")] = b
        except Exception:
            pass

    books_output = []

    for seed in BOOKS_SEED:
        prev_book = existing_map.get(seed["id"], {})
        search_q = seed["query"] if "말이 줄어든 자리에 남는 것들" not in seed["query"] else seed["fallback_title"]
        search_q = seed["query"] if "멈춰서 돌아본다" not in seed["query"] else seed["fallback_title"]
        search_q = seed["query"] if "하루가 행복할 수 있다면" not in seed["query"] else seed["fallback_title"]

        book_api = naver_search("book.json", search_q, display=3, sort="sim")
        blog_api = naver_search("blog.json", f'"{search_q}" 후기 OR 리뷰', display=8, sort="date")
        news_api = naver_search("news.json", f'"{search_q}"', display=6, sort="date")

        title = seed["fallback_title"]
        publisher = "부크크(bookk)"
        pubdate = ""
        isbn = ""
        cover_url = seed["cover_url"]
        description = seed["summary"]

        if book_api.get("items"):
            top_book = book_api["items"][0]
            api_title = clean_html(top_book.get("title", ""))
            if api_title:
                title = api_title
            publisher = clean_html(top_book.get("publisher", "")) or publisher
            pubdate = top_book.get("pubdate", "")
            isbn = top_book.get("isbn", "")
            cover_url = top_book.get("image") or cover_url
            api_desc = clean_html(top_book.get("description", ""))
            if api_desc:
                description = api_desc

        reviews = []
        for item in blog_api.get("items", []):
            reviews.append({
                "title": clean_html(item.get("title", "")),
                "snippet": clean_html(item.get("description", "")),
                "blogger": clean_html(item.get("bloggername", "네이버 블로그")),
                "date": item.get("postdate", ""),
                "link": item.get("link", "")
            })

        press = []
        for item in news_api.get("items", []):
            press.append({
                "title": clean_html(item.get("title", "")),
                "snippet": clean_html(item.get("description", "")),
                "date": item.get("pubDate", ""),
                "link": item.get("originallink") or item.get("link", "")
            })

        # API 결과가 비어 있을 때 기존 데이터 보존
        if not reviews and prev_book.get("reviews"):
            reviews = prev_book["reviews"]
        if not press and prev_book.get("press"):
            press = prev_book["press"]

        books_output.append({
            "id": seed["id"],
            "bookk_id": seed["bookk_id"],
            "bookk_url": seed["bookk_url"],
            "title": title,
            "author": seed["author"],
            "publisher": publisher,
            "pubdate": pubdate,
            "isbn": isbn,
            "cover_url": cover_url,
            "summary": description,
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
    result = build_dataset()
    with open("data/books_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Saved data/books_data.json successfully.")
