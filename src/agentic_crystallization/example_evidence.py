"""Synthetic API example, never live agent evidence."""
from .evidence_api import Evidence, Measurement, Protocol, CHANNELS


def example() -> Evidence:
    protocol = Protocol("demo-protocol", ("A", "B"), "fallback", "synthetic-task",
                        "demo-context", 24, .05, (1024, 1024, 1024), 0,
                        "Illustration: fixed paired draws from a frozen task distribution",
                        "Illustration only: independently justified honest reference required",
                        True, True)
    rows = tuple(Measurement(f"{channel}-{candidate}", candidate, "fallback",
                            channel, "synthetic-example", (gain,)*1024, -1, 1, 2, 3, .1)
                 for channel in CHANNELS for candidate, gain in (("A", .8), ("B", -.8)))
    return Evidence(protocol, 0, 1, 4, 20, rows)
