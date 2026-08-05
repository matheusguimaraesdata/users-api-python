def test_criar_usuario(auth_client, usuario_payload):
    response = auth_client.post("/usuario", json=usuario_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Usuário de Teste"
    assert data["conta"]["numero"] == "00099-9"
    assert data["id"] is not None


def test_criar_usuario_sem_token_retorna_401(client, usuario_payload):
    response = client.post("/usuario", json=usuario_payload)
    assert response.status_code == 401


def test_listar_usuarios_vazio(client):
    response = client.get("/usuario")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_usuarios_apos_criar(auth_client, usuario_payload):
    auth_client.post("/usuario", json=usuario_payload)
    auth_client.post("/usuario", json=usuario_payload)

    response = auth_client.get("/usuario")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_obter_usuario_por_id(auth_client, usuario_payload):
    criado = auth_client.post("/usuario", json=usuario_payload).json()

    response = auth_client.get(f"/usuario/{criado['id']}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Usuário de Teste"


def test_obter_usuario_inexistente_retorna_404(client):
    response = client.get("/usuario/9999")
    assert response.status_code == 404


def test_patch_atualiza_apenas_campo_enviado(auth_client, usuario_payload):
    criado = auth_client.post("/usuario", json=usuario_payload).json()

    response = auth_client.patch(f"/usuario/{criado['id']}", json={"nome": "Nome Atualizado"})
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Nome Atualizado"
    # os demais campos não devem ter sido afetados
    assert data["conta"]["numero"] == "00099-9"


def test_patch_sem_token_retorna_401(client, auth_client, usuario_payload):
    criado = auth_client.post("/usuario", json=usuario_payload).json()

    # client "puro" não tem o header Authorization
    response = client.patch(f"/usuario/{criado['id']}", json={"nome": "Não importa"})
    assert response.status_code == 401


def test_patch_usuario_inexistente_retorna_404(auth_client):
    response = auth_client.patch("/usuario/9999", json={"nome": "Não importa"})
    assert response.status_code == 404


def test_put_substitui_usuario_completo(auth_client, usuario_payload):
    criado = auth_client.post("/usuario", json=usuario_payload).json()

    novo_payload = dict(usuario_payload)
    novo_payload["nome"] = "Nome Totalmente Novo"
    response = auth_client.put(f"/usuario/{criado['id']}", json=novo_payload)
    assert response.status_code == 200
    assert response.json()["nome"] == "Nome Totalmente Novo"


def test_deletar_usuario(auth_client, usuario_payload):
    criado = auth_client.post("/usuario", json=usuario_payload).json()

    response = auth_client.delete(f"/usuario/{criado['id']}")
    assert response.status_code == 204

    # confirma que realmente sumiu (leitura continua pública)
    response = auth_client.get(f"/usuario/{criado['id']}")
    assert response.status_code == 404


def test_deletar_usuario_sem_token_retorna_401(client, auth_client, usuario_payload):
    criado = auth_client.post("/usuario", json=usuario_payload).json()

    response = client.delete(f"/usuario/{criado['id']}")
    assert response.status_code == 401


def test_deletar_usuario_inexistente_retorna_404(auth_client):
    response = auth_client.delete("/usuario/9999")
    assert response.status_code == 404


def test_filtro_por_nome(auth_client, usuario_payload):
    auth_client.post("/usuario", json=usuario_payload)  # "Usuário de Teste"

    outro = dict(usuario_payload)
    outro["nome"] = "Alguém Diferente"
    outro["conta"] = {**usuario_payload["conta"], "numero": "00098-8"}
    auth_client.post("/usuario", json=outro)

    response = auth_client.get("/usuario", params={"nome": "Teste"})
    assert response.status_code == 200
    resultados = response.json()
    assert len(resultados) == 1
    assert resultados[0]["nome"] == "Usuário de Teste"


def test_paginacao(auth_client, usuario_payload):
    for i in range(5):
        payload = dict(usuario_payload)
        payload["conta"] = {**usuario_payload["conta"], "numero": f"0000{i}-0"}
        auth_client.post("/usuario", json=payload)

    response = auth_client.get("/usuario", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    assert len(response.json()) == 2
