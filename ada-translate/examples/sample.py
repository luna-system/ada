def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def factorial(n: int) -> int:
    """Calculate n factorial."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def is_prime(n: int) -> bool:
    """Check if n is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def filter_and_sum(items: list[dict]) -> int:
    """Sum values of active items."""
    return sum(item["value"] for item in items if item.get("active"))


async def fetch_all(urls: list[str]) -> list[str]:
    """Fetch all URLs in parallel."""
    import asyncio
    import httpx
    
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.text for r in responses]
