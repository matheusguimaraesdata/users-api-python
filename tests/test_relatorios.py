def test_estatisticas_sem_usuarios(client):
    response = client.get("/relatorios/estatisticas")
    assert response.status_code == 200
    assert response.json()["total_usuarios"] == 0


def test_estatisticas_com_usuarios(client, usuario_payload):
    client.post("/usuario", json=usuario_payload)

    outro = dict(usuario_payload)
    outro["conta"] = {"numero": "00098-8", "agencia": "0002", "balanco": 300.0, "limite": 1000.0}
    client.post("/usuario", json=outro)

    response = client.get("/relatorios/estatisticas")
    assert response.status_code == 200
    data = response.json()
    assert data["total_usuarios"] == 2
    # (100 + 300) / 2 = 200
    assert data["balanco_medio"] == 200.0
    assert data["usuarios_por_agencia"] == {"0001": 1, "0002": 1}


def test_export_csv(client, usuario_payload):
    client.post("/usuario", json=usuario_payload)

    response = client.get("/relatorios/usuarios.csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    corpo = response.text
    assert "nome" in corpo.splitlines()[0]  # cabeçalho
    assert "Usuário de Teste" in corpo
