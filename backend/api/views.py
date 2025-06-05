from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from accounts.models import User

class SampleAPIView(APIView):

    def get(self, request):
        return Response("OK", status=status.HTTP_200_OK)


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
        ldap_authenticated = True

        if ldap_authenticated:
            try:
                user, created = User.objects.get_or_create(university_id=university_id)
                
                user.logined_at = timezone.now()
                user.save(update_fields=['logined_at'])

                request.session['university_id'] = user.university_id # セッションにユーザーIDを保存
                
                return Response({
                    'success': True,
                    'user': {
                        'university_id': user.university_id,
                        'logined_at': user.logined_at,
                        'created': created,
                    },
                    'message': 'ログインに成功しました'
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'サーバーエラー: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'success': False,
                'message': 'LDAP認証に失敗しました'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        content = {
            'message': 'ログインエンドポイントです。学籍番号 (university_id) とパスワード (password) をPOSTしてください。'
        }
        return Response(content)