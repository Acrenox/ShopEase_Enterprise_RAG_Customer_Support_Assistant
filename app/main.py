from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version='1.0.0')
app.include_router(router, prefix=settings.api_prefix)


@app.get('/')
def root():
    return RedirectResponse(url='/docs', status_code=307)


@app.get('/health')
def health():
    return {'status': 'healthy', 'service': settings.app_name}
