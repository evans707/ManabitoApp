import requests

API_URL = "http://localhost:8000/api/login/"  #

def test_login_success():
    payload = {
        "university_id": "23RD076",
        "password": "your_common_password"
    }

    response = requests.post(API_URL, json=payload)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "ログイン成功"

# まだLDAPサーバーが立ち上がっていないので、以下のテストはコメントアウトしておく
# def test_login_fail():
#     payload = {
#         "university_id": "invalid_user",
#         "password": "wrong_password"
#     }

#     response = requests.post(API_URL, json=payload)
#     assert response.status_code == 401
#     assert "error" in response.json()