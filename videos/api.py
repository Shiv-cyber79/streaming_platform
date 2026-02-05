from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class PlaylistAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "JWT access token is working in real time"
        })
