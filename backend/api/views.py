from django.http import JsonResponse
from accounts.models import User
from accounts.ldap_auth import authenticate_with_ldap
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json


class SampleAPIView(APIView):

    def get(self, request):
        return Response("OK", status=status.HTTP_200_OK)


class Login(APIView):
    
    def post(self, request):
        data = request.data
        university_id = data.get('university_id')
        password = data.get('password')

        if not university_id or not password:
            return Response({'error': '学籍番号とパスワードが必要です'}, status=status.HTTP_400_BAD_REQUEST)

        # LDAP認証を行うが、ここでは仮の認証を行う
        # authenticate_with_ldap(university_id, password) == Trueとして
        if True:
            user, created = User.objects.get_or_create(university_id=university_id)
            
            request.session['user_id'] = user.id
            return Response({'message': 'ログイン成功', 'created': created})
        else:
            return Response({'error': 'LDAP認証に失敗しました'}, status=status.HTTP_401_UNAUTHORIZED)