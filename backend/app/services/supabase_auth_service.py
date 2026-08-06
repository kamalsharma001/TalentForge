"""
SupabaseAuthService — verifies Supabase Auth session tokens.

Supabase Auth (used here purely for the "Continue with Google" handshake)
issues its own JWT after a successful Google OAuth login. This service
verifies that token's signature/expiry and extracts the verified identity
(email, name, avatar) — it does NOT decide roles or authorization; that
remains entirely in AuthService / User.role, unchanged.

Verification strategy
----------------------
Supabase now signs Auth tokens asymmetrically (ES256, or RS256 on older
projects) by default for new projects — there is no shared secret to
configure. Instead we verify against the project's public signing keys,
published at:

    {SUPABASE_URL}/auth/v1/.well-known/jwks.json

This is Supabase's currently recommended verification approach for
backends that want to avoid a network round-trip to /auth/v1/user on
every request: PyJWT's PyJWKClient fetches and caches the public keys
(keyed by `kid`), and transparently re-fetches if it sees a `kid` it
doesn't recognize yet (e.g. after Supabase rotates keys).
"""

import jwt
from jwt import PyJWKClient
from app.config import get_config
from app.utils.errors import AuthenticationError

# One PyJWKClient per Supabase project URL, reused across requests so the
# public keys are cached in memory instead of re-fetched every call.
_jwk_client_cache: dict[str, PyJWKClient] = {}


class SupabaseAuthService:

    @staticmethod
    def _get_jwk_client() -> PyJWKClient:
        cfg = get_config()
        supabase_url = (cfg.SUPABASE_URL or "").rstrip("/")
        if not supabase_url:
            raise AuthenticationError("Google sign-in is not configured.")

        client = _jwk_client_cache.get(supabase_url)
        if client is None:
            jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
            client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
            _jwk_client_cache[supabase_url] = client

        return client

    @staticmethod
    def verify_access_token(token: str) -> dict:
        """
        Verify a Supabase-issued access token against the project's
        public JWKS and return its claims.

        Raises AuthenticationError if the token is missing, malformed,
        expired, or signed by a key that isn't in the project's key set.
        """
        if not token:
            raise AuthenticationError("Missing Supabase access token.")

        audience = current_app.config.get("SUPABASE_JWT_AUDIENCE", "authenticated")

        try:
            jwk_client = SupabaseAuthService._get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                audience=audience,
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Google sign-in session has expired. Please try again.")
        except (jwt.PyJWKClientError, jwt.InvalidTokenError) as exc:
            current_app.logger.warning("Supabase token verification failed: %s", exc)
            raise AuthenticationError("Invalid Google sign-in session.")

        email = claims.get("email")
        if not email:
            raise AuthenticationError("Google account has no verified email address.")

        return claims

    @staticmethod
    def extract_profile(claims: dict) -> dict:
        """Pull a best-effort name/avatar out of the Google identity claims."""
        metadata = claims.get("user_metadata") or {}

        full_name = metadata.get("full_name") or metadata.get("name") or ""
        first_name, _, last_name = full_name.partition(" ")

        return {
            "email": claims["email"],
            "first_name": first_name or metadata.get("given_name") or "",
            "last_name": last_name or metadata.get("family_name") or "",
            "avatar_url": metadata.get("avatar_url") or metadata.get("picture") or None,
        }