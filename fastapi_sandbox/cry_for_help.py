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


def get_actual_price(product_id: int, initial_price: float) -> float:
    return 666.740  # STUB


@app.get("/actual_price")
def actual_price(product_id: int, initial_price: float = 666.740, authorization: str = Header(default=None)):
    # If user does not have token or the token has expired -- let's make him login!
    if authorization is None:
        return RedirectResponse(idp.login_uri)
    assert authorization.startswith("Bearer ")
    token = authorization[len("Bearer "):]
    if not idp.token_is_valid(token):
        return RedirectResponse(idp.login_uri)

    return get_actual_price(product_id, initial_price)


def get_user_description(username: str) -> str:
    return "Blah blah blah"  # STUB


@app.get("/user_info")
def method_2(username: str = "woody_woodpecker", authorization: str = Header(default=None)):
    # If user does not have token or the token has expired -- let's make him login!
    if authorization is None:
        return RedirectResponse(idp.login_uri)
    assert authorization.startswith("Bearer ")
    token = authorization[len("Bearer "):]
    if not idp.token_is_valid(token):
        return RedirectResponse(idp.login_uri)

    return get_user_description(username)


@app.get("/callback")
def callback(session_state: str, code: str):
    auth_token = idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token
    # Our user will get here both from method_1 and from method_2
    # We should somehow determine, what method should be called -- and with what parameters.
    # How can we determine it?

    # Here we should call get_user_description(... ) or get_actual_price(...), according to which method was initially called


    # return auth_token


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8081)