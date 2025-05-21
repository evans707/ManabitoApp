from django.http import JsonResponse
from accounts.models import User
from accounts.ldap_auth import authenticate_with_ldap
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POSTメソッドでリクエストしてください'}, status=405)

    data = json.loads(request.body)
    university_id = data.get('university_id')
    password = data.get('password')

    if not university_id or not password:
        return JsonResponse({'error': '学籍番号とパスワードが必要です'}, status=400)

    # LDAP認証を行うが、ここでは仮の認証を行う
    # authenticate_with_ldap(university_id, password) == Trueとして
    if True:
        user, created = User.objects.get_or_create(university_id=university_id)
        
        request.session['user_id'] = user.id
        return JsonResponse({'message': 'ログイン成功', 'created': created})
    else:
        return JsonResponse({'error': 'LDAP認証に失敗しました'}, status=401)