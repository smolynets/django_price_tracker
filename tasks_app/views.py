from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PingSerializer

class PingView(APIView):
    def get(self, request):
        return Response({"message": "Hello! The task API is working."})

    def post(self, request):
        
        # Using serializer to format the response
        serializer = PingSerializer(data={
            "status": "working"
        })
        serializer.is_valid()
        return Response(serializer.data)
