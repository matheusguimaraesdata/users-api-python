def test_criar_usuario(client, usuario_payload):
    response = client.post("/usuario", json=usuario_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Usuário de Teste"
    assert data["conta"]["numero"] == "00099-9"
    assert data["id"] is not None


def test_listar_usuarios_vazio(client):
    response = client.get("/usuario")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_usuarios_apos_criar(client, usuario_payload):
    client.post("/usuario", json=usuario_payload)
    client.post("/usuario", json=usuario_payload)

    response = client.get("/usuario")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_obter_usuario_por_id(client, usuario_payload):
    criado = client.post("/usuario", json=usuario_payload).json()

    response = client.get(f"/usuario/{criado['id']}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Usuário de Teste"


def test_obter_usuario_inexistente_retorna_404(client):
    response = client.get("/usuario/9999")
    assert response.status_code == 404


def test_patch_atualiza_apenas_campo_enviado(client, usuario_payload):
    criado = client.post("/usuario", json=usuario_payload).json()

    response = client.patch(f"/usuario/{criado['id']}", json={"nome": "Nome Atualizado"})
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Nome Atualizado"
    # os demais campos não devem ter sido afetados
    assert data["conta"]["numero"] == "00099-9"


def test_patch_usuario_inexistente_retorna_404(client):
    response = client.patch("/usuario/9999", json={"nome": "Não importa"})
    assert response.status_code == 404


def test_put_substitui_usuario_completo(client, usuario_payload):
    criado = client.post("/usuario", json=usuario_payload).json()

    novo_payload = dict(usuario_payload)
    novo_payload["nome"] = "Nome Totalmente Novo"
    response = client.put(f"/usuario/{criado['id']}", json=novo_payload)
    assert response.status_code == 200
    assert response.json()["nome"] == "Nome Totalmente Novo"


def test_deletar_usuario(client, usuario_payload):
    criado = client.post("/usuario", json=usuario_payload).json()

    response = client.delete(f"/usuario/{criado['id']}")
    assert response.status_code == 204

    # confirma que realmente sumiu
    response = client.get(f"/usuario/{criado['id']}")
    assert response.status_code == 404


def test_deletar_usuario_inexistente_retorna_404(client):
    response = client.delete("/usuario/9999")
    assert response.status_code == 404


def test_filtro_por_nome(client, usuario_payload):
    client.post("/usuario", json=usuario_payload)  # "Usuário de Teste"

    outro = dict(usuario_payload)
    outro["nome"] = "Alguém Diferente"
    outro["conta"] = {**usuario_payload["conta"], "numero": "00098-8"}
    client.post("/usuario", json=outro)

    response = client.get("/usuario", params={"nome": "Teste"})
    assert response.status_code == 200
    resultados = response.json()
    assert len(resultados) == 1
    assert resultados[0]["nome"] == "Usuário de Teste"


def test_paginacao(client, usuario_payload):
    for i in range(5):
        payload = dict(usuario_payload)
        payload["conta"] = {**usuario_payload["conta"], "numero": f"0000{i}-0"}
        client.post("/usuario", json=payload)

    response = client.get("/usuario", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    assert len(response.json()) == 2
