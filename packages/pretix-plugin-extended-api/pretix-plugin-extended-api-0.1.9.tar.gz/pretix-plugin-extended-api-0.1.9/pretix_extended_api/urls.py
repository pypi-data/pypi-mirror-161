from pretix.api.urls import event_router

from .views.orders import OrdersViewSet
from .views.tickets import TicketsViewSet
from .views.vouchers import VouchersViewSet

event_router.register("tickets", TicketsViewSet, basename="tickets")
event_router.register("extended-orders", OrdersViewSet, basename="extended-orders")
event_router.register(
    "extended-vouchers", VouchersViewSet, basename="extended-vouchers"
)
