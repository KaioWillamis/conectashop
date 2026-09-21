# ConectaShop — Grupo Cliente

Projeto da atividade de Sistemas Distribuídos — Interoperabilidade REST e gRPC.

## Cliente REST

Execute a partir da raiz do projeto:

```powershell
python cliente_rest/rest_client.py
```

Por padrão, o cliente usa:

```text
http://localhost:8080
```

Para trocar o servidor sem alterar o código:

```powershell
$env:REST_BASE_URL="http://HOST:PORTA"
python cliente_rest/rest_client.py
```

Para trocar o código da equipe:

```powershell
$env:CLIENT_TEAM="C01"
python cliente_rest/rest_client.py
```

Também é possível usar argumentos:

```powershell
python cliente_rest/rest_client.py --base-url "http://HOST:PORTA" --team C01
```

