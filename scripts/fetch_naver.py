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
        "stores": {
            "paper": [
                {"name": "부크크", "url": "https://bookk.co.kr/bookStore/6b0590cade1ad179312a4036"}
            ],
            "ebook": [
                {"name": "부크크 eBook", "url": "https://bookk.co.kr/bookStore/6b07a74913cd34e08772d3cc"}
            ]
        },
        "query": "말이 줄어든 자리에 남는 것들",
        "required_phrases": ["말이 줄어든 자리에 남는 것들", "말이줄어든자리에남는것들"],
        "require_author_or_book": False,
        "fallback_title": "말이 줄어든 자리에 남는 것들",
        "author": "김현승",
        "cover_url": "",
        "summary": (
            "우리는 얼마나 많은 말을 하며 살아왔을까.\n"
            "나를 이해시키기 위해 설명하고, 오해받지 않기 위해 해명하고, 누군가에게 인정받기 위해 끊임없이 자신을 증명해 왔다.\n\n"
            "하지만 시간이 흐를수록 깨닫게 된다.\n"
            "모든 말이 진심을 전달하는 것은 아니며, 모든 관계를 붙잡아야 하는 것도 아니라는 사실을.\n\n"
            "어쩌면 삶이 깊어진다는 것은 더 많은 것을 말하는 일이 아니라, 굳이 설명하지 않아도 되는 것들을 알아가는 과정인지도 모른다.\n\n"
            "《말이 줄어든 자리에 남는 것들》은 쉼 없이 쏟아지는 세상의 소음에서 한 걸음 물러나, 자신의 내면을 들여다보는 여정이다.\n"
            "타인의 시선과 평가에서 벗어나는 법, 상처를 품고도 무너지지 않는 마음, 가까운 관계일수록 필요한 여백, 때로는 단호하게 거절할 줄 아는 용기, 그리고 나만의 속도로 삶을 살아가는 지혜를 이야기한다.\n\n"
            "일과 관계에서의 침묵부터 혼자만의 시간과 자기 돌봄, 나이 듦과 성숙, 지나온 삶을 정리하고 다음 세대에 남기고 싶은 태도까지.\n"
            "일상의 여러 순간을 통해 무엇을 덜어내고 무엇을 지켜야 하는지 조용히 질문한다.\n\n"
            "말을 줄인다고 마음까지 닫을 필요는 없다. 침묵은 누군가를 외면하는 차가움이 아니라, 나 자신과 타인을 조금 더 깊이 이해하기 위한 여백일 수 있다.\n"
            "이제는 모든 사람에게 이해받으려 애쓰지 않아도 좋다. 모든 관계에 자신을 소모하지 않아도 좋다. 남들의 속도에 맞추느라 정작 자신의 삶을 놓치지 않아도 좋다.\n\n"
            "말이 줄어든 자리에는 무엇이 남을까.\n"
            "어쩌면 그곳에는 타인의 인정이 아닌 나만의 평온이, 화려한 말이 아닌 진심이, 끝없는 욕망이 아닌 삶의 여백이 남아 있을 것이다.\n\n"
            "이 책이 당신에게 불필요한 소음을 잠시 내려놓고, 오래 보아도 질리지 않는 자신만의 삶을 발견하는 시간이 되기를 바란다."
        ),
        "toc": [
            "#프롤로그 말이 줄어든 자리에서 들리기 시작한 것들",
            "[제1부] 소음을 끄고 내면의 방으로",
            "제1장. 소음의 시대, 말의 쓸모를 묻다",
            "제2장. 속삭임이 울림이 되는 나이",
            "제3장. 혼자만의 방, 내면의 소리",
            "제4장. 오래 보아도 질리지 않는 삶의 문법",
            "제5장. 상처받지 않기 위한 마음",
            "제6장. 거절의 미덕, '아니오'",
            "제7장. 속도의 시대에 역행하는 고요한 발걸음",
            "제8장. 후회와 미련이라는 소음을 건너며",
            "제9장. 나이 들수록 깊어지는 사색",
            "제10장. 침묵의 끝에서 피어나는 삶의 온기",
            "제11장. 실패와 상실 앞에서 입을 다무는 법",
            "제12장. 시간의 결을 따라 늙어간다는 것의 미학",
            "[제2부] 침묵이 일과 관계의 품격이 될 때",
            "제13장. 일의 세계에서 빛나는 과묵함의 힘",
            "제14장. 사랑과 가족, 가까운 사이일수록 필요한 여백",
            "제15장. 욕망과 소유를 줄이는 물질의 침묵",
            "제16장. 디지털 소음에서 벗어난 감각의 회복",
            "제17장. 경청, 말을 줄인 자만이 얻는 초능력",
            "제18장. 분노와 감정 폭발을 다스리는 침묵의 쉼표",
            "[제3부] 계절과 세월을 건너는 관조의 미학",
            "제19장. 자연이 가르쳐준 위대한 침묵의 언어",
            "제20장. 예술과 고전, 시대를 건너온 침묵의 울림",
            "제21장. 유한함을 깨닫는 나이, 삶의 군더더기를 덜어내다",
            "제22장. 침묵이 빚어낸 어른의 뒷모습",
            "제23장. 다시, 나만의 문장으로 삶을 써 내려가며",
            "제24장. 오래 보아도 질리지 않는 사람",
            "[제4부] 흔들리지 않는 일상의 리듬과 자기 돌봄",
            "제25장. 몸이 먼저 알아차리는 말의 피로",
            "제26장. 혼자만의 시간을 지키는 단단한 루틴",
            "제27장. 조급함을 덜어낸 시간의 주권",
            "제28장. 지친 마음을 눕히는 고요한 회복",
            "[제5부] 침묵이 남긴 자리에서 피어나는 삶",
            "제29장. 오해와 평가 너머의 담담한 시선",
            "제30장. 전환기의 문턱에서 서두르지 않는 용기",
            "제31장. 다 말하지 않고도 남는 마음의 결",
            "제32장. 세월의 끝자락까지 이어질 조용한 품격",
            "[제6부] 덜어낸 자리에 남는 사람과 공간의 온도",
            "제33장. 곁에 남는 사람들의 공통점",
            "제34장. 머무는 공간이 닮아가는 내면의 고요",
            "제35장. 도움을 주고받는 어른의 담백한 방식",
            "제36장. 침묵이 허락하는 깊고 느슨한 연대",
            "[제7부] 지나온 계절을 건너 다음 세대에게 남기는 문장",
            "제37장. 후회 없는 기억을 남기는 정리의 시간",
            "제38장. 말 대신 삶의 결로 건네는 조용한 유산",
            "제39장. 끝나지 않는 배움, 침묵 속에서 다시 묻다",
            "제40장. 오래 보아도 질리지 않는 한 사람의 뒷모습",
            "#에필로그 오래 보아도 질리지 않는 사람으로 남는다는 것"
        ],
        "excerpts": [
            "말이 줄어든 자리에 비로소 들리기 시작하는 것들이 있다.",
            "바쁘게 지나쳐 온 계절 끝에서, 나는 나에게 가장 늦게 말을 건넸다."
        ]
    },
    {
        "id": "book-2",
        "bookk_id": "67b32cdd74f2ff3eee47f6b1",
        "bookk_url": "https://bookk.co.kr/bookStore/67b32cdd74f2ff3eee47f6b1",
        "stores": {
            "paper": [
                {
                    "name": "네이버 도서",
                    "url": "https://search.shopping.naver.com/book/search?bookTabType=ALL&pageIndex=1&pageSize=40&query=%EB%A9%88%EC%B6%B0%EC%84%9C+%EB%8F%8C%EC%95%84%EB%B3%B8%EB%8B%A4&sort=REL&prevQuery=%EB%A9%88%EC%B6%B0%EC%84%9C%EB%8F%8C%EC%95%84%EB%B3%B8%EB%8B%A4"
                }
            ],
            "ebook": [
                {
                    "name": "YES24 eBook",
                    "url": "https://www.yes24.com/Product/Goods/142843232"
                }
            ]
        },
        "query": "멈춰서 돌아본다",
        "required_phrases": ["멈춰서 돌아본다", "멈춰서돌아본다"],
        "require_author_or_book": True,
        "fallback_title": "멈춰서 돌아본다",
        "author": "김현승",
        "cover_url": "",
        "summary": (
            "온전한 내가 되었을 때\n"
            "삶은 나를 따라 움직입니다.\n\n"
            "너무 빠르게, 너무 힘들게\n"
            "앞만 보고 달리고 있다면\n\n"
            "잠시 멈춰서\n\n"
            "온전한 나를\n"
            "돌아보시길 바랍니다."
        ),
        "toc": [
            "「차례」",
            "#프롤로그 14",
            "#1부",
            "- 집중 17",
            "- 반복 18",
            "- 못된 습관 19",
            "- 공감 20",
            "- 결국 21",
            "- 그때 22",
            "- 고민 23",
            "- 옆에 24",
            "- 존재 25",
            "- 감정 사이 26",
            "- 그냥 27",
            "- 선(善)과 악(惡) 28",
            "- 없다 29",
            "- 가족 30",
            "- 쉼표 31",
            "#2부",
            "- 선물 33",
            "- 속마음 34",
            "- 오늘 35",
            "- 생각보다 36",
            "- 몰랐던 그곳 37",
            "- 선 38",
            "- 지나간다 39",
            "- 마지막에 40",
            "- 선입견 41",
            "- 좋은 생각 42",
            "- 오뚝이 43",
            "- 가끔은 44",
            "- 마스크 45",
            "- 나이 46",
            "- 반복*2 47",
            "#3부",
            "- 포기 49",
            "- 고민 상담 50",
            "- 심호흡 51",
            "- 듣는 바보 52",
            "- 그런 날 53",
            "- 공백 54",
            "- 휴식 55",
            "- 거래 56",
            "- 함께 57",
            "- 현타 58",
            "- 3초 59",
            "- 비교 60",
            "- 겉과 속 61",
            "- 기대 62",
            "- 표현 63",
            "#4부",
            "- 나이*2 65",
            "- 나는 66",
            "- 다름 67",
            "- 가족*2 68",
            "- 그리움 69",
            "- 처음 70",
            "- 적응 71",
            "- 옆에*2 72",
            "- 스트레스 73",
            "- 어쩔 수 없이 74",
            "- 좋은 사람 75",
            "- 쉼표*2 76",
            "- 무게 77",
            "- 반대 78",
            "- 가면 79",
            "#5부",
            "- 그곳 81",
            "- 선택 82",
            "- 생각 83",
            "- 나무 84",
            "- 성장 85",
            "- 선택*2 86",
            "- 그때로 87",
            "- 세월 88",
            "- 변화 89",
            "- 지향 90",
            "- 행복 91",
            "- 끝맺음 92",
            "- 경쟁 93",
            "- 인연 94",
            "- 세 가지 95",
            "#6부",
            "- 진심 97",
            "- 잘했다 98",
            "- 걱정 99",
            "- 그대 100",
            "- 오늘은 101",
            "- 엄마,아빠 102",
            "- 혼자라서 103",
            "- 순간 104",
            "- 금토일 105",
            "- 꽃잎 106",
            "- 정보 107",
            "- 낚시 108",
            "- 바보 109",
            "- 힐링 110",
            "- 원했던 것 111",
            "#7부",
            "- 성숙한 사람 113",
            "- 한 가지만 114",
            "- 믿음 115",
            "- 독 116",
            "- 클로버 117",
            "- 인연*2 118",
            "- 세월*2 119",
            "- 술 120",
            "- 편지 121",
            "- 열매 122",
            "- 얼굴 123",
            "- 한강 124",
            "- 그대*2 125",
            "- 반가운 사람 126",
            "- 거품 127",
            "#8부",
            "- 팽이 129",
            "- 옷 130",
            "- 길을 걷다가 131",
            "- 모닥불 132",
            "- 소나기 133",
            "- 엄마,아빠*2 134",
            "- 스마트폰 135",
            "- 해바라기 136",
            "- 빗방울 137",
            "- 눈물 138",
            "- 보름달 139",
            "- 눈사람 140",
            "- 봄 그리고 가을 141",
            "- 안녕 142",
            "- 구름 143",
            "#9부",
            "- 어렸을 적 145",
            "- 비행기 146",
            "- 나이*3 147",
            "- 시 148",
            "- 모래밭 149",
            "- 관객 150",
            "- 투명테이프 151",
            "- 발걸음 152",
            "- 가을바람 153",
            "- 낙엽 154",
            "- 밤공기 155",
            "- 여행 156",
            "- 지하철 157",
            "- 마음의 거리 158",
            "- 속상한 마음 159",
            "#10부",
            "- 그런 사람 161",
            "- 돌아오지 않는 그대 162",
            "- 망각 163",
            "- 세잎클로버 164",
            "- 무소식 165",
            "- 아쉽구나 166",
            "- 사랑 167",
            "- 호감 168",
            "- 싶으면 169",
            "- 선택*3 170",
            "- 내 이름 171",
            "#에필로그 173"
        ],
        "excerpts": [
            "완벽한 답보다 다정한 질문 하나가 하루를 버티게 할 때가 있다."
        ]
    },
    {
        "id": "book-3",
        "bookk_id": "646abe734222b24502d39197",
        "bookk_url": "https://bookk.co.kr/bookStore/646abe734222b24502d39197",
        "stores": {
            "paper": [
                {
                    "name": "네이버 도서",
                    "url": "https://search.shopping.naver.com/book/catalog/32492774157?cat_id=50011280&frm=MBOKPRO&query=%25ED%2595%2598%25EB%25A3%25A8%25EA%25B0%2580%2B%25ED%2596%2589%25EB%25B3%25B5%25ED%2595%25A0%2B%25EC%2588%2598%2B%25EC%259E%2588%25EB%258B%25A4%25EB%25A9%25B4&N"
                }
            ],
            "ebook": [
                {
                    "name": "YES24 eBook",
                    "url": "https://www.yes24.com/Product/Goods/142763189"
                }
            ]
        },
        "query": "하루가 행복할 수 있다면",
        "required_phrases": ["하루가 행복할 수 있다면", "하루가행복할수있다면"],
        "require_author_or_book": True,
        "fallback_title": "하루가 행복할 수 있다면",
        "author": "김현승",
        "cover_url": "",
        "summary": (
            "하루가 지나면 아는게 많아질 줄 알았는데,\n"
            "하루가 지나면서 알고 싶은게 많아진다.\n\n"
            "나이가 들면 모든게 이해될 줄 알았는데\n"
            "나이가 들면서 이해해야 할 것들이 많아진다.\n\n"
            "시간이 지나면\n"
            "자연스레 바뀔 줄 알았는데\n"
            "내 마음은 제자리일 뿐.\n\n"
            "이 책을 통해 다른 사람이 행복한 하루가 아닌\n"
            "당신의 하루가 행복할 수 있기를 바랍니다."
        ),
        "toc": [
            "#프롤로그 … 12",
            "Part 1. #오늘도_무너지지_말아",
            "┕ 길을 억지로 찾으려 하지 말자 누구에게나 열려 있으니까 … 16",
            "┕ 지금 내 삶이 무의미하다고 느껴질 때 … 22",
            "┕ 스스로 지치지 않는 법 … 27",
            "┕ 규칙대로 사는 것보단 가끔은 어기고 도전해 보는 것 … 30",
            "┕ 지금 가야 하는 길을 모르겠다면 … 35",
            "┕ 처음이니까 서툴어도 괜찮아 … 39",
            "┕ 중요하지만, 쫓는 사람이 되지 않기를 … 41",
            "┕ 가까운 듯 멀리만 느껴질 때 … 44",
            "┕ 갑자기 이유 없이 지치고 힘들 때 … 46",
            "┕ 주춤하고 있다면 … 49",
            "┕ 내 삶에 잊지 말아야 할 단 한 가지 … 52",
            "┕ 사람 관계에 '혹시나'라는 생각이 든다면 … 54",
            "┕ 성공하고 싶은 그대에게 … 56",
            "┕ 무수히 많은 생각이 머릿속을 지배할 때 … 59",
            "┕ 어린 나이에 일찍 사회생활로 지쳐 있다면 … 62",
            "┕ 만약, 도움의 손길이 의심스럽다면 … 65",
            "┕ 관계 속 허탈한 마음이 든다면 … 68",
            "┕ 상대방의 말 때문에 힘들다면 … 73",
            "┕ 작은 경험 속 높은 기준을 갖고 있다면 … 75",
            "┕ 능력이 부족하다고 느낄 때 … 77",
            "┕ 막 화나고 짜증이 날 때면 … 78",
            "┕ 혼자가 어렵다 생각이 들 때 … 81",
            "Part 2. #내일을_향한_프롤로그",
            "┕ 당신은 내일을 기대할 수 있는 행복한 사람입니다 … 84",
            "┕ 지금이 내 삶에 가장 젊은 시간 … 89",
            "┕ 지우고 싶은 기억이 앞으로 만들어 갈 소중한 기억을 막지 않기를 … 92",
            "┕ 버리세요 늦지 않았으니까 … 95",
            "┕ 가끔은 나도 그들 덕분에 살아요 … 98",
            "┕ 참 아까워요 당신이 … 100",
            "┕ 들려주세요 … 103",
            "┕ 사람에게 받은 상처 조금씩 내려놓아도 좋습니다 … 105",
            "┕ 그들에게 어울리는 대접을 해주세요 … 109",
            "┕ 사람 관계는 모닥불처럼 … 111",
            "┕ 알아도 모르는 척하세요 … 113",
            "┕ 지금이라도, 공유하세요 … 116",
            "┕ 즐겁고 행복하게 살고 싶다면 보는 방식을 바꿔보자 … 118",
            "┕ 자존감을 높여보세요 새로운 세상이 기다릴 거예요 … 121",
            "┕ 조금만 귀 기울여 보세요 … 124",
            "┕ 내 삶의 변화를 위해 … 127",
            "┕ 더도 말고 덜도 말고 딱 그 정도만 … 128",
            "┕ 다 지나갈 테니, 걱정하지 마세요 … 129",
            "┕ 인생은 거북이처럼 … 130",
            "┕ 하는 일이 잘 안되죠 괜찮아요 … 132",
            "┕ 행복해지는 게 참 어렵죠 이것만 하지 말아요 … 134",
            "Part 3. #하루를_채우는_나와의_경쟁",
            "┕ 남보다 내 마음을 얻으려 애쓰도록 … 138",
            "┕ 받고 싶던 사랑은 나 자신을 사랑하지 않았던 ‘나의 사랑’이란 걸 깨달았다 … 140",
            "┕ 너는 너고, 나는 나야 … 144",
            "┕ 내가 나를 놓아 버리기 전에 … 147",
            "┕ 나 아니면 안되는 것들도 많습니다 … 149",
            "┕ 가끔은 가슴 속에서 하고 싶었던 말 … 151",
            "┕ 남의 만족이 아닌 내가 주최 하는 삶 … 154",
            "┕ 작은 다툼이 있더라도 … 157",
            "┕ 나에게 주는 작고 당당한 속삭임 … 159",
            "┕ 나만의 여행 … 161",
            "┕ 나를 힘들게 하는 사람이 있다면 … 162",
            "┕ 내가 다른 사람이 되어간다고 느낄 때 한 번씩 … 164",
            "┕ 내 생각 그리고 행동에 의심하지 마세요 … 166",
            "┕ 나에게 하는 조언 … 169",
            "┕ 내가 살아가는 2가지 힘 … 171",
            "┕ 문득, 내가 보이지 않을 때 … 172",
            "┕ 버려야 할 나의 심리 … 173",
            "┕ 나에게 30%의 사랑만이라도 … 174",
            "┕ 나를 방어하는 무기는 ‘겸손 … 176",
            "┕ 내가 진정으로 바랐던 것 … 179",
            "┕ SNS에 나를 비교하지 말아요 … 182",
            "┕ 보는 관점으로 나를 돌아볼 수 있는 자세 … 186",
            "┕ 나만 모르는 한 가지 … 188",
            "┕ 나는 '별' … 190",
            "┕ 내 삶의 그릇 … 191",
            "Part 4.#나를_위한_이야기",
            "┕ 평범한 하루를 마무리하는 마음 … 193",
            "┕ 어쩌다 한 번쯤은 … 197",
            "┕ '우리'라는 존재 … 198",
            "┕ 하루를 보내는 4가지 단어 … 199",
            "┕ 첫 만남, 기억 속에 일기 … 201",
            "┕ 세상에 하나뿐인 귀한 보물 … 203",
            "┕ 남자 그리고 여자 사이에서 … 206",
            "┕ 당신은 약하기도 하지만 강하기도 한 존재입니다 … 209",
            "┕ 20대에게 그리고 30대의 작은 여유 … 211",
            "┕ 거절하지 못하는 건 당신의 문제가 아니라 상황 때문이다 … 213",
            "┕ 잊는다는 것도 가끔은 … 215",
            "┕ 올바른 욕심 … 217",
            "┕ 사주가 말하는 이야기가 나의 인생일까 … 219",
            "┕ 진실한 마음 표현 방법 3가지 … 222",
            "┕ 사랑이란 … 224",
            "┕ 한 번뿐인 짧은 인생 … 225",
            "┕ 성장 그리고 책 … 227",
            "┕ 사람에게 받은 상처 … 229",
            "#에필로그 … 232"
        ],
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


def fetch_bookk_cover_and_title(bookk_url: str) -> dict:
    """부크크 페이지에서 최신 표지 URL과 제목을 보조로 가져옵니다."""
    info = {"title": "", "cover_url": ""}
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale="ko-KR"
            )
            page = context.new_page()
            page.goto(bookk_url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1200)

            og_title = page.locator('meta[property="og:title"]').get_attribute("content") or ""
            og_img = page.locator('meta[property="og:image"]').get_attribute("content") or ""
            browser.close()

        if og_title:
            info["title"] = re.sub(r"\s*\|\s*부크크.*$", "", clean_text(og_title)).strip()
        if og_img:
            img_url = html.unescape(og_img).strip()
            info["cover_url"] = ("https:" + img_url) if img_url.startswith("//") else img_url
        return info
    except Exception:
        pass

    try:
        page_html = fetch_html(bookk_url)
        og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)
        og_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', page_html, re.I)
        if og_title:
            info["title"] = re.sub(r"\s*\|\s*부크크.*$", "", clean_text(og_title.group(1))).strip()
        if og_img:
            img_url = html.unescape(og_img.group(1)).strip()
            info["cover_url"] = ("https:" + img_url) if img_url.startswith("//") else img_url
    except Exception as e:
        print(f"[WARN] Failed to fetch Bookk meta ({bookk_url}): {e}")
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


def sanitize_store_list(raw_list: list[dict] | None) -> list[dict]:
    if not raw_list:
        return []
    cleaned = []
    for item in raw_list:
        name = (item.get("name") or "").strip()
        url = (item.get("url") or "").strip()
        if name and url.startswith(("http://", "https://")):
            cleaned.append({"name": name, "url": url})
    return cleaned


def build_dataset() -> dict:
    os.makedirs("data", exist_ok=True)
    books_output = []

    for seed in BOOKS_SEED:
        bookk_meta = fetch_bookk_cover_and_title(seed["bookk_url"])
        time.sleep(random.uniform(0.8, 1.5))

        resolved_title = (seed["query"] or seed["fallback_title"] or bookk_meta["title"]).strip()
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

        raw_stores = seed.get("stores") or {}
        paper_stores = sanitize_store_list(raw_stores.get("paper"))
        if not paper_stores and seed.get("bookk_url"):
            paper_stores = [{"name": "부크크", "url": seed["bookk_url"]}]
        ebook_stores = sanitize_store_list(raw_stores.get("ebook"))

        books_output.append({
            "id": seed["id"],
            "bookk_id": seed["bookk_id"],
            "bookk_url": seed["bookk_url"],
            "stores": {
                "paper": paper_stores,
                "ebook": ebook_stores
            },
            "title": resolved_title,
            "author": seed["author"],
            "publisher": "부크크(bookk)",
            "pubdate": "",
            "isbn": "",
            "cover_url": seed["cover_url"] or bookk_meta["cover_url"] or "",
            "summary": seed["summary"],
            "toc": seed["toc"],
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
    print("Updated data/books_data.json with paper and ebook store links.")
