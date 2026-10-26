"""FleetLogix · generación de datos sintéticos (~535.000 registros) en PostgreSQL.

    python scripts/01_data_generation.py [--scale 1]

La lógica vive en `app/`: generadores por entidad (`app/generators`), sentencias SQL
(`app/db/statements.py`) y la fachada `ProjectIntegrator` (`app/core/integrator.py`).
"""
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.integrator import ProjectIntegrator  # noqa: E402
from app.db.postgres_manager import PostgresManager  # noqa: E402


def main(argv=None):
    from dotenv import load_dotenv

    parser = argparse.ArgumentParser(description="Genera datos sintéticos de FleetLogix en PostgreSQL.")
    parser.add_argument("--scale", type=int, default=1, help="Multiplicador de volumen (1 ≈ 535.000 registros)")
    args = parser.parse_args(argv)

    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    print("=" * 60 + "\nFleetLogix - Data Generation Pipeline\n" + "=" * 60)

    result = ProjectIntegrator(PostgresManager()).run_pipeline(scale_factor=args.scale)

    print("\n" + "=" * 60)
    print(f"Status: {result.status}\nDuration: {result.duration_seconds:.2f} seconds\n\nRecords Generated:")
    for entity, count in result.records_generated.items():
        print(f"  {entity}: {count:,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
