"""Chaves de progresso do guia.

O guia tem itens marcáveis em seis listas (passos da rota, compradores, troféus,
casas, vendas e perks). Este módulo centraliza o formato das chaves para que
`module.py`, `page.py` e o importador/exportador falem a mesma língua.
"""
from __future__ import annotations

from . import guide_data


def step_key(num: str) -> str:
    return "step_" + str(num).replace(".", "_")


def buyer_key(buyer_id: str) -> str:
    return f"buyer_{buyer_id}"


def trophy_key(trophy_id: str) -> str:
    return f"trophy_{trophy_id}"


def house_key(index: int) -> str:
    return f"house_{index}"


def sale_key(index: int) -> str:
    return f"sale_{index}"


def perk_key(index: int) -> str:
    return f"perk_{index}"


def secret_key(index: int) -> str:
    return f"secret_{index}"


def trophy_keys() -> list[str]:
    return [trophy_key(t["id"]) for t in guide_data.TROPHIES]


def sale_keys() -> list[str]:
    return [sale_key(i) for i in range(guide_data.SALES_TOTAL)]


def sales_done(done: set[str]) -> int:
    """Quantas vendas estão marcadas (o contador do Senior Estate Agent)."""
    return sum(1 for key in sale_keys() if key in done)


def all_keys() -> list[str]:
    """Todas as chaves marcáveis do guia, na ordem das abas."""
    keys = [step_key(step["num"]) for step in guide_data.ROUTE]
    keys += [buyer_key(b["key"]) for b in guide_data.BUYERS]
    keys += trophy_keys()
    keys += [house_key(i) for i in range(len(guide_data.HOUSES))]
    keys += sale_keys()
    keys += [perk_key(i) for i in range(len(guide_data.PERKS))]
    keys += [secret_key(i) for i in range(len(guide_data.SECRETS))]
    return keys


def normalize_imported(raw) -> set[str]:
    """Aceita o formato deste plugin e um dicionário `{chave: bool}`."""
    if isinstance(raw, dict):
        raw = [key for key, value in raw.items() if value]
    return {str(key) for key in raw}
