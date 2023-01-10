import uvicorn
from fastapi import FastAPI, Depends, Request, Header
from fastapi.responses import RedirectResponse
from fastapi_keycloak import FastAPIKeycloak, OIDCUser

app = FastAPI()
idp = FastAPIKeycloak(
    server_url="http://localhost:8085/auth",
    client_id="test-client",
    client_secret="GzgACcJzhzQ4j8kWhmhazt7WSdxDVUyE",
    admin_client_secret="BIcczGsZ6I8W5zf0rZg5qSexlloQLPKB",
    realm="Test",
    callback_uri="http://localhost:8081/callback"
)
idp.add_swagger_config(app)


@app.get("/")  # Unprotected
def root():
    return 'Hello World'


@app.get("/user")  # Requires logged in
def current_users(user: OIDCUser = Depends(idp.get_current_user())):
    return user


@app.get("/admin")  # Requires the admin role
def company_admin(user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"]))):
    return f'Hi admin {user}'


@app.get("/login")
def login_redirect():
    return RedirectResponse(idp.login_uri)


@app.get("/ask_to_login_1")
def ask_to_login_1(authorization: str = Header(default=None)):

    # Если у пользователя нет токена, или токен протух -- посылаем его логиниться.
    if authorization is None:
        return RedirectResponse(idp.login_uri)
    assert authorization.startswith("Bearer ")
    token = authorization[len("Bearer "):]
    if not idp.token_is_valid(token):
        return RedirectResponse(idp.login_uri)

    return "RESULT FROM METHOD 1"


@app.get("/ask_to_login_2")
def ask_to_login_2(authorization: str = Header(default=None)):

    # Если у пользователя нет токена, или токен протух -- посылаем его логиниться.
    if authorization is None:
        return RedirectResponse(idp.login_uri)
    assert authorization.startswith("Bearer ")
    token = authorization[len("Bearer "):]
    if not idp.token_is_valid(token):
        return RedirectResponse(idp.login_uri)

    return "RESULT FROM METHOD 2"


@app.get("/callback")
def callback(session_state: str, code: str):
    auth_token = idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token
    # Сюда пользователь будет прилетать из /ask_to_login_1 и /ask_to_login_2,
    # Но как мне понять, из какого метода сюда прилетел юзер, чтобы вернуть ему разный результат?

    return auth_token

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8081)