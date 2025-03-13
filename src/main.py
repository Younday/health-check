import asyncio
import contextlib
import logging
import os
import pathlib
import time

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import Settings, read_yaml

logging.basicConfig(
    format="%(asctime)s %(levelname)-1s %(message)s", level=logging.INFO
)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

DEFAULT_OK_MESSAGE = ["up", "ok"]

def parse_time(time_str: str) -> int:
    """
    Parse time string (for example: 1s, 4m, 1h) to seconds
    
    Args:
    time_str: str - time string to parse

    Returns:
    int: time in seconds
    """
    if time_str.endswith("s"):
        return int(time_str[:-1])
    elif time_str.endswith("m"):
        return int(time_str[:-1]) * 60
    elif time_str.endswith("h"):
        return int(time_str[:-1]) * 60 * 60
    else:
        return int(time_str)

def send_alert_message_slack(message: str) -> None:
    # Mock sending message to slack
    logging.info(f"Sending message to slack: {message}")

async def parse_response(resp: aiohttp.ClientResponse) -> None:
    """
    Parse response from endpoint and check for "checks" key in the response
    Logs if service found in "checks" key in response is up or down

    Args:
    resp: aiohttp.ClientResponse - response from endpoint

    Returns:
    None
    """
    if resp is None:
        return
    if resp.headers.get("Content-Type") != "application/json":
        return
    resp_dict = await resp.json()
    # Only check for "checks" key in the response for now
    # An improvement would be to check for different sections in the response
    # OR allow the user to define with sections to check
    if "checks" in resp_dict:
        checks = resp_dict["checks"]
        if checks is None or not isinstance(checks, dict):
            return
        for service, status in checks.items():
            if status.lower() in DEFAULT_OK_MESSAGE:
                logging.info(f"Service {service} is up - endpoint: {resp.url}")
            else:
                logging.error(f"Service {service} is down - endpoint: {resp.url}")

async def health_check_async(session, url: str, timeout: int) -> None:
    """"
    Perform health check on endpoint asynchronously and 
    logs errors if any errors occur or if the service is down.
    Metrics like response time are also logged.
    
    Args:
    session: aiohttp.ClientSession - session to use for the request
    url: str - url to perform health check on
    timeout: int - timeout for the request

    Returns:
    None
    """

    # Convert time to milliseconds
    start_time = time.time() * 1000
    try:
        resp = await session.get(url, timeout=timeout)
    except aiohttp.ClientConnectionError:
        logging.error(f"Connection error for {url}")
        send_alert_message_slack(f"Connection error for {url}")
        return
    except asyncio.exceptions.TimeoutError:
        logging.warning(f"Request timed out for {url} after {timeout} seconds")
        send_alert_message_slack(f"Request timed out for {url} after {timeout} seconds")
        return
    # Convert time to milliseconds
    end_time = time.time() * 1000
    resp_time = end_time - start_time
    await parse_response(resp)
    if resp.status != 200:
        logging.error(
            f"response time: {resp_time:.1f} ms - endpoint: {url} - status code: {resp.status} - status: down"
        )
        send_alert_message_slack(
            f"Healthcheck failed - response time: {resp_time:.1f} ms - endpoint: {url} - status code: {resp.status} - status: down")
    else:
        logging.info(
            f"response time: {resp_time:.1f} ms - endpoint: {url} - status code: {resp.status} - status: up"
        )

async def run_async(urls: list[tuple[str, int]]) -> None:
    """
    Run health check function on multiple endpoints asynchronously 
    with a shared aiohttp session

    Args:
    urls: list[tuple[str, int]] - list of tuples containing url and timeout for the request

    Returns:
    None
    """
    async with aiohttp.ClientSession() as session:
        tasks = [health_check_async(session, url, timeout) for (url, timeout) in urls]
        _ = await asyncio.gather(*tasks)

async def main():
    settings = Settings()
    job_defaults = {
        'coalesce': False,
        'max_instances': settings.max_instances
    }
    endpoints = read_yaml(os.path.join(pathlib.Path().absolute(), settings.yaml_file))
    intervals = [x.interval for x in endpoints.endpoints]
    scheduler = AsyncIOScheduler(job_defaults=job_defaults)
    for interval in set(intervals):
        ends = endpoints.get_by_interval(interval)
        urls = [(str(x.url), x.timeout) for x in ends]
        scheduler.add_job(run_async, "interval", seconds=parse_time(interval), args=(urls,), name=f"health_check_{interval}")
    scheduler.start()
    while True:
        await asyncio.sleep(100)

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
