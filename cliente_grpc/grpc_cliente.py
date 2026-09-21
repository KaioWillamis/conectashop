import os
import sys
import time
import uuid

import grpc

import shipping_pb2
import shipping_pb2_grpc


CLIENT_TEAM = os.getenv("CLIENT_TEAM", "C01")
GRPC_TARGET = os.getenv("GRPC_TARGET", "localhost:50051")


def gerar_request_id():
    return f"req-{uuid.uuid4().hex[:12]}"


def imprimir_log(
    request_id,
    operation,
    target,
    status,
    duration_ms,
    result,
    detalhes="",
):
    linha = (
        f"protocol=GRPC "
        f"client={CLIENT_TEAM} "
        f"requestId={request_id} "
        f"operation={operation} "
        f"target={target} "
        f"status={status} "
        f"durationMs={duration_ms} "
        f"result={result}"
    )

    if detalhes:
        linha += f" {detalhes}"

    print(linha)


def teste_g1_health(stub):
    request_id = gerar_request_id()
    inicio = time.perf_counter()

    try:
        resposta = stub.Health(
            shipping_pb2.HealthRequest(),
            metadata=[
                ("x-client-team", CLIENT_TEAM)
            ],
            timeout=5,
        )

        duracao = int((time.perf_counter() - inicio) * 1000)

        passou = resposta.status == "SERVING"

        imprimir_log(
            request_id,
            "Health",
            GRPC_TARGET,
            "OK",
            duracao,
            "PASS" if passou else "FAIL",
            f"status={resposta.status} serverTeam={resposta.server_team}",
        )

        return passou

    except grpc.RpcError as erro:
        duracao = int((time.perf_counter() - inicio) * 1000)

        imprimir_log(
            request_id,
            "Health",
            GRPC_TARGET,
            erro.code().name,
            duracao,
            "FAIL",
            f"details={erro.details()}",
        )

        return False


def teste_calculate(
    nome,
    weight_grams,
    zone,
    mode,
    expected_price,
    expected_days,
):
    request_id = gerar_request_id()
    inicio = time.perf_counter()

    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            stub = shipping_pb2_grpc.ShippingServiceStub(channel)

            request = shipping_pb2.ShippingRequest(
                request_id=request_id,
                weight_grams=weight_grams,
                zone=zone,
                mode=mode,
            )

            resposta = stub.CalculateShipping(
                request,
                metadata=[
                    ("x-client-team", CLIENT_TEAM)
                ],
                timeout=5,
            )

        duracao = int((time.perf_counter() - inicio) * 1000)

        passou = (
            resposta.request_id == request_id
            and resposta.price_cents == expected_price
            and resposta.estimated_days == expected_days
        )

        imprimir_log(
            request_id,
            "CalculateShipping",
            GRPC_TARGET,
            "OK",
            duracao,
            "PASS" if passou else "FAIL",
            (
                f"priceCents={resposta.price_cents} "
                f"estimatedDays={resposta.estimated_days} "
                f"serverTeam={resposta.server_team}"
            ),
        )

        return passou

    except grpc.RpcError as erro:
        duracao = int((time.perf_counter() - inicio) * 1000)

        imprimir_log(
            request_id,
            "CalculateShipping",
            GRPC_TARGET,
            erro.code().name,
            duracao,
            "FAIL",
            f"details={erro.details()}",
        )

        return False


def teste_g5():
    request_id = gerar_request_id()
    inicio = time.perf_counter()

    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            stub = shipping_pb2_grpc.ShippingServiceStub(channel)

            request = shipping_pb2.ShippingRequest(
                request_id=request_id,
                weight_grams=0,
                zone=shipping_pb2.LOCAL,
                mode=shipping_pb2.STANDARD,
            )

            stub.CalculateShipping(
                request,
                metadata=[
                    ("x-client-team", CLIENT_TEAM)
                ],
                timeout=5,
            )

        duracao = int((time.perf_counter() - inicio) * 1000)

        imprimir_log(
            request_id,
            "CalculateShipping",
            GRPC_TARGET,
            "OK",
            duracao,
            "FAIL",
            "esperava INVALID_WEIGHT",
        )

        return False

    except grpc.RpcError as erro:
        duracao = int((time.perf_counter() - inicio) * 1000)

        passou = (
            erro.code() == grpc.StatusCode.INVALID_ARGUMENT
            and erro.details() == "INVALID_WEIGHT"
        )

        imprimir_log(
            request_id,
            "CalculateShipping",
            GRPC_TARGET,
            erro.code().name,
            duracao,
            "PASS" if passou else "FAIL",
            f"details={erro.details()}",
        )

        return passou


def main():
    print("========================================")
    print("Cliente gRPC - ConectaShop")
    print(f"Equipe: {CLIENT_TEAM}")
    print(f"Destino: {GRPC_TARGET}")
    print("========================================")

    resultados = []

    with grpc.insecure_channel(GRPC_TARGET) as channel:
        stub = shipping_pb2_grpc.ShippingServiceStub(channel)

        print("\nG1 - Health")
        resultados.append(teste_g1_health(stub))

    print("\nG2 - 1500g LOCAL STANDARD")
    resultados.append(
        teste_calculate(
            "G2",
            1500,
            shipping_pb2.LOCAL,
            shipping_pb2.STANDARD,
            1800,
            2,
        )
    )

    print("\nG3 - 2500g REGIONAL EXPRESS")
    resultados.append(
        teste_calculate(
            "G3",
            2500,
            shipping_pb2.REGIONAL,
            shipping_pb2.EXPRESS,
            4600,
            2,
        )
    )

    print("\nG4 - 1000g NATIONAL STANDARD")
    resultados.append(
        teste_calculate(
            "G4",
            1000,
            shipping_pb2.NATIONAL,
            shipping_pb2.STANDARD,
            3400,
            7,
        )
    )

    print("\nG5 - peso 0")
    resultados.append(teste_g5())

    print("\n========================================")

    total = sum(resultados)

    print(f"Resultado final: {total}/5 testes PASS")

    if total == 5:
        print("Todos os testes gRPC passaram!")
        return 0

    print("Existem testes que falharam.")
    return 1


if __name__ == "__main__":
    sys.exit(main())