# django
from django.utils import timezone
from django.contrib.auth import login, logout as django_logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache


# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

# local
from accounts.models import User
from scraping.services import scrape_moodle, scrape_webclass
from scraping.serializers import AssignmentSerializer
from scraping.models import Assignment


# 認証されたユーザーに対してメッセージを返すサンプルAPI
class SampleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello, authenticated user {request.user.university_id}!"}, status=status.HTTP_200_OK)

# Login API
class Login(APIView):
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def post(self, request):
        data = request.data
        university_id_from_request = data.get('university_id')
        password = data.get('password')

        # 大文字の学籍番号を使用するために変換
        university_id = university_id_from_request.upper() if university_id_from_request else None

        if not university_id or not password:
            return Response({
                'success': False,
                'message': '学籍番号とパスワードが必要です'
            }, status=status.HTTP_400_BAD_REQUEST)

        # LDAP認証を行う (ここでは仮の認証成功としています)
        # ldap_authenticated = authenticate_with_ldap(university_id, password)
        ldap_authenticated = True

        if ldap_authenticated:
            try:
                user, created = User.objects.get_or_create(university_id=university_id)
                
                user.logined_at = timezone.now()
                user.save(update_fields=['logined_at'])

                # Djangoの認証システムにログインさせる
                login(request, user)

                # スクレイピングを実行
                scrape_webclass(user, password)
                scrape_moodle(user, password)  

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
                    'message': f'サーバーエラーが発生しました。'
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

# Logout API
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        django_logout(request)
        return Response({"message": "ログアウトしました。"}, status=status.HTTP_200_OK)

# AuthStatus API
class AuthStatusView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                "isAuthenticated": True,
                "user": {
                    "university_id": request.user.university_id,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"isAuthenticated": False}, status=status.HTTP_200_OK)
        

# CSRF Cookie API
@method_decorator(never_cache, name='get')
@method_decorator(ensure_csrf_cookie, name='get')
class CsrfTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set."})
    

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)