from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .external_apis.nbu_currency import get_rates
from .models import CurrencyRate
from .serializers import CurrencyRateSerializer


class CurrencyRateListView(generics.ListAPIView):
    """
    API endpoint that allows currency rates to be viewed.
    """
    queryset = CurrencyRate.objects.all().order_by('-created_at')
    serializer_class = CurrencyRateSerializer


class UpdateCurrencyRateView(APIView):
    def get(self, request):
        get_rates() # for test
        return Response({"message": "Hello! The task API is working."})
