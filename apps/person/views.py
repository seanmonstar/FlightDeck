import commonware.log
import waffle

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django import http

from django.core.mail import mail_admins

from amo.authentication import  AMOAuthentication
from amo.helpers import AMOOAuth

from django_browserid import auth as browserid_auth
from person.models import Profile

log = commonware.log.getLogger('f.profile.views')

def public_profile(r, username):
    """
    Public profile
    """
    page = "profile"
    try:
        profile = Profile.objects.get_user_by_username_or_nick(username)
    except ObjectDoesNotExist:
        raise Http404
    person = profile.user
    addons = person.packages_originated.addons().active()
    libraries = person.packages_originated.libraries().active()
    # if owner of the profile and not specially wanted to see it - redirect
    # to dashboard
    return render_to_response("profile.html", {
        'page': page,
        'person': person,
        'profile': profile,
        'addons': addons,
        'libraries': libraries
    }, context_instance=RequestContext(r))


def get_packages(person):
    addons = person.packages_originated.addons().active()
    libraries = person.packages_originated.libraries().active()
    disabled_addons = person.packages_originated.disabled().filter(type='a')
    disabled_libraries = person.packages_originated.disabled().filter(type='l')
    return addons, libraries, disabled_addons, disabled_libraries


@login_required
def dashboard(r):
    """
    Dashboard of the user
    """
    page = "dashboard"
    person = r.user
    (addons, libraries,
     disabled_addons, disabled_libraries) = get_packages(person)
    return render_to_response("user_dashboard.html", {
        'page': page,
        'person': person,
        'addons': addons,
        'libraries': libraries,
        'disabled_addons': disabled_addons,
        'disabled_libraries': disabled_libraries
    }, context_instance=RequestContext(r))


@login_required
def dashboard_browser(r, page_number=1, type=None, disabled=False):
    """
    Display a list of addons or libraries with pages
    Filter based on the request (type, username).
    """

    author = r.user
    packages = author.packages_originated.disabled() \
            if disabled else author.packages_originated.active()

    if type:
        other_type = 'l' if type == 'a' else 'a'
        other_packages_number = len(packages.filter(type=other_type))
        packages = packages.filter(type=type)
        template_suffix = settings.PACKAGE_PLURAL_NAMES[type]

    limit = r.GET.get('limit', settings.PACKAGES_PER_PAGE)

    pager = Paginator(
        packages,
        per_page=limit,
        orphans=1
    ).page(page_number)

    (addons, libraries, disabled_addons,
     disabled_libraries) = get_packages(author)

    return render_to_response(
        'user_%s.html' % template_suffix, {
            'pager': pager,
            'author': author,
            'addons': addons,
            'disabled': disabled,
            'libraries': libraries,
            'disabled_addons': disabled_addons,
            'disabled_libraries': disabled_libraries,
            'other_packages_number': other_packages_number,
            'other_type': other_type
        }, context_instance=RequestContext(r))

def browserid_authenticate(request, assertion):
    """
    Verify a BrowserID login attempt. If the BrowserID assertion is
    good, but no account exists on flightdeck, create one.
    """
    backend = browserid_auth.BrowserIDBackend()

    result = backend.verify(assertion, settings.SITE_URL)
    if not result:
        return (None, None)

    id = None
    email = result.get('email')
    if not email:
        log.error('[browserID] Assertion did not return an email')
        return (None, None)

    try:
        amouser = AMOAuthentication.auth_browserid_authenticate(email)
    except ValueError, err:
        # Some issue with connecting to AMO let's not raise an error
        mail_admins( 'Problem with browserID authentication', str(err))
        log.error("[browserID] Error from AMO error is emailed")
    except Http404, err:
        # AMO responded with 404 - email doesn't exist on AMO side
        log.error("[browserID] 404 Error from AMO: %s" % email)
        return (None, None)
    else:
        if not amouser or 'id' not in amouser:
            mail_admins('AMO user API returned no data',
                    'It supposed to raise 404')
            return (None, None)
        id = amouser['id']
    if id:
        try:
            user = User.objects.get(username=id)
        except User.DoesNotExist:
            # user exists on AMO, but not on Builder - create user
            user = User.objects.create(username=id, email=email)
            profile = Profile.objects.create(user=user)
        except Exception:
            # we should raise or treat somehow multiple users with the same
            # username
            raise
        else:
            try:
                profile = user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)
    else:
        # this now happens only for ValueError (probably never)
        # XXX: actually every time for -dev
        # mail_admins('No id returned from AMO', 'Just a flag this code is used')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # we can't create a new user as there is no connection to AMO
            # TODO give a better response
            raise
        except Exception:
            # we should raise or treat somehow multiple users with the same
            # email
            raise
        else:
            try:
                profile = user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)

    profile.user.backend = 'django_browserid.auth.BrowserIDBackend'
    if id:
        profile.update_from_AMO(amouser)

    return (profile, None)


def browserid_login(request):
    """
    If browserID is enabled, then try to authenticate with the assertion
    """
    if waffle.switch_is_active('browserid-login'):
        if request.user.is_authenticated():
            return http.HttpResponse(status=200)

        profile, msg = browserid_authenticate(
            request,
            assertion=request.POST['assertion'])

        if profile is not None:
            auth.login(request, profile.user)
            return http.HttpResponse(status=200)

        return http.HttpResponse(status=401)
    else:
        return http.HttpResponse(status=403)
