#!/usr/bin/env python3
"""Extract web search results from Phase 2 agent transcripts."""
import json
import os
import sys

TRANSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(TRANSCRIPT_DIR, "extracted")

# Mapping from INDEX.md
AGENT_MAP = {
    "a051e5c61d947f5dc": {"job": "EP_007_Q1", "output": "whitney_webb_Q1_top_claims"},
    "a668a77b314ff4c09": {"job": "EP_007_Q2", "output": "whitney_webb_Q2_bcci_verification"},
    # Q3 already recovered - skip
    "ad811ad5ed94ac67b": {"job": "EP_007_Q4", "output": "whitney_webb_Q4_science_verification"},
    "ad2c30ecf2bcd2654": {"job": "EP_007_Q5", "output": "whitney_webb_Q5_weak_claims"},
    "a6796c0bbe274f0d6": {"job": "EP_008_Q1", "output": "epstein_gravity_crossref"},
    "a78a0554cbfcd82df": {"job": "EP_008_Q2", "output": "epstein_financial_crossref"},
    "ac75a11eb1645b2d5": {"job": "EP_008_Q3", "output": "epstein_iran_contra_crossref"},
    "ab6bf13ecb18c55f4": {"job": "EP_008_Q4", "output": "lutnick_entity_crossref"},
}


def extract_research(jsonl_path):
    """Extract all web search queries and results from an agent transcript."""
    research = []
    assistant_text = []

    with open(jsonl_path) as f:
        lines = f.readlines()

    pending = {}  # tool_use_id -> query info
    for line in lines:
        try:
            data = json.loads(line.strip())
            msg = data.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", [])

            if not isinstance(content, list):
                # Might be a text string from assistant
                if role == "assistant" and isinstance(content, str) and len(content) > 50:
                    assistant_text.append(content)
                continue

            for block in content:
                if not isinstance(block, dict):
                    continue

                # Capture assistant reasoning text
                if block.get("type") == "text" and role == "assistant":
                    text = block.get("text", "")
                    if len(text) > 50:
                        assistant_text.append(text)

                # Capture search queries (WebSearch)
                if block.get("type") == "tool_use" and block.get("name") == "WebSearch":
                    tool_id = block.get("id", "")
                    inp = block.get("input", {})
                    pending[tool_id] = {
                        "type": "WebSearch",
                        "query": inp.get("query", ""),
                    }

                # Capture web fetch (WebFetch)
                if block.get("type") == "tool_use" and block.get("name") == "WebFetch":
                    tool_id = block.get("id", "")
                    inp = block.get("input", {})
                    pending[tool_id] = {
                        "type": "WebFetch",
                        "url": inp.get("url", ""),
                        "prompt": inp.get("prompt", ""),
                    }

                # Capture tool results
                if block.get("type") == "tool_result":
                    tool_id = block.get("tool_use_id", "")
                    if tool_id in pending:
                        result_content = block.get("content", "")
                        if isinstance(result_content, list):
                            result_text = "\n".join(
                                b.get("text", "") for b in result_content if isinstance(b, dict)
                            )
                        else:
                            result_text = str(result_content)

                        entry = pending[tool_id].copy()
                        entry["result"] = result_text
                        research.append(entry)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"  Warning: {e}", file=sys.stderr)
            continue

    return research, assistant_text


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for agent_id, info in AGENT_MAP.items():
        jsonl_path = os.path.join(TRANSCRIPT_DIR, f"{agent_id}.jsonl")
        if not os.path.exists(jsonl_path):
            print(f"SKIP {info['job']}: transcript not found")
            continue

        print(f"Extracting {info['job']} ({info['output']})...")
        research, reasoning = extract_research(jsonl_path)

        output = {
            "job_id": info["job"],
            "output_name": info["output"],
            "agent_id": agent_id,
            "search_count": len(research),
            "reasoning_blocks": len(reasoning),
            "searches": research,
            "reasoning": reasoning,
        }

        out_path = os.path.join(OUTPUT_DIR, f"{info['output']}.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)

        size_kb = os.path.getsize(out_path) / 1024
        print(f"  -> {len(research)} searches, {len(reasoning)} reasoning blocks, {size_kb:.1f}KB")

    print("\nDone. Extracted files in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
