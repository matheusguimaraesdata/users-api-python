def test_estatisticas_sem_usuarios(client):
    response = client.get("/relatorios/estatisticas")
    assert response.status_code == 200
    assert response.json()["total_usuarios"] == 0


def test_estatisticas_com_usuarios(auth_client, usuario_payload):
    auth_client.post("/usuario", json=usuario_payload)  # balanco 100, limite 500

    outro = dict(usuario_payload)
    outro["conta"] = {"numero": "00098-8", "agencia": "0002", "balanco": 300.0, "limite": 1000.0}
    auth_client.post("/usuario", json=outro)

    response = auth_client.get("/relatorios/estatisticas")
    assert response.status_code == 200
    data = response.json()

    assert data["total_usuarios"] == 2
    assert data["saldo"]["medio"] == 200.0  # (100 + 300) / 2
    assert data["saldo"]["minimo"] == 100.0
    assert data["saldo"]["maximo"] == 300.0
    assert data["saldo"]["contas_negativas"] == 0
    assert data["limite"]["distribuicao_por_faixa"]["até 1k"] == 2  # 500 e 1000 caem na mesma faixa
    assert data["usuarios_por_agencia"] == {"0001": 1, "0002": 1}


def test_estatisticas_identifica_conta_negativa(auth_client, usuario_payload):
    negativo = dict(usuario_payload)
    negativo["conta"] = {"numero": "00097-7", "agencia": "0001", "balanco": -50.0, "limite": 500.0}
    auth_client.post("/usuario", json=negativo)

    response = auth_client.get("/relatorios/estatisticas")
    data = response.json()
    assert data["saldo"]["contas_negativas"] == 1
    assert data["saldo"]["percentual_contas_negativas"] == 100.0


def test_top_usuarios_sem_dados(client):
    response = client.get("/relatorios/top-usuarios")
    assert response.status_code == 200
    assert response.json()["resultado"] == []


def test_top_usuarios_por_balanco_desc(auth_client, usuario_payload):
    baixo = dict(usuario_payload)
    baixo["conta"] = {"numero": "1", "agencia": "0001", "balanco": 50.0, "limite": 500.0}
    auth_client.post("/usuario", json=baixo)

    alto = dict(usuario_payload)
    alto["conta"] = {"numero": "2", "agencia": "0001", "balanco": 900.0, "limite": 500.0}
    auth_client.post("/usuario", json=alto)

    response = auth_client.get("/relatorios/top-usuarios", params={"criterio": "balanco", "ordem": "desc", "limite": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data["resultado"]) == 1
    assert data["resultado"][0]["balanco"] == 900.0


def test_top_usuarios_criterio_invalido_retorna_422(client):
    response = client.get("/relatorios/top-usuarios", params={"criterio": "campo_que_nao_existe"})
    assert response.status_code == 422


def test_export_csv(auth_client, usuario_payload):
    auth_client.post("/usuario", json=usuario_payload)

    response = auth_client.get("/relatorios/usuarios.csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    corpo = response.text
    assert "nome" in corpo.splitlines()[0]  # cabeçalho
    assert "Usuário de Teste" in corpo
