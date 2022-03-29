from fastapi import FastAPI
from order_routes import order_router
from auth_routes import auth_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
import inspect, re
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Pizza Delivery API",
        version="1.0.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    cookie_security_schemes = {
        "AuthJWTCookieAccess": {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-TOKEN"
        },
        "AuthJWTCookieRefresh": {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-TOKEN"
        }
    }
    refresh_token_cookie = {
        "name": "refresh_token_cookie",
        "in": "cookie",
        "required": False,
        "schema": {
            "title": "refresh_token_cookie",
            "type": "string"
        }
    }
    access_token_cookie = {
        "name": "access_token_cookie",
        "in": "cookie",
        "required": False,
        "schema": {
            "title": "access_token_cookie",
            "type": "string"
        }
    }

    if "components" in openapi_schema:
        openapi_schema["components"].update({"securitySchemes": cookie_security_schemes})
    else:
        openapi_schema["components"] = {"securitySchemes": cookie_security_schemes}

    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route,"endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required",inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required",inspect.getsource(endpoint)) or
                re.search("jwt_optional",inspect.getsource(endpoint))
            ):
                try:
                    openapi_schema["paths"][path][method]['parameters'].append(access_token_cookie)
                except Exception:
                    openapi_schema["paths"][path][method].update({"parameters":[access_token_cookie]})

                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != "get":
                    openapi_schema["paths"][path][method].update({
                        'security': [{"AuthJWTCookieAccess": []}]
                    })

            # refresh_token
            if re.search("jwt_refresh_token_required",inspect.getsource(endpoint)):
                try:
                    openapi_schema["paths"][path][method]['parameters'].append(refresh_token_cookie)
                except Exception:
                    openapi_schema["paths"][path][method].update({"parameters":[refresh_token_cookie]})

                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != "get":
                    openapi_schema["paths"][path][method].update({
                        'security': [{"AuthJWTCookieRefresh": []}]
                    })

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_router)
app.include_router(order_router)
