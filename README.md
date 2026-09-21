# ConectaShop — Grupo Cliente

Projeto da atividade de Sistemas Distribuídos — Interoperabilidade REST e gRPC.

## Cliente REST
## Pré-requisitos e Instalação

- **Python 3.10+** instalado.
- Instale as dependências executando na raiz do projeto:

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

-------------------------------------------

Execute a partir da raiz do projeto:

-Cliente REST-

PowerShell
python cliente_rest/rest_client.py

Por padrão, o cliente usa: - Plaintext

http://localhost:8080

Para trocar o servidor sem alterar o código: - PowerShell

$env:REST_BASE_URL="http://HOST:PORTA"
python cliente_rest/rest_client.py

Para trocar o código da equipe: - PowerShell

$env:CLIENT_TEAM="C01"
python cliente_rest/rest_client.py

Também é possível usar argumentos: - PowerShell

python cliente_rest/rest_client.py --base-url "http://HOST:PORTA" --team C01

-Cliente gRPC-

Execute a partir da raiz do projeto: - PowerShell

python cliente_grpc/grpc_cliente.py

Por padrão, o cliente usa: - Plaintext

localhost:50051

Para trocar o servidor sem alterar o código: - PowerShell

$env:GRPC_TARGET="HOST:PORTA"
python cliente_grpc/grpc_cliente.py

Para trocar o código da equipe: - PowerShell

$env:CLIENT_TEAM="C01"
python cliente_grpc/grpc_cliente.py
