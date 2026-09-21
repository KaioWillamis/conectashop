from concurrent import futures
import math

import grpc

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "cliente_grpc")
)

import shipping_pb2
import shipping_pb2_grpc


SERVER_TEAM = "S-LOCAL"


class ShippingService(shipping_pb2_grpc.ShippingServiceServicer):

    def Health(self, request, context):
        metadata = dict(context.invocation_metadata())

        if "x-client-team" not in metadata:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "MISSING_CLIENT_TEAM"
            )

        return shipping_pb2.HealthResponse(
            status="SERVING",
            server_team=SERVER_TEAM,
        )

    def CalculateShipping(self, request, context):
        metadata = dict(context.invocation_metadata())

        if "x-client-team" not in metadata:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "MISSING_CLIENT_TEAM"
            )

        if not request.request_id:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "MISSING_REQUEST_ID"
            )

        if request.weight_grams < 1 or request.weight_grams > 30000:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "INVALID_WEIGHT"
            )

        if request.zone == shipping_pb2.SHIPPING_ZONE_UNSPECIFIED:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "INVALID_ZONE"
            )

        if request.mode == shipping_pb2.SHIPPING_MODE_UNSPECIFIED:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "INVALID_MODE"
            )

        tarifas = {
            shipping_pb2.LOCAL: {
                shipping_pb2.STANDARD: 1000,
                shipping_pb2.EXPRESS: 1600,
            },
            shipping_pb2.REGIONAL: {
                shipping_pb2.STANDARD: 1800,
                shipping_pb2.EXPRESS: 2800,
            },
            shipping_pb2.NATIONAL: {
                shipping_pb2.STANDARD: 3000,
                shipping_pb2.EXPRESS: 4500,
            },
        }

        adicionais = {
            shipping_pb2.STANDARD: 400,
            shipping_pb2.EXPRESS: 600,
        }

        prazos = {
            shipping_pb2.LOCAL: {
                shipping_pb2.STANDARD: 2,
                shipping_pb2.EXPRESS: 1,
            },
            shipping_pb2.REGIONAL: {
                shipping_pb2.STANDARD: 4,
                shipping_pb2.EXPRESS: 2,
            },
            shipping_pb2.NATIONAL: {
                shipping_pb2.STANDARD: 7,
                shipping_pb2.EXPRESS: 3,
            },
        }

        quilogramas_cobrados = math.ceil(
            request.weight_grams / 1000
        )

        tarifa_base = tarifas[request.zone][request.mode]
        adicional = adicionais[request.mode]

        price = (
            tarifa_base
            + quilogramas_cobrados * adicional
        )

        estimated_days = prazos[request.zone][request.mode]

        return shipping_pb2.ShippingResponse(
            request_id=request.request_id,
            price_cents=price,
            estimated_days=estimated_days,
            server_team=SERVER_TEAM,
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    shipping_pb2_grpc.add_ShippingServiceServicer_to_server(
        ShippingService(),
        server,
    )

    server.add_insecure_port("[::]:50051")

    server.start()

    print("Servidor gRPC iniciado")
    print("Equipe: S-LOCAL")
    print("Porta: 50051")
    print("Aguardando chamadas...")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()