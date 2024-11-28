from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import time

from users.views import getRolesAndFormApi
from django.contrib.auth.models import User, Group


try:
    from urllib.parse import urlencode
except ImportError:
    # Python < 3
    from urllib import urlencode

try:
    from django.utils.http import url_has_allowed_host_and_scheme                                                                                                                                                 
except ImportError:                                                                                                                                                                                               
    from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme 

try:
    from urllib.parse import quote
except ImportError:
    from urllib import pathname2url as quote

import django
from django.core.exceptions import SuspiciousOperation
try:
    from django.urls import reverse
except ImportError:
    # Django < 2.0.0
    from django.core.urlresolvers import reverse
from django.contrib import auth
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.utils.module_loading import import_string
from django.views.generic import View
from django.contrib.auth.backends import BaseBackend

from mozilla_django_oidc.utils import (
    absolutify,
    import_from_settings,
    is_authenticated
)
from mozilla_django_oidc.views import OIDCAuthenticationCallbackView


class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    @property
    def failure_url(self):
        
        return import_from_settings('LOGIN_REDIRECT_URL_FAILURE', '/')


    def login_failure(self):
        return HttpResponseRedirect(self.failure_url)


    @property
    def success_url(self):
        # Pull the next url from the session or settings--we don't need to
        # sanitize here because it should already have been sanitized.
        # role = getRolesAndFormApi(username=self.user)
        # print(role)
        return import_from_settings('LOGIN_REDIRECT_URL', '/')

def get_next_url(request, redirect_field_name):
    """Retrieves next url from request

    Note: This verifies that the url is safe before returning it. If the url
    is not safe, this returns None.

    :arg HttpRequest request: the http request
    :arg str redirect_field_name: the name of the field holding the next url

    :returns: safe url or None

    """
    next_url = request.GET.get(redirect_field_name)
    if next_url:
        kwargs = {
            'url': next_url,
            'allowed_hosts': request.get_host()
        }
        # NOTE(willkg): Django 1.11+ allows us to require https, too.
        if django.VERSION >= (1, 11):
            kwargs['require_https'] = request.is_secure()
        is_safe = url_has_allowed_host_and_scheme(**kwargs)
        if is_safe:
            return next_url
    return None

class NdeOIDC(OIDCAuthenticationBackend):


    def create_user(self, claims):                                                                                                                                                           
        """Return object for a newly created user account."""                                                                                                                                
        email = claims.get("email")                                                                                                                                                          
        username = claims.get("preferred_username")                                                                                                                                                
        first_name = claims.get("given_name")    
        new_user = self.UserModel.objects.create_user(username, email=email, first_name=first_name)
        # #  Cek 
        role = getRolesAndFormApi(username=username)
        # if role:
        #     print('Role data found')
        #     try:
        #         group = Group.objects.get(name='ukpbj')
        #     except Group.DoesNotExist:

        #         group = Group.objects.create(name='ukpbj')
        #         print('Group "ukpbjs" created')
        #     new_user.groups.add(group)
        #     new_user.save()                                                             # 
        return new_user

    def filter_users_by_claims(self, claim):
        username = claim.get('preferred_username')
        if not username:
            return self.UserModel.objects.none()

        return self.UserModel.objects.filter(username=username)
    
    def authenticate(self, **kwargs):
        """Authenticates a user based on the OIDC code flow."""

        self.request = kwargs.pop('request', None)
        if not self.request:
            return None

        state = self.request.GET.get('state')
        code = self.request.GET.get('code')
        nonce = kwargs.pop('nonce', None)

        if not code or not state:
            return None

        reverse_url = import_from_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                           'oidc_authentication_callback')
        # print(self.request.scheme)
        # scheme = self.request.scheme
        # host = self.request.get_host()
        # full_url = f"{scheme}://{host}{reverse_url}"
        token_payload = {
            'client_id': self.OIDC_RP_CLIENT_ID,
            'client_secret': self.OIDC_RP_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri':  reverse_url ,
        }

        # Get the token
        token_info = self.get_token(token_payload)
        id_token = token_info.get('id_token')
        access_token = token_info.get('access_token')

        # Validate the token
        verified_id = self.verify_token(id_token, nonce=nonce)

        print(verified_id)

        if verified_id:
            return self.get_or_create_user(access_token, id_token, verified_id)


def provider_logout(request):
    from django.conf import settings
    logout_url = quote(settings.LOGOUT_REDIRECT_URL)
    redirect_url = settings.OIDC_BASE_URL + '/protocol/openid-connect/logout?redirect_uri=' + logout_url
    return redirect_url

class OIDCAuthenticationCallbackView(CustomOIDCAuthenticationCallbackView):
    def get(self, request):
        """Callback handler for OIDC authorization code flow"""

        nonce = request.session.get('oidc_nonce')
        if nonce:
            # Make sure that nonce is not used twice
            del request.session['oidc_nonce']

        if request.GET.get('error'):
            # Ouch! Something important failed.
            # Make sure the user doesn't get to continue to be logged in
            # otherwise the refresh middleware will force the user to
            # redirect to authorize again if the session refresh has
            # expired.
            if is_authenticated(request.user):
                auth.logout(request)
            assert not is_authenticated(request.user)
        elif 'code' in request.GET and 'state' in request.GET:
            kwargs = {
                'request': request,
                'nonce': nonce,
            }

            if 'oidc_state' not in request.session:
                return self.login_failure()

            if request.GET['state'] != request.session['oidc_state']:
                msg = 'Session `oidc_state` does not match the OIDC callback state'
                raise SuspiciousOperation(msg)

            authbackend = NdeOIDC()

            self.user = authbackend.authenticate(**kwargs)


            if self.user and self.user.is_active:
                auth.login(request, self.user, backend="django.contrib.auth.backends.ModelBackend")
                print(request.user.is_authenticated)
                return HttpResponseRedirect(self.success_url)
        return self.login_failure()
    
class OIDCAuthenticationRequestView(View):
    """OIDC client authentication HTTP endpoint"""

    http_method_names = ['get']

    def __init__(self, *args, **kwargs):
        super(OIDCAuthenticationRequestView, self).__init__(*args, **kwargs)

        self.OIDC_OP_AUTH_ENDPOINT = import_from_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
        self.OIDC_RP_CLIENT_ID = import_from_settings('OIDC_RP_CLIENT_ID')

    def get(self, request):
        """OIDC client authentication initialization HTTP endpoint"""
        state = get_random_string(import_from_settings('OIDC_STATE_SIZE', 32))
        redirect_field_name = import_from_settings('OIDC_REDIRECT_FIELD_NAME', 'next')
        reverse_url = import_from_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                           'oidc_authentication_callback')
        # print(request.scheme)
        # scheme = request.scheme
        # host = request.get_host()
        # full_url = f"{scheme}://{host}{import_from_settings("OIDC_REDIRECT_URL")}"
        params = {
            'response_type': 'code',
            'scope': import_from_settings('OIDC_RP_SCOPES', 'openid email'),
            'client_id': self.OIDC_RP_CLIENT_ID,
            'redirect_uri': import_from_settings("OIDC_REDIRECT_URL"),
            'state': state,
        }
        print(params)

        params.update(self.get_extra_params(request))

        if import_from_settings('OIDC_USE_NONCE', True):
            nonce = get_random_string(import_from_settings('OIDC_NONCE_SIZE', 32))
            params.update({
                'nonce': nonce
            })
            request.session['oidc_nonce'] = nonce

        request.session['oidc_state'] = state
        request.session['oidc_login_next'] = get_next_url(request, redirect_field_name)

        query = urlencode(params)
        redirect_url = '{url}?{query}'.format(url=self.OIDC_OP_AUTH_ENDPOINT, query=query)
        return HttpResponseRedirect(redirect_url)

    def get_extra_params(self, request):
        return import_from_settings('OIDC_AUTH_REQUEST_EXTRA_PARAMS', {})
    
class OIDCLogoutView(View):
    """Logout helper view"""
    http_method_names = ['get']
    def get(self, request):
        """Log out the user."""
        from django.conf import settings
        logout_url = quote(settings.LOGOUT_REDIRECT_URL)
        redirect_url = settings.OIDC_BASE_URL + '/protocol/openid-connect/logout?redirect_uri=' + logout_url

        if is_authenticated(request.user):
            auth.logout(request)

        return HttpResponseRedirect(redirect_url)
