from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import exceptions

class BlackListCheckJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(
            raw_token
        )
        from apps.users.token_blacklist import BlacklistedToken
        if BlacklistedToken.objects.filter(jti=token["jti"]).exists():
            raise exceptions.AuthenticationFailed("Token has been blacklisted.")
        return token