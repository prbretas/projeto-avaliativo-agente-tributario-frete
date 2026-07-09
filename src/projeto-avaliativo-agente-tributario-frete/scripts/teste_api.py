"""
Script de teste do fluxo completo via API REST.
Executa: python scripts/teste_api.py
"""
import sys
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as resp:
        return json.loads(resp.read())


print("=== Teste do Agente Tributário de Frete via API ===\n")

# 1. Dispara o agente
print("1. POST /classificar — Operação rodoviária Lucro Real 2026...")
operacao = {
    "modal": "rodoviario",
    "origem_uf": "SP",
    "destino_uf": "RJ",
    "regime_tributario": "lucro_real",
    "data_emissao": "2026-09-15",
    "contratado_pessoa_fisica": False
}

try:
    r1 = post("/classificar", operacao)
    thread_id = r1["thread_id"]
    print(f"   thread_id : {thread_id}")
    print(f"   status    : {r1['status']}")
    print(f"   cclasstrib: {r1['cclasstrib']}")
    print(f"   aliquota  : {r1['aliquota_total']}")
    print(f"   fase      : {r1['fase_transicao']}")
    if r1.get('justificativa'):
        print(f"   justific. : {r1['justificativa'][:100]}...")
    if r1.get('fontes_citadas'):
        print(f"   fontes    : {r1['fontes_citadas']}")
except Exception as e:
    print(f"   ERRO: {e}")
    sys.exit(1)

print()

# 2. Consulta o estado pendente
print(f"2. GET /classificar/{thread_id} — Consultando estado...")
try:
    r2 = get(f"/classificar/{thread_id}")
    print(f"   status    : {r2['status']}")
except Exception as e:
    print(f"   ERRO: {e}")

print()

# 3. Aprova a classificação
print(f"3. POST /classificar/{thread_id}/review — Aprovando...")
try:
    r3 = post(f"/classificar/{thread_id}/review", {"aprovado": True})
    print(f"   status    : {r3['status']}")
    print(f"   cclasstrib: {r3['cclasstrib']}")
    print(f"   aliquota  : {r3['aliquota_total']}")
except Exception as e:
    print(f"   ERRO: {e}")

print("\n=== Fluxo completo executado com sucesso! ===")
