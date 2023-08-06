from pretix.base.models import TeamAPIToken
from rest_framework import exceptions


def check_permission(request, permission):
    # Only allow Team API tokens to call this API.
    perm_holder = request.auth if isinstance(request.auth, TeamAPIToken) else None
    if not perm_holder or not perm_holder.has_event_permission(
        request.event.organizer, request.event, permission
    ):
        raise exceptions.PermissionDenied()
