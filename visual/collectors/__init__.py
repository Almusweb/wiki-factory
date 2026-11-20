"""Collettori read-only, uno per fonte. Nessuno apre un file in scrittura."""
from visual.collectors.base import Collector, Reading
from visual.collectors.coordinamento import CoordinamentoCollector
from visual.collectors.cost_alert import CostAlertCollector
from visual.collectors.events import EventStoreCollector
from visual.collectors.kanban import SprintCollector
from visual.collectors.sessione import SessioneCollector
from visual.collectors.sessions import SessionCollector
from visual.collectors.tokens import TokenLedgerCollector

# UNICA fonte dell'elenco dei collettori (la plancia importa questo, non ne ha uno suo).
# L'ordine e' quello dei riquadri in pagina, dalla domanda piu' urgente: «cosa sta
# succedendo adesso» viene prima di «cosa e' stato registrato».
ALL_COLLECTORS = (SessioneCollector, EventStoreCollector, SprintCollector,
                  CoordinamentoCollector, SessionCollector, TokenLedgerCollector,
                  CostAlertCollector)

__all__ = ["Collector", "Reading", "EventStoreCollector", "SprintCollector",
           "TokenLedgerCollector", "CoordinamentoCollector", "CostAlertCollector", "SessioneCollector", "SessionCollector",
           "ALL_COLLECTORS"]
