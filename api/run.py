import sys
from pathlib import Path

import uvicorn

sys.path.append(str(Path(__file__).parent.parent))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
        reload_includes=["*.py"],
        server_header=False,
        workers=1,
    )
