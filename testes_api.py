"""Suíte de integração da API ImóvelFácil (Entrega 4).

Rode contra o servidor local:
    uvicorn main:app --port 8000
    python testes_api.py
"""

import json
import os
import sqlite3
import urllib.error
import urllib.request
import uuid

BASE = os.getenv("TEST_API_BASE", "http://localhost:8000")
RESULTS = []
RUN_ID = uuid.uuid4().hex[:8]
TEST_EMAIL = f"qa.{RUN_ID}@teste.com"
TEST_TITLE = f"Casa Demo Entrega 4 {RUN_ID}"


def request(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        BASE + path, data=data, method=method, headers=headers
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode() or "null")


def check(name, method, path, expected_status, body=None, token=None, expect=None):
    status, payload = request(method, path, body=body, token=token)
    ok = status == expected_status and (expect is None or expect(payload))
    RESULTS.append(ok)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}")
    print(f"       {method} {path} -> {status} (esperado {expected_status})")
    if not ok:
        print(f"       payload: {payload}")
    return payload


print("=" * 72)
print("TESTES DA API IMOVELFACIL - ENTREGA 4")
print("=" * 72)

print("\n--- 1. Saúde e listagem pública ---")
check("Health check", "GET", "/api/health", 200,
      expect=lambda p: p["status"] == "ok" and p["version"] == "1.2.0")
check("Raiz da API", "GET", "/", 200)
check("Lista pública", "GET", "/api/properties", 200,
      expect=lambda p: isinstance(p, list) and len(p) >= 10)
check("Filtro por tipo", "GET", "/api/properties?property_type=Casa", 200,
      expect=lambda p: all(i["property_type"] == "Casa" for i in p))
check("Filtro por finalidade", "GET", "/api/properties?purpose=alugar", 200,
      expect=lambda p: all(i["purpose"] == "alugar" for i in p))
check("Filtro por banheiros", "GET", "/api/properties?bathrooms=3", 200,
      expect=lambda p: all(i["bathrooms"] >= 3 for i in p))
check("Filtro por área", "GET", "/api/properties?min_area=100&max_area=500", 200,
      expect=lambda p: all(100 <= i["area_sqm"] <= 500 for i in p))
check("Faixa de área inválida", "GET", "/api/properties?min_area=500&max_area=100", 400)
check("Ordenação crescente", "GET", "/api/properties?sort=price_asc", 200,
      expect=lambda p: [i["price"] for i in p] == sorted(i["price"] for i in p))
check("Metadados de paginação", "GET", "/api/properties?limit=3&offset=0&with_meta=true", 200,
      expect=lambda p: len(p["items"]) == 3 and p["total"] >= 10 and p["has_next"] is True)
check("Limite inválido", "GET", "/api/properties?limit=999", 422)

print("\n--- 2. Autenticação assinada ---")
check("/me sem token", "GET", "/api/auth/me", 401)
seed_login = check(
    "Login do usuário seed", "POST", "/api/auth/login", 200,
    body={"email": "augusto@email.com", "password": "123456"},
    expect=lambda p: p["token"].count(".") == 2 and p["token_type"] == "bearer",
)
SEED_TOKEN = seed_login.get("token")
check("/me com token", "GET", "/api/auth/me", 200, token=SEED_TOKEN,
      expect=lambda p: p["email"] == "augusto@email.com")
qa_register = check(
    "Cadastro com sessão", "POST", "/api/auth/register", 201,
    body={"name": "QA Entrega 4", "email": TEST_EMAIL, "password": "123456"},
    expect=lambda p: p["email"] == TEST_EMAIL and p["token"].count(".") == 2,
)
QA_TOKEN = qa_register.get("token")
check("E-mail duplicado", "POST", "/api/auth/register", 409,
      body={"name": "QA", "email": TEST_EMAIL, "password": "123456"})
check("E-mail inválido", "POST", "/api/auth/register", 422,
      body={"name": "QA", "email": "email-invalido", "password": "123456"})
check("Senha curta", "POST", "/api/auth/register", 422,
      body={"name": "QA", "email": f"curta.{RUN_ID}@teste.com", "password": "123"})

print("\n--- 3. Criação, edição, propriedade e exclusão ---")
novo = {
    "title": TEST_TITLE,
    "description": "Imóvel criado pela suíte da Entrega 4.",
    "property_type": "Casa",
    "purpose": "comprar",
    "price": 750000,
    "location": "Rua Teste, 42",
    "neighborhood": "Centro",
    "city": "Goiânia",
    "state": "GO",
    "bedrooms": 3,
    "bathrooms": 2,
    "area_sqm": 120,
    "featured": False,
}
check("Criação sem login", "POST", "/api/properties", 401, body=novo)
created = check(
    "Criação autenticada", "POST", "/api/properties", 201,
    body=novo, token=QA_TOKEN,
    expect=lambda p: p["title"] == TEST_TITLE and p["owner_id"] is not None,
)
PROPERTY_ID = created.get("id")
check("Meus anúncios", "GET", "/api/properties/mine", 200, token=QA_TOKEN,
      expect=lambda p: any(i["id"] == PROPERTY_ID for i in p))
check("Outro usuário não pode editar", "PUT", f"/api/properties/{PROPERTY_ID}", 403,
      body={"price": 800000}, token=SEED_TOKEN)
check("Proprietário edita anúncio", "PUT", f"/api/properties/{PROPERTY_ID}", 200,
      body={"price": 810000, "bathrooms": 3}, token=QA_TOKEN,
      expect=lambda p: p["price"] == 810000 and p["bathrooms"] == 3)
check("Edição vazia", "PUT", f"/api/properties/{PROPERTY_ID}", 400,
      body={}, token=QA_TOKEN)

print("\n--- 4. Favoritos isolados por usuário ---")
check("Favoritar sem login", "POST", "/api/favorites", 401,
      body={"property_id": 1, "is_favorite": True})
check("QA favorita imóvel", "POST", "/api/favorites", 200, token=QA_TOKEN,
      body={"property_id": 1, "is_favorite": True},
      expect=lambda p: p["is_favorite"] is True)
check("Lista de favoritos do QA", "GET", "/api/favorites", 200, token=QA_TOKEN,
      expect=lambda p: any(i["id"] == 1 for i in p))
check("Favoritos não vazam para outro usuário", "GET", "/api/favorites", 200,
      token=SEED_TOKEN, expect=lambda p: all(i["id"] != 1 for i in p))
check("Listagem marca favorito do QA", "GET", "/api/properties/1", 200,
      token=QA_TOKEN, expect=lambda p: p["is_favorite"] is True)
check("Remover favorito", "DELETE", "/api/favorites/1", 200, token=QA_TOKEN,
      expect=lambda p: p["is_favorite"] is False)

print("\n--- 5. Estatísticas e exclusão lógica ---")
check("Estatísticas dinâmicas", "GET", "/api/stats", 200,
      expect=lambda p: p["available_properties"] >= 10
      and p["total_users"] >= 2 and isinstance(p["by_type"], dict))
check("Outro usuário não pode excluir", "DELETE", f"/api/properties/{PROPERTY_ID}", 403,
      token=SEED_TOKEN)
check("Proprietário exclui anúncio", "DELETE", f"/api/properties/{PROPERTY_ID}", 200,
      token=QA_TOKEN)
check("Excluído não aparece nos detalhes", "GET", f"/api/properties/{PROPERTY_ID}", 404)


def cleanup():
    """Remove os dados desta execução quando o servidor usa SQLite."""
    from app.config import DATABASE_URL

    if not DATABASE_URL.startswith("sqlite"):
        return
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        return
    connection = sqlite3.connect(db_path)
    user_row = connection.execute(
        "SELECT id FROM users WHERE email = ?", (TEST_EMAIL,)
    ).fetchone()
    if user_row:
        user_id = user_row[0]
        connection.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
        connection.execute("DELETE FROM properties WHERE owner_id = ?", (user_id,))
        connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()


cleanup()
passed = sum(RESULTS)
total = len(RESULTS)
print("\n" + "=" * 72)
print(f"RESULTADO: {passed}/{total} testes passaram")
print("TODOS OS TESTES PASSARAM" if passed == total else f"FALHAS: {total - passed}")
print("=" * 72)
raise SystemExit(0 if passed == total else 1)
