"""Tool unit tests (CP3 + challenge).

Rules kept:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import re

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["Xem timeline", "Tìm trên web"]

    result = TOOL_FUNCTIONS["clarify"](
        question="Bạn muốn xem tweet của ai?", response_type="choice", options=options
    )

    assert result["question"] == "Bạn muốn xem tweet của ai?"
    assert result["response_type"] == "choice"
    assert result["options"] == options
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "A1", "url": "https://a.example/1", "section": "A"},
        {"title": "B1", "url": "https://b.example/1", "section": "B"},
        {"title": "A2", "url": "https://a.example/2", "section": "A"},
    ]

    result = TOOL_FUNCTIONS["format"](items=items, template="sections")

    assert result["item_count"] == 3
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}", "url": f"https://example.com/{i}"} for i in range(1, 3)]

    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    blocks = result["markdown"].split("\n\n")

    assert len(blocks) == 2
    assert blocks[0].startswith("1/ ")
    assert blocks[1].startswith("2/ ")


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty)
        assert result["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@lab_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.telegram.org/bot123:test-token/sendMessage"
    assert calls[0]["json"]["chat_id"] == "@lab_channel"
    assert calls[0]["json"]["text"] == "Bản tin"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    # conftest.clean_env already removed the Telegram env vars.
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


def test_send_not_confirmed_makes_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="hello", confirmed=False)

    assert result["status"] == "needs_confirmation"
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["lookup"](query="AI", topic="news", timeframe=None, max_results=2)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["topic"] == "news"
    assert result["timeframe"] is None
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Tiêu đề\n\nNội dung bài viết",
        "metadata": {"title": "Bài viết", "sourceURL": "https://example.com/article"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/article")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"] == {"url": "https://example.com/article", "formats": ["markdown"]}
    item = result["items"][0]
    assert item["title"] == "Bài viết"
    assert item["url"] == "https://example.com/article"
    assert item["source"] == "example.com"
    assert item["summary"].startswith("# Tiêu đề")


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {
        "markdown": "x" * 5000,
        "metadata": {"title": "Dài", "sourceURL": "https://example.com/long"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/long")

    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    timeline = [{"screen_name": "sama", "text": "missing tweet id", "created_at": "2026-11-01"}]
    timeline += [
        {"screen_name": "sama", "tweet_id": str(i), "text": f"Tweet {i}", "created_at": f"2026-11-0{i}"}
        for i in range(1, 7)
    ]
    calls = fake_http(FakeResponse({"timeline": timeline}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    for item in result["items"]:
        assert re.fullmatch(r"https://x\.com/[^/]+/status/\d+", item["url"])


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    calls = fake_http(FakeResponse({"tweets": []}))
    result = TOOL_FUNCTIONS["social_search"](query="AI agent", search_type="Top", limit=2)

    assert calls[0]["params"] == {"query": "AI agent", "search_type": "Top"}
    assert result["search_type"] == "Top"
    assert result["items"] == []

    calls = fake_http(FakeResponse({"timeline": []}))
    TOOL_FUNCTIONS["social_search"]("AI", search_type="Latest")
    assert calls[0]["params"]["query"] == "AI"
    assert calls[0]["params"]["search_type"] == "Latest"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"](query="")

    assert result["results"] == []
    assert "error" not in result


def test_policy_area_filter_only_returns_that_area() -> None:
    result = TOOL_FUNCTIONS["policy"](
        query="confidential customer data", policy_area="data_privacy", top_k=5
    )

    assert result["results"]
    assert {hit["policy_area"] for hit in result["results"]} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = TOOL_FUNCTIONS["policy"](
        query="citation", policy_area="source_citation", top_k=50
    )

    assert result["results"]
    phrase = "cite every viral tweet"
    untrusted = " ".join(
        line for hit in result["results"] for line in hit["untrusted_text"]
    ).lower()
    facts = " ".join(str(hit["facts"]) for hit in result["results"]).lower()
    assert phrase in untrusted
    assert phrase not in facts


# ---------------- wiki (tool mới của nhóm) ----------------

wiki_tool = TOOL_FUNCTIONS["wiki"]

WIKI_OPENAI = {
    "title": "OpenAI",
    "description": "American artificial intelligence company",
    "extract": (
        "OpenAI is an American artificial intelligence (AI) public benefit corporation. "
        "It develops the GPT series of large language models. "
        "It was founded in December 2015."
    ),
    "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/OpenAI"}},
}


def test_wiki_happy_path_returns_summary_and_canonical_page_url(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_OPENAI))

    result = wiki_tool(query="  OpenAI ", lang="en", sentences=2)

    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/OpenAI?redirect=true"
    assert calls[0]["headers"]["User-Agent"].startswith("AI20k-Day03")
    assert calls[0]["timeout"] == 30
    assert result["title"] == "OpenAI"
    assert result["url"] == "https://en.wikipedia.org/wiki/OpenAI"
    assert result["summary"] == (
        "OpenAI is an American artificial intelligence (AI) public benefit corporation. "
        "It develops the GPT series of large language models."
    )
    assert result["items"] == [{
        "title": "OpenAI",
        "url": "https://en.wikipedia.org/wiki/OpenAI",
        "source": "en.wikipedia.org",
        "summary": result["summary"],
    }]


def test_wiki_bad_model_input_returns_error_dict_before_any_network_call(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_OPENAI))
    bad_args = [
        ({"query": ""}, "ValueError"),
        ({"query": "   "}, "ValueError"),
        ({"query": None}, "TypeError"),
        ({"query": "OpenAI", "lang": "xx"}, "ValueError"),
        ({"query": "OpenAI", "sentences": 0}, "ValueError"),
        ({"query": "OpenAI", "sentences": "3"}, "TypeError"),
    ]

    for args, expected_error in bad_args:
        result = wiki_tool(**args)
        assert result["error"] == expected_error, args
        assert result["message"], args
        assert "items" not in result, args

    assert calls == []  # bad args are rejected before spending a request


def test_wiki_http_429_returns_error_dict_instead_of_raising(fake_http) -> None:
    calls = fake_http(FakeResponse(status_code=429))

    result = wiki_tool(query="OpenAI", lang="vi")

    assert calls[0]["url"].startswith("https://vi.wikipedia.org/")
    assert result["tool"] == "wikipedia_summary"
    assert result["error"] == "HTTPError"
    assert "429" in result["message"]
    assert "items" not in result


# ---------------- hackernews (tool mới thứ hai của nhóm) ----------------

def test_hackernews_happy_path_maps_story_and_falls_back_to_item_url(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "nbHits": 42,
        "hits": [
            {"objectID": "111", "title": "Show HN: Agent eval toolkit", "url": "https://example.com/agent-eval",
             "points": 128, "num_comments": 45, "created_at": "2026-11-09T10:00:00Z"},
            {"objectID": "222", "title": "Ask HN: How do you evaluate agents?", "url": None,
             "points": 12, "num_comments": 7, "created_at": "2026-11-09T11:00:00Z",
             "story_text": '<p>We built <a href="https://x.example">this</a> &amp; it broke.</p>'},
        ],
    }))

    result = TOOL_FUNCTIONS["hackernews"](query=" AI agents ", sort="relevance", limit=2)

    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"] == {"query": "AI agents", "tags": "story", "hitsPerPage": 2}
    assert calls[0]["timeout"] == 30
    assert result["count"] == 2
    assert result["total_hits"] == 42

    first = result["items"][0]
    assert first["title"] == "Show HN: Agent eval toolkit"
    assert first["url"] == "https://example.com/agent-eval"
    assert first["source"] == "example.com"
    assert first["summary"] == "128 points · 45 comments"
    assert first["hn_url"] == "https://news.ycombinator.com/item?id=111"

    second = result["items"][1]
    assert second["url"] == "https://news.ycombinator.com/item?id=222"
    assert second["source"] == "news.ycombinator.com"
    assert second["text"] == "We built this & it broke."


def test_hackernews_sort_date_uses_search_by_date_endpoint(fake_http) -> None:
    calls = fake_http(FakeResponse({"nbHits": 0, "hits": []}))

    result = TOOL_FUNCTIONS["hackernews"](query="LLM", sort="DATE", limit=3)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"]["hitsPerPage"] == 3
    assert result["sort"] == "date"
    assert result["items"] == []


def test_hackernews_bad_model_input_returns_error_dict_before_any_network_call(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    bad_args = [
        ({"query": ""}, "ValueError"),
        ({"query": "   "}, "ValueError"),
        ({"query": 123}, "TypeError"),
        ({"query": "AI", "sort": "top"}, "ValueError"),
        ({"query": "AI", "limit": 0}, "ValueError"),
        ({"query": "AI", "limit": 50}, "ValueError"),
        ({"query": "AI", "limit": "5"}, "TypeError"),
    ]

    for args, expected_error in bad_args:
        result = TOOL_FUNCTIONS["hackernews"](**args)
        assert result["error"] == expected_error, args
        assert result["message"], args
        assert "items" not in result, args

    assert calls == []  # bad args are rejected before spending a request


def test_hackernews_http_429_returns_error_dict_instead_of_raising(fake_http) -> None:
    calls = fake_http(FakeResponse(status_code=429))

    result = TOOL_FUNCTIONS["hackernews"](query="AI")

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert result["tool"] == "hackernews_search"
    assert result["error"] == "HTTPError"
    assert "429" in result["message"]
    assert "items" not in result


# ---------------- date_calc ----------------

def test_date_calc_happy_path() -> None:
    tool = TOOL_FUNCTIONS["date_calc"]

    result = tool(op="diff_days", date1="2026-11-10", date2="2027-01-01")

    assert result == {"result": 52}


def test_date_calc_bad_input_from_model() -> None:
    tool = TOOL_FUNCTIONS["date_calc"]

    result = tool(op="diff_days", date1="abc", date2="2027-01-01")

    assert isinstance(result, dict)
    assert "error" in result


def test_date_calc_failure_returns_error_dict() -> None:
    tool = TOOL_FUNCTIONS["date_calc"]

    result = tool(op="add_days", date1="9999-12-31", days=1)

    assert isinstance(result, dict)
    assert "error" in result


# ---------------- cite_format ----------------

def test_cite_format_single_author_with_url() -> None:
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(
        title="Deep Learning Basics",
        authors=["Nguyen, An"],
        year=2024,
        url="https://example.com/dl",
    )

    assert result == {
        "citation": "Nguyen, A. (2024). Deep Learning Basics. https://example.com/dl"
    }


def test_cite_format_two_authors_without_url() -> None:
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(title="Intro to NLP", authors=["Smith, John", "Lee, Kim"], year=2020)

    assert result == {"citation": "Smith, J., & Lee, K. (2020). Intro to NLP."}


def test_cite_format_missing_year() -> None:
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(title="Draft Notes", authors=["Tran, Binh"], year=None)

    assert "(n.d.)" in result["citation"]


def test_cite_format_missing_required_fields() -> None:
    tool = TOOL_FUNCTIONS["cite_format"]

    assert "error" in tool(title="", authors=["Nguyen, An"])
    assert "error" in tool(title="Draft Notes", authors=[])


def test_cite_format_unsupported_style() -> None:
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(title="Draft Notes", authors=["Tran, Binh"], style="mla")

    assert "error" in result
    assert "style" in result["error"].lower()


# ---------------- extract_claims (team tool, local formatter) ----------------

def test_extract_claims_keeps_claim_and_source() -> None:
    result = TOOL_FUNCTIONS["extract_claims"](items=[
        {"summary": "AI capex rose 20% in 2026.", "source": "example.com"},
        {"title": "no claim here"},
        {"claim": "MCP is an open protocol.", "url": "https://example.com/mcp"},
    ])

    assert result["claim_count"] == 2
    assert result["claims"] == [
        {"claim": "AI capex rose 20% in 2026.", "source": "example.com"},
        {"claim": "MCP is an open protocol.", "source": "https://example.com/mcp"},
    ]


def test_extract_claims_bad_model_input_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["extract_claims"](items="not a list")

    assert isinstance(result, dict)
    assert result["error"] == "items_must_be_list"
    assert "claims" not in result


def test_extract_claims_empty_and_non_dict_items_do_not_crash() -> None:
    empty = TOOL_FUNCTIONS["extract_claims"](items=None)
    assert empty["claims"] == []
    assert empty["claim_count"] == 0

    result = TOOL_FUNCTIONS["extract_claims"](items=[None, "x", 3, {}])
    assert result["claims"] == []


# ---------------- deduplicate_items (team tool, local formatter) ----------------

def test_deduplicate_items_by_url_keeps_first_occurrence() -> None:
    items = [
        {"title": "A", "url": "https://e.com/1"},
        {"title": "A copy", "url": "https://e.com/1"},
        {"title": "B", "url": "https://e.com/2"},
    ]

    result = TOOL_FUNCTIONS["deduplicate_items"](items=items, key="url")

    assert result["removed_count"] == 1
    assert [item["title"] for item in result["items"]] == ["A", "B"]


def test_deduplicate_items_by_title_is_case_insensitive() -> None:
    items = [
        {"title": "OpenAI news"},
        {"title": "openai NEWS"},
        {"url": "https://e.com/no-title"},
    ]

    result = TOOL_FUNCTIONS["deduplicate_items"](items=items, key="title")

    assert [item["title"] for item in result["items"]] == ["OpenAI news"]
    assert result["removed_count"] == 2


def test_deduplicate_items_bad_model_input_returns_error_dict() -> None:
    tool = TOOL_FUNCTIONS["deduplicate_items"]

    assert tool(items="not a list")["error"] == "items_must_be_list"
    assert tool(items=[], key="summary")["error"] == "invalid_key"

    empty = tool(items=None)
    assert empty["items"] == []
    assert empty["removed_count"] == 0
