"""Adaptador de plugin do Streamer Sidekick (categoria: platina)."""
from dataclasses import dataclass

from . import guide_data

MODULE_ID = guide_data.GUIDE_ID


@dataclass(frozen=True)
class ModuleInfo:
    module_id: str
    title: str
    subtitle: str
    status: str
    accent: str


def module_info():
    from .progress import trophy_keys
    from .storage import load_progress

    done_keys = load_progress()
    trophies = trophy_keys()
    done = sum(1 for key in trophies if key in done_keys)
    data = dict(
        module_id=guide_data.GUIDE_ID,
        title=guide_data.GAME_NAME,
        subtitle=guide_data.GAME_SUBTITLE,
        status=f"{done}/{len(trophies)} troféus",
        accent=guide_data.ACCENT,
    )
    try:
        from streamer_sidekick.core.modules import ModuleInfo as SidekickModuleInfo

        return SidekickModuleInfo(**data)
    except Exception:
        return ModuleInfo(**data)


def help_text() -> str:

    from .paths import guide_dir_label
    return (
        "Guia de platina de House Flipper (jogo base) em PT-BR, em 10 abas.\n\n"
        "Antes de começar:\n"
        "• Mude a moeda do jogo para EURO — Negotiator (50.000) e Millionaire "
        "(1.000.000) comparam valores em euro.\n"
        "• Desinstale as DLCs — Perfectionist e Game Over contam as ordens e as "
        "casas das expansões.\n\n"
        "Como usar:\n"
        "• “Passo a passo” tem a rota completa em 5 fases: preparação, ordens, "
        "os 10 compradores, o Game Over e o fechamento.\n"
        "• “Compradores” é a metade da platina. Cada card traz o PERFIL que o jogo "
        "pontua e a RECEITA testada (casa + itens exatos). O leilão é relativo: o "
        "troféu sai para quem der o MAIOR lance, por isso às vezes o certo é deixar "
        "a casa suja.\n"
        "• “37 Casas” é o checklist do Game Over — vender cada uma já entrega 37 "
        "das 50 vendas.\n"
        "• “50 Vendas” é o contador do Senior Estate Agent, com os marcos 10 e 20.\n"
        "• A busca do topo procura em passos, troféus, casas e compradores ao mesmo "
        "tempo.\n\n"
        "O progresso é salvo automaticamente em "
        f"{guide_dir_label()} e sobrevive a "
        "atualizações. Use Exportar/Importar para levar o progresso para outro PC."
    )


def build_page(config=None):
    from .page import GuidePage

    return GuidePage()
