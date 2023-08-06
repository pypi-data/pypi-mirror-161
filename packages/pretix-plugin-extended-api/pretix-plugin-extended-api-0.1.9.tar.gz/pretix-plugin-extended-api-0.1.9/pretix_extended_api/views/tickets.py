from django.db.models import Q
from django_scopes import scopes_disabled
from pretix.base.models import Order, OrderPosition
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import check_permission
from .serializers import (
    AttendeeHasTicketBodySerializer,
    AttendeeTicketBodySerializer,
    OrderPositionSerializer,
)


class TicketsViewSet(viewsets.ViewSet):
    # Disable scoping because we want to allow cross-organization checking
    # This allows us to do stuff like, you can attend PyCon Italia 2022
    # if you attended europython 2021
    @scopes_disabled()
    @action(url_path="attendee-has-ticket", detail=False, methods=["post"])
    def attendee_has_ticket(self, request, **kwargs):
        check_permission(request, "can_view_orders")

        serializer = AttendeeHasTicketBodySerializer(data=request.data)
        serializer.is_valid(True)

        attendee_email = serializer.data["attendee_email"]
        events = serializer.data["events"]

        if not events:
            return Response({"user_has_admission_ticket": False})

        qs = OrderPosition.objects.filter(
            attendee_email__iexact=attendee_email,
            order__status=Order.STATUS_PAID,
            item__admission=True,
        )

        events_filter = Q()
        for event in events:
            events_filter |= Q(
                order__event__slug=event["event_slug"],
                order__event__organizer__slug=event["organizer_slug"],
            )

        qs = qs.filter(events_filter)
        return Response({"user_has_admission_ticket": qs.exists()})

    @action(url_path="attendee-tickets", detail=False, methods=["get"])
    def attendee_tickets(self, request, *args, **kwargs):
        check_permission(request, "can_view_orders")

        serializer = AttendeeTicketBodySerializer(data=request.query_params)
        serializer.is_valid(True)

        attendee_email = serializer.data["attendee_email"]

        qs = OrderPosition.objects.filter(
            attendee_email__iexact=attendee_email,
            order__status=Order.STATUS_PAID,
            item__admission=True,
            order__event__slug=request.event.slug,
            order__event__organizer__slug=request.organizer.slug,
        )

        serializer = OrderPositionSerializer(
            instance=qs,
            many=True,
            context={
                "request": request,
                "event": request.event,
            },
        )
        return Response(serializer.data)
