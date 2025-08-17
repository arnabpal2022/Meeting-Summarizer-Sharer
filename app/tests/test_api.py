# tests/test_api.py
def test_transcript_to_summary_flow(client):
    tx = {
        "title": "Weekly Sync",
        "text": "Attendees: Alice, Bob.\n\nWe discussed Q3 goals. Alice will lead the hiring plan. Bob to draft API spec by Friday.\nRisks: tight timeline.",
    }
    r = client.post("/api/transcripts", json=tx)
    assert r.status_code == 200, r.text
    transcript_id = r.json()["id"]

    sm_req = {"transcript_id": transcript_id, "instruction": "Highlight only action items and owners"}
    r2 = client.post("/api/summaries", json=sm_req)
    assert r2.status_code == 200, r2.text
    summary_id = r2.json()["id"]
    assert "MOCK SUMMARY" in r2.json()["content"]

    u = client.patch(f"/api/summaries/{summary_id}", json={"content": "Edited summary"})
    assert u.status_code == 200
    assert u.json()["content"] == "Edited summary"
