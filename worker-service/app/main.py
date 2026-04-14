from __future__ import annotations

import asyncio

from src.workers.backup_worker import run_backup_loop


def main() -> None:
    asyncio.run(run_backup_loop())


if __name__ == "__main__":
    main()

