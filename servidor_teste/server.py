from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math

HOST = "localhost"
PORT = 8080
SERVER_TEAM = "S-TESTE"

CATALOG = {
    "KB-100": {"sku": "KB-100", "name": "Teclado Mecânico", "unitPriceCents": 25990, "available": True},
    "MS-200": {"sku": "MS-200", "name": "Mouse Sem Fio", "unitPriceCents": 12990, "available": True},
    "HD-300": {"sku": "HD-300", "name": "Headset USB", "unitPriceCents": 19990, "available": True},
    "MN-400": {"sku": "MN-400", "name": "Monitor 27", "unitPriceCents": 119990, "available": True},
}


class ConectaShopHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[SERVER] {format % args}")

    def send_json(self, status_code, body, request_id=None):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))

        if request_id:
            self.send_header("X-Request-ID", request_id)

        self.end_headers()
        self.wfile.write(data)

    def get_required_headers(self):
        client_team = self.headers.get("X-Client-Team")
        request_id = self.headers.get("X-Request-ID")

        if not client_team or not request_id:
            missing_id = request_id or "unknown"
            self.send_json(
                400,
                {
                    "code": "MISSING_REQUIRED_HEADER",
                    "message": "X-Client-Team and X-Request-ID are required",
                    "requestId": missing_id,
                },
                request_id if request_id else None,
            )
            return None, None

        return client_team, request_id

    def do_GET(self):
        _, request_id = self.get_required_headers()

        if not request_id:
            return

        prefix = "/api/v1/products/"

        if self.path.startswith(prefix):
            sku = self.path[len(prefix):]

            if sku in CATALOG:
                self.send_json(200, CATALOG[sku], request_id)
                return

            self.send_json(
                404,
                {
                    "code": "PRODUCT_NOT_FOUND",
                    "message": "Product not found",
                    "requestId": request_id,
                },
                request_id,
            )
            return

        self.send_json(
            404,
            {
                "code": "NOT_FOUND",
                "message": "Path not found",
                "requestId": request_id,
            },
            request_id,
        )

    def do_POST(self):
        _, request_id = self.get_required_headers()

        if not request_id:
            return

        if self.path != "/api/v1/quotes":
            self.send_json(
                404,
                {
                    "code": "NOT_FOUND",
                    "message": "Path not found",
                    "requestId": request_id,
                },
                request_id,
            )
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            body = json.loads(raw_body.decode("utf-8"))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(
                400,
                {
                    "code": "INVALID_REQUEST",
                    "message": "Invalid JSON",
                    "requestId": request_id,
                },
                request_id,
            )
            return

        if not isinstance(body, dict) or not isinstance(body.get("items"), list):
            self.send_json(
                400,
                {
                    "code": "INVALID_REQUEST",
                    "message": "items is required",
                    "requestId": request_id,
                },
                request_id,
            )
            return

        items = body["items"]

        if not 1 <= len(items) <= 5:
            self.send_json(
                422,
                {
                    "code": "INVALID_QUANTITY_OR_ITEMS",
                    "message": "items must contain 1 to 5 distinct items",
                    "requestId": request_id,
                },
                request_id,
            )
            return

        seen_skus = set()
        subtotal = 0

        for item in items:
            if not isinstance(item, dict):
                self.send_json(
                    400,
                    {
                        "code": "INVALID_REQUEST",
                        "message": "Invalid item",
                        "requestId": request_id,
                    },
                    request_id,
                )
                return

            sku = item.get("sku")
            quantity = item.get("quantity")

            if sku in seen_skus:
                self.send_json(
                    422,
                    {
                        "code": "INVALID_QUANTITY_OR_ITEMS",
                        "message": "Duplicate SKU",
                        "requestId": request_id,
                    },
                    request_id,
                )
                return

            if not isinstance(quantity, int) or isinstance(quantity, bool) or not 1 <= quantity <= 10:
                self.send_json(
                    422,
                    {
                        "code": "INVALID_QUANTITY_OR_ITEMS",
                        "message": "Quantity must be between 1 and 10",
                        "requestId": request_id,
                    },
                    request_id,
                )
                return

            if sku not in CATALOG:
                self.send_json(
                    422,
                    {
                        "code": "INVALID_PRODUCT",
                        "message": "Invalid product",
                        "requestId": request_id,
                    },
                    request_id,
                )
                return

            seen_skus.add(sku)
            subtotal += CATALOG[sku]["unitPriceCents"] * quantity

        if subtotal < 50000:
            discount_percent = 0
        elif subtotal < 100000:
            discount_percent = 5
        else:
            discount_percent = 10

        discount_cents = (subtotal * discount_percent) // 100
        total_cents = subtotal - discount_cents

        self.send_json(
            200,
            {
                "requestId": request_id,
                "subtotalCents": subtotal,
                "discountPercent": discount_percent,
                "discountCents": discount_cents,
                "totalCents": total_cents,
            },
            request_id,
        )


def main():
    server = ThreadingHTTPServer((HOST, PORT), ConectaShopHandler)

    print("=" * 60)
    print("ConectaShop - Servidor REST de TESTE")
    print(f"Equipe do servidor: {SERVER_TEAM}")
    print(f"Endereço: http://{HOST}:{PORT}")
    print("Pressione CTRL+C para parar.")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
