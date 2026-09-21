import argparse
import json
import logging
import os
import sys
import time
import uuid

import requests


DEFAULT_BASE_URL = "http://localhost:8080"
DEFAULT_CLIENT_TEAM = "C01"
TIMEOUT_SECONDS = 10

logger = logging.getLogger("conectashop-rest")


def configure_logging(log_file: str) -> None:
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def new_request_id() -> str:
    return f"req-{uuid.uuid4().hex[:12]}"


def normalize_api_base(base_url: str) -> str:
    base_url = base_url.rstrip("/")

    if base_url.endswith("/api/v1"):
        return base_url

    return f"{base_url}/api/v1"


def log_result(
    request_id: str,
    operation: str,
    target: str,
    status: str,
    duration_ms: int,
    result: str,
    extra: str = "",
) -> None:
    message = (
        f"protocol=REST "
        f"client={CLIENT_TEAM} "
        f"requestId={request_id} "
        f"operation={operation} "
        f"target={target} "
        f"status={status} "
        f"durationMs={duration_ms} "
        f"result={result}"
    )

    if extra:
        message += f" {extra}"

    logger.info(message)


def request_json(method: str, url: str, request_id: str, **kwargs):
    headers = kwargs.pop("headers", {})
    kwargs.pop("operation", None)
    headers["X-Client-Team"] = CLIENT_TEAM
    headers["X-Request-ID"] = request_id

    response = None
    started = time.perf_counter()

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
        duration_ms = round((time.perf_counter() - started) * 1000)

        try:
            data = response.json()
        except ValueError:
            data = None

        return response, data, duration_ms

    except requests.RequestException as exc:
        duration_ms = round((time.perf_counter() - started) * 1000)
        log_result(
            request_id,
            kwargs.get("operation", "UNKNOWN"),
            url,
            "CONNECTION_ERROR",
            duration_ms,
            "FAIL",
            f"error={json.dumps(str(exc), ensure_ascii=False)}",
        )
        return None, None, duration_ms


def run_r1(api_base: str) -> bool:
    request_id = new_request_id()
    url = f"{api_base}/products/KB-100"

    response, data, duration = request_json(
        "GET",
        url,
        request_id,
        operation="GET_PRODUCT",
    )

    passed = (
        response is not None
        and response.status_code == 200
        and isinstance(data, dict)
        and data.get("unitPriceCents") == 25990
    )

    status = response.status_code if response is not None else "ERROR"
    extra = f"unitPriceCents={data.get('unitPriceCents')}" if isinstance(data, dict) else ""

    log_result(request_id, "R1_GET_PRODUCT", url, str(status), duration, "PASS" if passed else "FAIL", extra)
    print(f"R1: {'PASS' if passed else 'FAIL'}")
    return passed


def run_r2(api_base: str) -> bool:
    request_id = new_request_id()
    url = f"{api_base}/products/XX-999"

    response, data, duration = request_json(
        "GET",
        url,
        request_id,
        operation="GET_PRODUCT",
    )

    passed = (
        response is not None
        and response.status_code == 404
        and isinstance(data, dict)
        and data.get("code") == "PRODUCT_NOT_FOUND"
    )

    status = response.status_code if response is not None else "ERROR"
    extra = f"code={data.get('code')}" if isinstance(data, dict) else ""

    log_result(request_id, "R2_GET_UNKNOWN_PRODUCT", url, str(status), duration, "PASS" if passed else "FAIL", extra)
    print(f"R2: {'PASS' if passed else 'FAIL'}")
    return passed


def run_r3(api_base: str) -> bool:
    request_id = new_request_id()
    url = f"{api_base}/quotes"

    payload = {
        "items": [
            {"sku": "KB-100", "quantity": 2},
            {"sku": "MS-200", "quantity": 1},
        ]
    }

    response, data, duration = request_json(
        "POST",
        url,
        request_id,
        operation="CREATE_QUOTE",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    passed = (
        response is not None
        and response.status_code == 200
        and isinstance(data, dict)
        and data.get("subtotalCents") == 64970
        and data.get("discountPercent") == 5
        and data.get("discountCents") == 3248
        and data.get("totalCents") == 61722
    )

    status = response.status_code if response is not None else "ERROR"
    extra = (
        f"subtotalCents={data.get('subtotalCents')} "
        f"discountPercent={data.get('discountPercent')} "
        f"discountCents={data.get('discountCents')} "
        f"totalCents={data.get('totalCents')}"
        if isinstance(data, dict)
        else ""
    )

    log_result(request_id, "R3_CREATE_QUOTE", url, str(status), duration, "PASS" if passed else "FAIL", extra)
    print(f"R3: {'PASS' if passed else 'FAIL'}")
    return passed


def run_r4(api_base: str) -> bool:
    request_id = new_request_id()
    url = f"{api_base}/quotes"

    payload = {
        "items": [
            {"sku": "MN-400", "quantity": 1},
        ]
    }

    response, data, duration = request_json(
        "POST",
        url,
        request_id,
        operation="CREATE_QUOTE",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    passed = (
        response is not None
        and response.status_code == 200
        and isinstance(data, dict)
        and data.get("subtotalCents") == 119990
        and data.get("discountPercent") == 10
        and data.get("discountCents") == 11999
        and data.get("totalCents") == 107991
    )

    status = response.status_code if response is not None else "ERROR"
    extra = (
        f"subtotalCents={data.get('subtotalCents')} "
        f"discountPercent={data.get('discountPercent')} "
        f"discountCents={data.get('discountCents')} "
        f"totalCents={data.get('totalCents')}"
        if isinstance(data, dict)
        else ""
    )

    log_result(request_id, "R4_CREATE_QUOTE", url, str(status), duration, "PASS" if passed else "FAIL", extra)
    print(f"R4: {'PASS' if passed else 'FAIL'}")
    return passed


def run_r5(api_base: str) -> bool:
    request_id = new_request_id()
    url = f"{api_base}/quotes"

    payload = {
        "items": [
            {"sku": "XX-999", "quantity": 1},
        ]
    }

    response, data, duration = request_json(
        "POST",
        url,
        request_id,
        operation="CREATE_QUOTE",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    passed = (
        response is not None
        and response.status_code == 422
        and isinstance(data, dict)
        and data.get("code") == "INVALID_PRODUCT"
    )

    status = response.status_code if response is not None else "ERROR"
    extra = f"code={data.get('code')}" if isinstance(data, dict) else ""

    log_result(request_id, "R5_INVALID_PRODUCT", url, str(status), duration, "PASS" if passed else "FAIL", extra)
    print(f"R5: {'PASS' if passed else 'FAIL'}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Cliente REST - ConectaShop")
    parser.add_argument(
        "--base-url",
        default=os.getenv("REST_BASE_URL", DEFAULT_BASE_URL),
        help="URL base do servidor REST. Também pode ser definida por REST_BASE_URL.",
    )
    parser.add_argument(
        "--team",
        default=os.getenv("CLIENT_TEAM", DEFAULT_CLIENT_TEAM),
        help="Código da equipe cliente. Também pode ser definido por CLIENT_TEAM.",
    )
    args = parser.parse_args()

    global CLIENT_TEAM
    CLIENT_TEAM = args.team

    log_file = os.path.join("logs", "rest_client.log")
    os.makedirs("logs", exist_ok=True)
    configure_logging(log_file)

    api_base = normalize_api_base(args.base_url)

    print("=" * 60)
    print("ConectaShop - Cliente REST")
    print(f"Equipe: {CLIENT_TEAM}")
    print(f"Servidor: {api_base}")
    print("=" * 60)

    tests = [
        run_r1,
        run_r2,
        run_r3,
        run_r4,
        run_r5,
    ]

    results = [test(api_base) for test in tests]

    passed = sum(results)
    total = len(results)

    print("=" * 60)
    print(f"Resultado final: {passed}/{total} testes PASS")
    print(f"Log: {log_file}")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
