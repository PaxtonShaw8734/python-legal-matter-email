import json
import os
from datetime import date
from pathlib import Path

from src.infrai_email import infrai
from src.matter_email import send_matter_email


def main() -> None:
    matter_path = Path(os.environ.get("MATTER_FILE", "matter.json"))
    matter = json.loads(matter_path.read_text(encoding="utf-8"))
    result = send_matter_email(matter, date.today(), infrai.email.send)
    print(json.dumps(result or {"status": "no message due"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
