from __future__ import annotations

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status


_bucket: Dict[Tuple[str, str], Tuple[int, float]] = {}


def client_key(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    sess = request.cookies.get("pc_sess") or "anon"
    return f"{ip}:{sess}"


def validations_today(key: str) -> int:
    cnt, ts = _bucket.get((key, day_stamp()), (0, time.time()))
    return cnt


def day_stamp() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def increment_validation(key: str) -> int:
    k = (key, day_stamp())
    cnt, _ = _bucket.get(k, (0, time.time()))
    cnt += 1
    _bucket[k] = (cnt, time.time())
    return cnt


def enforce_limit(request: Request, limit_per_day: int) -> None:
    key = client_key(request)
    cnt = validations_today(key)
    if cnt >= limit_per_day:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Free plan limit reached (5/day). Upgrade to enable more, UPO and export.",
        )

