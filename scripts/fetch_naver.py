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
        "required_phrases": ["말이 줄어든 자리에 남는 것들", "말이줄어든자리에남는것들"],
        "require_author_or_book": False,
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
        "required_phrases": ["멈춰서 돌아본다", "멈춰서돌아본다"],
        "require_author_or_book": True,
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
        "required_phrases": ["하루가 행복할 수 있다면", "하루가행복할수있다면"],
        "require_author_or_book": True,
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

BLOCKED_DOMAINS = (
    "naver.com/search",
    "search.naver.com",
    "help.naver.com",
    "keep.naver.com",
    "nid.naver.com",
    "m.naver.com/shorts",
    "clip.naver.com"
)

BLOCKED_TITLES = (
    "새 창 열림",
    "keep에 바로가기",
    "keep에 저장",
    "네이버뉴스",
    "블로그",
    "카페"
)

BOOK_CONTEXT_KEYWORDS = (
    "김현승", "부크크", "bookk", "출간", "저자", "작가",
    "시집", "에세이", "도서", "책", "독서", "서평", "리뷰", "후기",
    "yes24", "알라딘", "교보문고"
)

SECTION_STOP_PATTERN = re.compile(
    r"^(?:목차|차례|책\s*소개|책소개|작품\s*소개|작품소개|저자\s*소개|저자소개|출판사\s*서평|출판사서평|배송/반품/교환|배송\s*/\s*반품|리뷰\s*\(\d*\)|관련\s*도서)$",
    re.IGNORECASE
)

UI_NOISE_LINES = {
    "더보기", "접기", "공유하기", "장바구니", "바로구매", "찜하기",
    "로그인", "회원가입", "고객센터", "이용약관", "개인정보처리방침"
}


def clean_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    no_tags = re.sub(r"<[^>]*>", " ", raw_html)
    no_broken_prefix = re.sub(r"^[^<]*>", " ", no_tags)
    unescaped = html.unescape(no_broken_prefix)
    cleaned = re.sub(r"(Keep에 바로가기|Keep에 저장|새 창 열림)", " ", unescaped)
    return re.sub(r"\s+", " ", cleaned).strip()


def normalize_compact(text: str) -> str:
    return re.sub(r"[\s\W_]+", "", text or "").lower()


def fetch_html(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def parse_section_from_lines(lines: list[str], start_keywords: tuple[str, ...]) -> list[str]:
    """렌더링된 텍스트 줄 목록에서 지정된 섹션 제목 이후 다음 섹션 전까지의 줄을 추출합니다."""
    start_idx = -1
    for i, line in enumerate(lines):
        compact = normalize_compact(line)
        if any(normalize_compact(kw) == compact or line.strip() in start_keywords for kw in start_keywords):
            start_idx = i + 1
            break

    if start_idx == -1:
        return []

    collected: list[str] = []
    for line in lines[start_idx:]:
        trimmed = re.sub(r"\s+", " ", line).strip()
        if not trimmed:
            continue
        if SECTION_STOP_PATTERN.match(trimmed):
            break
        if trimmed in UI_NOISE_LINES:
            continue
        if trimmed not in collected:
            collected.append(trimmed)
        if len(collected) >= 50:
            break

    return collected


def fetch_bookk_details_with_playwright(bookk_url: str) -> dict:
    """Playwright로 부크크 페이지를 렌더링해 제목, 표지, 책 소개, 목차를 추출합니다."""
    info = {"title": "", "summary": "", "cover_url": "", "toc": []}

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale="ko-KR"
            )
            page = context.new_page()
            page.goto(bookk_url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            # 접힌 섹션이나 더보기 버튼이 있다면 클릭 시도
            for btn_text in ("목차", "책 소개", "더보기"):
                try:
                    loc = page.get_by_text(btn_text, exact=False).first
                    if loc.is_visible(timeout=500):
                        loc.click(timeout=1000)
                        page.wait_for_timeout(400)
                except Exception:
                    pass

            og_title = page.locator('meta[property="og:title"]').get_attribute("content") or ""
            og_desc = page.locator('meta[property="og:description"]').get_attribute("content") or ""
            og_img = page.locator('meta[property="og:image"]').get_attribute("content") or ""
            body_text = page.inner_text("body")

            browser.close()

        if og_title:
            info["title"] = re.sub(r"\s*\|\s*부크크.*$", "", clean_text(og_title)).strip()

        if og_img:
            img_url = html.unescape(og_img).strip()
            info["cover_url"] = ("https:" + img_url) if img_url.startswith("//") else img_url

        lines = [re.sub(r"\s+", " ", ln).strip() for ln in body_text.splitlines() if ln.strip()]

        summary_lines = parse_section_from_lines(lines, ("책 소개", "책소개", "작품 소개", "작품소개"))
        if summary_lines:
            info["summary"] = "\n\n".join(summary_lines)
        elif og_desc and len(clean_text(og_desc)) > 15:
            info["summary"] = clean_text(og_desc)

        toc_lines = parse_section_from_lines(lines, ("목차", "차례"))
        if toc_lines:
            info["toc"] = [ln for ln in toc_lines if len(ln) <= 120][:40]

        return info

    except Exception as e:
        print(f"[WARN] Playwright failed for Bookk ({bookk_url}), falling back to static HTML: {e}")

    # 폴백: 정적 HTML 파싱
    try:
        page_html = fetch_html(bookk_url)
        og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)
        og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)
        og_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)

        if og_title:
            info["title"] = re.sub(r"\s*\|\s*부크크.*$", "", clean_text(og_title.group(1))).strip()
        if og_desc and len(clean_text(og_desc.group(1))) > 15:
            info["summary"] = clean_text(og_desc.group(1))
        if og_img:
            img_url = html.unescape(og_img.group(1)).strip()
            info["cover_url"] = ("https:" + img_url) if img_url.startswith("//") else img_url
    except Exception as e2:
        print(f"[WARN] Static fallback also failed ({bookk_url}): {e2}")

    return info


def is_valid_book_item(
    title: str,
    snippet: str,
    required_phrases: list[str],
    require_author_or_book: bool
) -> bool:
    if not title or len(title) < 4:
        return False
    if title.lower() in BLOCKED_TITLES:
        return False

    combined = f"{title} {snippet}"
    compact_combined = normalize_compact(combined)

    phrase_matched = any(
        normalize_compact(p) in compact_combined
        for p in required_phrases
        if p
    )
    if not phrase_matched:
        return False

    if require_author_or_book:
        lower_combined = combined.lower()
        if not any(kw in lower_combined for kw in BOOK_CONTEXT_KEYWORDS):
            return False

    return True


def parse_naver_results(
    page_html: str,
    required_phrases: list[str],
    require_author_or_book: bool,
    limit: int = 8,
    domain_filter: str | None = None
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

        if any(bd in href for bd in BLOCKED_DOMAINS):
            continue
        if domain_filter and domain_filter not in href:
            continue
        if href in seen_urls:
            continue

        start = max(0, match.start() - 120)
        end = min(len(page_html), match.end() + 700)
        context_block = clean_text(page_html[start:end])
        snippet = context_block.replace(title, "", 1).strip()
        if len(snippet) > 200:
            snippet = snippet[:200].rsplit(" ", 1)[0] + "..."

        if not is_valid_book_item(title, snippet, required_phrases, require_author_or_book):
            continue

        seen_urls.add(href)
        results.append({
            "title": title,
            "snippet": snippet,
            "blogger": "네이버 블로그" if domain_filter == "blog.naver.com" else "네이버 검색",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "link": href
        })

        if len(results) >= limit:
            break

    return results


def search_naver_web(
    query: str,
    required_phrases: list[str],
    require_author_or_book: bool,
    where: str = "nexearch",
    limit: int = 8,
    domain_filter: str | None = None
) -> list[dict]:
    encoded_q = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where={where}&query={encoded_q}"
    try:
        page_html = fetch_html(url)
        return parse_naver_results(
            page_html,
            required_phrases=required_phrases,
            require_author_or_book=require_author_or_book,
            limit=limit,
            domain_filter=domain_filter
        )
    except Exception as e:
        print(f"[WARN] Failed to fetch Naver search ({query}, {where}): {e}")
        return []


def build_dataset() -> dict:
    os.makedirs("data", exist_ok=True)
    books_output = []

    for seed in BOOKS_SEED:
        bookk_info = fetch_bookk_details_with_playwright(seed["bookk_url"])
        time.sleep(random.uniform(0.8, 1.5))

        resolved_title = (bookk_info["title"] or seed["query"] or seed["fallback_title"]).strip()
        required_phrases = seed["required_phrases"]
        require_ctx = seed["require_author_or_book"]

        blog_items = search_naver_web(
            f'"{resolved_title}" "김현승"',
            required_phrases=required_phrases,
            require_author_or_book=require_ctx,
            where="blog",
            limit=8,
            domain_filter="blog.naver.com"
        )
        if not blog_items:
            blog_items = search_naver_web(
                f'"{resolved_title}" "김현승"',
                required_phrases=required_phrases,
                require_author_or_book=require_ctx,
                where="nexearch",
                limit=8
            )

        time.sleep(random.uniform(1.0, 2.0))

        news_items = search_naver_web(
            f'"{resolved_title}" "김현승"',
            required_phrases=required_phrases,
            require_author_or_book=require_ctx,
            where="news",
            limit=6
        )

        time.sleep(random.uniform(1.0, 2.0))

        resolved_toc = bookk_info["toc"] if bookk_info["toc"] else (seed["toc"] or [])

        books_output.append({
            "id": seed["id"],
            "bookk_id": seed["bookk_id"],
            "bookk_url": seed["bookk_url"],
            "title": resolved_title,
            "author": seed["author"],
            "publisher": "부크크(bookk)",
            "pubdate": "",
            "isbn": "",
            "cover_url": seed["cover_url"] or bookk_info["cover_url"] or "",
            "summary": bookk_info["summary"] or seed["summary"],
            "toc": resolved_toc,
            "excerpts": seed["excerpts"],
            "reviews": blog_items,
            "press": news_items
        })

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "books": books_output
    }


if __name__ == "__main__":
    dataset = build_dataset()
    with open("data/books_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print("Updated data/books_data.json automatically with Playwright.")
