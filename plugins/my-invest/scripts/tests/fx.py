"""Test helpers: fixture loading and synthetic companyfacts builders (no network)."""
import json
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load(name):
    with open(os.path.join(DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


def text(name):
    with open(os.path.join(DIR, name), "r", encoding="utf-8") as f:
        return f.read()


def fact(end, val, start=None, filed="2025-11-01", accn="0000000001-25-000001", fy=2025, fp="FY", form="10-K"):
    f = {"end": end, "val": val, "accn": accn, "fy": fy, "fp": fp, "form": form, "filed": filed}
    if start:
        f["start"] = start
    return f


def facts_doc(**concepts):
    """facts_doc(Assets=[fact,...], ...) -> companyfacts-shaped dict; unit USD unless a (unit, list) tuple."""
    us = {}
    for name, v in concepts.items():
        unit, lst = v if isinstance(v, tuple) else ("USD", v)
        us[name] = {"units": {unit: lst}}
    return {"cik": 1, "entityName": "T", "facts": {"us-gaap": us}}


class FakeResp:
    def __init__(self, body):
        self._b = body if isinstance(body, bytes) else body.encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False
