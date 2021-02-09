from unittest import mock

import pytest
from model_bakery import baker
from indieweb.models import TToken


@pytest.fixture
def auth_token():
    return "58a51838067faa000320f5266238d673c5897f1d"


@pytest.fixture
def client_id():
    return "https://ownyourswarm.p3k.io"


@pytest.fixture
def m_micropub_scope():
    from indieweb.models import MMicropubScope

    return MMicropubScope.objects.all()


@pytest.fixture
def t_token(auth_token, client_id, m_micropub_scope):
    t_token = baker.make("indieweb.TToken", auth_token=auth_token, client_id=client_id)
    t_token.micropub_scope.set([m_micropub_scope[0], m_micropub_scope[1]])
    return t_token


@pytest.fixture
def t_token_access(auth_token, client_id, m_micropub_scope):
    t_token = baker.make("indieweb.TToken", key=auth_token, client_id=client_id)
    t_token.micropub_scope.set([m_micropub_scope[0], m_micropub_scope[1]])
    return t_token


@pytest.mark.django_db
class TestIndieAuthExchangeToken:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/token"

    @pytest.fixture
    def post_data(self, auth_token, client_id):
        return {
            "grant_type": "authorization_code",
            "me": "https://b6260560dd45.ngrok.io/",
            "code": auth_token,
            "redirect_uri": "https://ownyourswarm.p3k.io/auth/callback",
            "client_id": client_id,
        }

    @pytest.fixture
    def ninka_mock(self, monkeypatch):
        from ninka.indieauth import discoverAuthEndpoints

        m = mock.Mock(discoverAuthEndpoints, autospec=True)
        monkeypatch.setattr("indieweb.serializers.discoverAuthEndpoints", m)
        return m

    def test_valid(self, target, client, ninka_mock, post_data, t_token):
        ninka_mock.return_value = {"redirect_uri": [post_data["redirect_uri"]]}
        response = client.post(target, data=post_data)

        assert response.status_code == 200

        data = response.json()

        assert data["me"] == post_data["me"]
        assert len(data["access_token"]) == 40
        assert data["scope"] == "create update"

        t_token.refresh_from_db()
        assert t_token.auth_token == ""
        assert t_token.key == data["access_token"]

    def test_used_token_invalid(self, target, client, ninka_mock, post_data):
        ninka_mock.return_value = {"redirect_uri": [post_data["redirect_uri"]]}
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert response.json() == {"non_field_errors": ["Token not found"]}
        assert not ninka_mock.called

    def test_error_if_redirect_doesnt_match(
        self, target, client, ninka_mock, post_data, t_token
    ):
        post_data["redirect_uri"] = "http://local.test"
        ninka_mock.return_value = {"redirect_uri": []}
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["Redirect uri not found on client app"]
        }

        ninka_mock.assert_called_with(post_data["client_id"])


@pytest.mark.django_db
class TestVerifyIndieAuthToken:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/token"

    def test_valid(self, target, client, t_token_access, auth_token, client_id):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.get(target)
        assert response.status_code == 200
        assert response.json() == {
            "me": f"/author/{t_token_access.user.username}/",
            "client_id": client_id,
            "scope": "create update",
        }

    def test_valid(self, target, client, t_token_access, auth_token, client_id):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.get(target)
        assert response.status_code == 200
        assert response.json() == {
            "me": f"/author/{t_token_access.user.username}/",
            "client_id": client_id,
            "scope": "create update",
        }

    def test_no_header(self, target, client):
        response = client.get(target)
        assert response.status_code == 400
        assert response.json() == {
            "message": "Invalid token header. No credentials provided."
        }

    def test_no_token_found(self, target, client):
        client.credentials(HTTP_AUTHORIZATION="Bearer hogehoge")
        response = client.get(target)
        assert response.status_code == 400
        assert response.json() == {"token": ["Token not found."]}


@pytest.mark.django_db
class TestIndieAuthTokenRevoke:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/token"

    @pytest.fixture
    def post_data(self, auth_token, client_id):
        return {
            "action": "revoke",
            "token": auth_token,
        }

    @pytest.fixture
    def ninka_mock(self, monkeypatch):
        from ninka.indieauth import discoverAuthEndpoints

        m = mock.Mock(discoverAuthEndpoints, autospec=True)
        monkeypatch.setattr("indieweb.serializers.discoverAuthEndpoints", m)
        return m

    def test_valid(
        self, target, client, ninka_mock, post_data, t_token_access, auth_token
    ):
        assert TToken.objects.filter(key=auth_token).exists() is True
        response = client.post(target, data=post_data)
        assert response.status_code == 200
        assert TToken.objects.filter(key=auth_token).exists() is False

    def test_requires_revoke(
        self, target, client, ninka_mock, post_data, t_token_access, auth_token
    ):
        post_data["action"] = "hoge"
        assert TToken.objects.filter(key=auth_token).exists() is True
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert TToken.objects.filter(key=auth_token).exists() is True
