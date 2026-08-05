def test_login_com_credenciais_corretas(client):
    from tests.conftest import TEST_PASSWORD, TEST_USERNAME

    response = client.post(
        "/auth/login", data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_com_senha_errada(client):
    from tests.conftest import TEST_USERNAME

    response = client.post(
        "/auth/login", data={"username": TEST_USERNAME, "password": "senha-errada"}
    )
    assert response.status_code == 401


def test_login_com_usuario_inexistente(client):
    response = client.post(
        "/auth/login", data={"username": "nao-existe", "password": "qualquer"}
    )
    assert response.status_code == 401


def test_token_invalido_e_rejeitado(client, usuario_payload):
    response = client.post(
        "/usuario",
        json=usuario_payload,
        headers={"Authorization": "Bearer token-invalido-qualquer"},
    )
    assert response.status_code == 401
