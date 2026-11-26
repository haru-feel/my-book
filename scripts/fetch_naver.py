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

NOISE_WORDS = (
    "로그인", "회원가입", "고객센터", "이용약관", "개인정보처리방침",
    "검색옵션", "블로그 내 검색", "카페 내 검색", "뉴스검색", "연관검색어",
    "이전 페이지", "다음 페이지", "전체보기", "장바구니", "바로구매", "찜하기"
)


def clean_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    no_tags = re.sub(r"<[^>]+>", " ", raw_html)
    unescaped = html.unescape(no_tags)
    return re.sub(r"\s+", " ", unescaped).strip()


def normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", "", text or "").lower()


def fetch_html(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def extract_toc_from_html(page_html: str) -> list[str]:
    """부크크 상세 페이지 HTML에서 '목차' 항목들을 최대한 추출합니다."""
    candidates: list[str] = []

    # 1) HTML 태그 기반 목차 추출 ('목차' 또는 '차례' 이후 영역)
    toc_block_match = re.search(
        r"(?:목차|차례)[\s\S]{0,4000}",
        page_html,
        re.IGNORECASE
    )
    if toc_block_match:
        block = toc_block_match.group(0)
        # <br>이나 블록 태그를 줄바꿈으로 치환 후 텍스트 라인 분리
        block_with_breaks = re.sub(r"<(?:/?(?:p|div|li|tr|h[1-6])|br\s*/?)[^>]*>", "\n", block, flags=re.I)
        plain_block = html.unescape(re.sub(r"<[^>]+>", " ", block_with_breaks))
        for raw_line in plain_block.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if not line or line in ("목차", "차례"):
                continue
            if any(nw in line for nw in NOISE_WORDS):
                continue
            if 2 <= len(line) <= 90 and line not in candidates:
                candidates.append(line)
            if len(candidates) >= 20:
                break

    # 2) 페이지 내 내장 JSON / 스크립트 데이터에서 목차 관련 필드 탐색
    if not candidates:
        json_toc_matches = re.findall(
            r'["\']?(?:toc|tableOfContents|index|목차)["\']?\s*[:=]\s*["\']([^"\']{10,2000})["\']',
            page_html,
            re.IGNORECASE
        )
        for matched in json_toc_matches:
            decoded = matched.encode("utf-8").decode("unicode_escape", errors="ignore")
            decoded = html.unescape(decoded).replace("\\n", "\n")
            for raw_line in decoded.splitlines():
                line = re.sub(r"\s+", " ", raw_line).strip()
                if 2 <= len(line) <= 90 and line not in ("목차", "차례") and line not in candidates:
                    if not any(nw in line for nw in NOISE_WORDS):
                        candidates.append(line)
                if len(candidates) >= 20:
                    break
            if candidates:
                break

    return candidates


def fetch_bookk_details(bookk_url: str) -> dict:
    """부크크(bookk.co.kr) 상세 페이지에서 공개된 제목, 소개, 표지, 목차 정보를 추출합니다."""
    info = {
        "title": "",
        "summary": "",
        "cover_url": "",
        "toc": []
    }
    try:
        page_html = fetch_html(bookk_url)

        og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)
        og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)
        og_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)

        if og_title:
            t = clean_text(og_title.group(1))
            t = re.sub(r"\s*\|\s*부크크.*$", "", t).strip()
            info["title"] = t

        if og_desc:
            d = clean_text(og_desc.group(1))
            if len(d) > 15:
                info["summary"] = d

        if og_img:
            img_url = html.unescape(og_img.group(1)).strip()
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            info["cover_url"] = img_url

        info["toc"] = extract_toc_from_html(page_html)

    except Exception as e:
        print(f"[WARN] Failed to fetch Bookk page ({bookk_url}): {e}")

    return info


def is_matching_post(title: str, snippet: str, book_title: str, require_book_context: bool = False) -> bool:
    """책 제목과 동일한 단어(공백 무시 기준 포함)가 제목 또는 요약에 들어간 포스팅인지 검사합니다."""
    if not book_title:
        return False

    combined_raw = f"{title} {snippet}"
    if any(nw in combined_raw for nw in NOISE_WORDS):
        return False

    norm_title = normalize_for_match(title)
    norm_snippet = normalize_for_match(snippet)
    norm_combined = f"{norm_title} {norm_snippet}"
    norm_book = normalize_for_match(book_title)

    exact_present = norm_book in norm_combined
    words = [w for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", book_title)]
    word_hits = sum(1 for w in words if normalize_for_match(w) in norm_combined)

    if not exact_present:
        if len(words) >= 2:
            if word_hits < min(2, len(words)):
                return False
        else:
            return False

    if require_book_context:
        context_keywords = ("후기", "리뷰", "서평", "독서", "책", "문장", "추천", "완독", "에세이", "출간")
        if not any(ck in combined_raw for ck in context_keywords):
            return False

    return True


def parse_naver_results(
    page_html: str,
    book_title: str,
    limit: int = 6,
    domain_filter: str | None = None,
    require_book_context: bool = False
) -> list[dict]:
    results: list[dict] = []
    seen_urls: set[str] = set()

    anchor_pattern = re.compile(
        r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL
    )

    for match in anchor_pattern.finditer(page_html):
        href = html.unescape(match.group(1)).strip()
        title = clean_text(match.group(2))

        if not title or len(title) < 4:
            continue
        if href.startswith("https://search.naver.com") or href.startswith("https://help.naver.com"):
            continue
        if domain_filter and domain_filter not in href:
            continue
        if href in seen_urls:
            continue

        start = max(0, match.start() - 250)
        end = min(len(page_html), match.end() + 900)
        context_block = clean_text(page_html[start:end])
        snippet = context_block.replace(title, "", 1).strip()
        if len(snippet) > 200:
            snippet = snippet[:200].rsplit(" ", 1)[0] + "..."

        if not is_matching_post(title, snippet, book_title, require_book_context=require_book_context):
            continue

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


def search_naver_web(
    query: str,
    book_title: str,
    where: str = "nexearch",
    limit: int = 6,
    domain_filter: str | None = None,
    require_book_context: bool = False
) -> list[dict]:
    encoded_q = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where={where}&query={encoded_q}"
    try:
        page_html = fetch_html(url)
        return parse_naver_results(
            page_html,
            book_title=book_title,
            limit=limit,
            domain_filter=domain_filter,
            require_book_context=require_book_context
        )
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
        bookk_info = fetch_bookk_details(seed["bookk_url"])
        time.sleep(random.uniform(0.8, 1.5))

        resolved_title = (seed["query"] or seed["fallback_title"]).strip()

        blog_items = search_naver_web(
            f'"{resolved_title}" 후기 OR 리뷰',
            book_title=resolved_title,
            where="blog",
            limit=6,
            domain_filter="blog.naver.com",
            require_book_context=True
        )
        if not blog_items:
            blog_items = search_naver_web(
                f'"{resolved_title}"',
                book_title=resolved_title,
                where="nexearch",
                limit=6,
                require_book_context=False
            )

        time.sleep(random.uniform(1.0, 2.0))

        news_items = search_naver_web(
            f'"{resolved_title}"',
            book_title=resolved_title,
            where="news",
            limit=5,
            require_book_context=False
        )

        time.sleep(random.uniform(1.0, 2.0))

        reviews = blog_items if blog_items else prev_book.get("reviews", [])
        press = news_items if news_items else prev_book.get("press", [])

        # 부크크 페이지에서 목차가 추출되면 우선 반영하고, 없으면 시드/기존 목차 사용
        resolved_toc = (
            bookk_info["toc"]
            if bookk_info["toc"]
            else (seed["toc"] or prev_book.get("toc", []))
        )

        books_output.append({
            "id": seed["id"],
            "bookk_id": seed["bookk_id"],
            "bookk_url": seed["bookk_url"],
            "title": resolved_title,
            "author": seed["author"],
            "publisher": "부크크(bookk)",
            "pubdate": prev_book.get("pubdate", ""),
            "isbn": prev_book.get("isbn", ""),
            "cover_url": seed["cover_url"] or bookk_info["cover_url"] or prev_book.get("cover_url", ""),
            "summary": bookk_info["summary"] or seed["summary"],
            "toc": resolved_toc,
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
    print("Updated data/books_data.json with custom BOOKS_SEED and Bookk TOC extraction.")
