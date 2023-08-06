from django.db.models import F, Q
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.response import Response

from .permissions import check_permission
from .serializers import ExtendedVoucherSerializer


class VouchersViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk: str, **kwargs):
        check_permission(request, "can_view_vouchers")
        voucher = (
            self.request.event.vouchers.select_related("seat")
            .filter(
                Q(valid_until__isnull=True) | Q(valid_until__gt=now()),
                code=pk,
                redeemed__lt=F("max_usages"),
            )
            .first()
        )

        if not voucher:
            return Response(status=404)

        return Response(ExtendedVoucherSerializer(voucher).data)
