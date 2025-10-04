import subprocess
import logging
from typing import Dict

log = logging.getLogger(__name__)

def run_sql_in_psql(sql_text: str, conn_info: Dict[str,str], dry_run=True):
    """
    Executes SQL against Postgres using psql CLI. For safety, we only run when dry_run=False.
    conn_info keys: host, port, db, user, password
    """
    if dry_run:
        log.info("dry-run: not executing SQL. SQL length: %d", len(sql_text))
        return {"status":"dry-run","sample": sql_text[:500]}
    
    env = {"PGPASSWORD": conn_info["password"]}
    psql_cmd = [
        "psql",
        "-h", conn_info["host"],
        "-p", str(conn_info["port"]),
        "-d", conn_info["db"],
        "-U", conn_info["user"],
        "-v", "ON_ERROR_STOP=1",
        "-w"
    ]
    proc = subprocess.run(psql_cmd, input=sql_text.encode("utf-8"), env={**env, **dict()}, capture_output=True)
    return {"stdout": proc.stdout.decode(), "stderr": proc.stderr.decode(), "returncode": proc.returncode}
