from fastapi import Header, HTTPException

class AuthService:
    def __init__(self, secret: str):
        self.secret = secret

    async def require_user(self, authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        token = authorization.removeprefix("Bearer ").strip()
        if token != self.secret:
            raise HTTPException(status_code=403, detail="invalid token")
        return {"sub": "demo-user"}
