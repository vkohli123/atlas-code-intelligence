from fastapi import FastAPI, Depends
from app.auth import AuthService
from app.providers import ProviderRouter

app = FastAPI(title="Sample LLM Gateway")
auth = AuthService(secret="dev")
router = ProviderRouter(provider_order=["openai", "groq", "anthropic"])

@app.post("/v1/chat/completions")
async def chat(payload: dict, user=Depends(auth.require_user)):
    return await router.complete(payload)
