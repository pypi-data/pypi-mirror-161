from typing import List, Optional

from fastapi import Depends
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError

from fa_common import (
    AuthType,
    ForbiddenError,
    InternalServerError,
    UnauthorizedError,
    async_get,
    force_async,
    get_settings,
)
from fa_common import logger as LOG

from .models import AuthUser

oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        implicit={
            "authorizationUrl": get_settings().OAUTH2_AUTH_URL,
            "scopes": {"openid": "", "profile": "", "email": ""},
        }
    )
)


async def get_firebase_token(user: AuthUser) -> str:
    from firebase_admin import auth as fire_auth

    uid = user.sub

    # Potentially add scopes here
    # additional_claims = {
    #     "premiumAccount": True
    # }
    additional_claims: dict = {}
    return await force_async(fire_auth.create_custom_token)(uid, additional_claims)


async def get_user_profile(url: str, auth: str) -> AuthUser:
    data = await async_get(url, auth, json_only=True)
    return AuthUser(**data)


def get_token_auth_header(auth: str) -> str:
    """Obtains the Access Token from the Authorization Header"""
    if not auth:
        raise UnauthorizedError(
            detail="Authorization header is expected",
        )

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise UnauthorizedError(
            detail="Authorization header must start with Bearer",
        )
    elif len(parts) == 1:
        raise UnauthorizedError(
            detail="Token not found",
        )
    elif len(parts) > 2:
        raise UnauthorizedError(
            detail="Authorization header must be Bearer token",
        )

    token = parts[1]
    return token


async def decode_token(auth: str):
    settings = get_settings()
    token = get_token_auth_header(auth)
    jwks = await async_get(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json", json_only=True)

    unverified_header = jwt.get_unverified_header(token)
    rsa_key: dict = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=settings.JWT_ALGORITHMS,
                audience=settings.API_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )

        except jwt.ExpiredSignatureError as e:
            raise UnauthorizedError(
                detail="token is expired",
            ) from e
        except jwt.JWTClaimsError as e:
            raise UnauthorizedError(
                detail="incorrect claims, please check the audience and issuer",
            ) from e
        except Exception as e:
            raise UnauthorizedError(
                detail="Unable to parse authentication token.",
            ) from e

        return payload

    raise UnauthorizedError(
        detail="Unable to find appropriate key",
    )


async def get_user(payload: dict, token: str, get_profile: bool = True) -> Optional[AuthUser]:
    settings = get_settings()
    user: Optional[AuthUser] = None
    token_scopes: List[str] = []
    roles: List[str] = []

    if "permissions" in payload and payload.get("permissions") is not None:
        token_scopes = payload["permissions"]

    if settings.ROLES_NAMESPACE in payload and payload.get(settings.ROLES_NAMESPACE) is not None:
        roles = payload[settings.ROLES_NAMESPACE]

    if "sub" in payload:
        if get_profile and "aud" in payload and len(payload["aud"]) > 1 and "userinfo" in payload["aud"][1]:
            try:
                user = await get_user_profile(payload["aud"][1], token)
            except Exception as err:
                LOG.warning(
                    "Something went wrong retieving user profile falling back to creating user from "
                    + f"the payload. Error: {err}"
                )
                user = AuthUser(**payload)
        else:
            user = AuthUser(**payload)

        if len(token_scopes) > 0:
            user.scopes = token_scopes

        if len(roles) > 0:
            user.roles = roles

    return user


async def get_standalone_user() -> AuthUser:
    """
    Manage user authentication and identity management using a
    standalone licence (instead of OAuth2).

    To use simply change your import for get_current_user():

        if get_settings().AUTH_TYPE is AuthType.STANDALONE:
            from fa_common.auth import get_standalone_user as get_current_user
        else:
            from fa_common.auth import get_current_user

    returns:
        user (AuthUser): The standalone instance user

    raises:
        InternalServerError
    """
    settings = get_settings()
    if settings.AUTH_TYPE is not AuthType.STANDALONE:
        LOG.error(f"AUTH_TYPE must be STANDALONE not {settings.AUTH_TYPE}")
        raise InternalServerError(
            detail="Standalone authentication not enabled",
        )

    return AuthUser(sub="standalone", name="Default User", scopes=["read:me"])


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    get_profile: bool = None,
) -> AuthUser:
    settings = get_settings()
    if get_profile is None:
        get_profile = settings.USE_AUTH0_PROFILE
    try:
        payload = await decode_token(token)
        user = await get_user(payload, token, get_profile)

    except (JWTError, ValidationError) as e:
        LOG.error("Could not validate credentials. {}", str(e))
        raise UnauthorizedError(
            detail="Could not validate credentials.",
        ) from e

    if not user:
        raise UnauthorizedError(
            detail="Invalid authentication credentials.",
        )

    if settings.ENABLE_SCOPES:
        for scope in security_scopes.scopes:
            if scope not in user.scopes and scope not in user.roles:
                raise ForbiddenError(
                    detail="Not enough permissions",
                )
    return user


async def get_auth_simple(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> AuthUser:
    return await get_current_user(security_scopes, token, False)
