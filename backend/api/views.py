from django.utils import timezone
from django.contrib.auth import login, logout as django_logout


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.permissions import IsAuthenticated

from accounts.models import User

class SampleAPIView(APIView):
    permission_classes = [IsAuthenticated] # 認証ガードを追加

    def get(self, request):
        return Response({"message": f"Hello, authenticated user {request.user.university_id}!"}, status=status.HTTP_200_OK)


class Login(APIView):
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def post(self, request):
        data = request.data
        university_id = data.get('university_id')
        password = data.get('password')

        if not university_id or not password:
            return Response({
                'success': False,
                'message': '学籍番号とパスワードが必要です'
            }, status=status.HTTP_400_BAD_REQUEST)

        # LDAP認証を行う (ここでは仮の認証成功としています)
        # ldap_authenticated = authenticate_with_ldap(university_id, password)
        # from accounts.ldap_auth import authenticate_with_ldap # 必要に応じてインポート
        ldap_authenticated = True

        if ldap_authenticated:
            try:
                user, created = User.objects.get_or_create(university_id=university_id)
                
                user.logined_at = timezone.now()
                user.save(update_fields=['logined_at'])

                # Djangoの認証システムにログインさせる
                login(request, user)

                return Response({
                    'success': True,
                    'user': {
                        'university_id': user.university_id,
                        'logined_at': user.logined_at,
                        'created': created,
                    },
                    'sessionid': request.session.session_key,
                    'message': 'ログインに成功しました'
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'サーバーエラーが発生しました。エラー内容: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'success': False,
                'message': '学籍番号またはパスワードが正しくありません。'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        content = {
            'message': 'Login endpoint. Please POST university_id and password.'
        }
        if request.user.is_authenticated:
            # Userモデルにuniversity_id属性があることを前提としています。なければ request.user.pk などを使用。
            content['status'] = f"You are already logged in as {request.user.university_id if hasattr(request.user, 'university_id') else request.user.pk}."
        else:
            content['status'] = "You are not logged in."
        return Response(content)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated] # ログアウトは認証済みユーザーのみ実行可能

    def post(self, request):
        django_logout(request)
        return Response({"message": "ログアウトしました。"}, status=status.HTTP_200_OK)

class AuthStatusView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                "isAuthenticated": True,
                "user": {
                    "university_id": request.user.university_id,
                    # 他に必要なユーザー情報があればここに追加
                }
            }, status=status.HTTP_200_OK)
        else:
            # 認証されていない場合は 401 Unauthorized を返す方がRESTful
            # return Response({"isAuthenticated": False}, status=status.HTTP_401_UNAUTHORIZED)
            # もしくは、成功として isAuthenticated: false を返す
            return Response({"isAuthenticated": False}, status=status.HTTP_200_OK)