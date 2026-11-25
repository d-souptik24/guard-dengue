"""
GuardDengue — API Integration Tests (FastAPI + TestClient)

Tests REST endpoints, SSE streaming responses, and static frontend serving.
"""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["corpus_release"] == "v0.1-dev"
        assert data["sqlite_storage"] is True
        assert data["qdrant_storage"] is True

@pytest.mark.asyncio
async def test_chat_endpoint_urgent_bypass():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Patient has severe abdominal pain, persistent vomiting, and bleeding gums",
            "language": "en"
        }
        res = await client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["route"] == "urgent"
        assert data["verdict"] == "template_bypass"
        assert data["telephony_action"] is not None
        assert data["telephony_action"]["number"] == "108"
        assert "EMERGENCY WARNING" in data["answer"]
        assert data["metrics"]["zone2_screener_ms"] > 0

@pytest.mark.asyncio
async def test_chat_endpoint_medication_bypass():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Can I take Combiflam for fever and headache?",
            "language": "en"
        }
        res = await client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["route"] == "medication"
        assert data["verdict"] == "template_bypass"
        assert "Combiflam" in data["answer"]
        assert "strictly contraindicated" in data["answer"].lower()

@pytest.mark.asyncio
async def test_chat_endpoint_education_rag():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "When should NS1 antigen and IgM tests be conducted for dengue diagnosis?",
            "language": "en"
        }
        res = await client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["route"] == "education"
        assert data["verdict"] == "pass"
        assert len(data["evidence"]) > 0
        assert data["evidence"][0]["metadata"]["source"] is not None
        assert "NS1" in data["answer"]

@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Severe vomiting and abdominal pain with dengue fever",
            "language": "en"
        }
        res = await client.post("/api/chat/stream", json=payload)
        assert res.status_code == 200
        assert "text/event-stream" in res.headers.get("content-type", "")
        body = res.text
        assert "event: screener_triage" in body
        assert "event: template_bypass" in body
        assert "event: answer_publish" in body

@pytest.mark.asyncio
async def test_static_frontend_serving():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert "GuardDengue" in res.text or "<!DOCTYPE html>" in res.text
