import os
import json
from datetime import datetime, date
from uuid import UUID, uuid4
from typing import List, Dict, Any, Optional
import requests

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_PORT", "8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin")

_BASE_URL = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}"


def _http_post(query: str, data: Optional[str] = None) -> requests.Response:
    url = _BASE_URL
    # Ensure ClickHouse ALTER UPDATE/DELETE wait for completion
    params = {"query": query, "mutations_sync": "1"}
    # Only send HTTP basic auth when both user and password are provided
    if CLICKHOUSE_USER and CLICKHOUSE_PASSWORD:
        auth = (CLICKHOUSE_USER, CLICKHOUSE_PASSWORD)
    else:
        auth = None
    if data is None:
        resp = requests.post(url, params=params, auth=auth)
    else:
        resp = requests.post(url, params=params, data=data.encode('utf-8'), auth=auth)
    
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # Include ClickHouse error details in exception
        error_body = ""
        try:
            error_body = resp.text
        except:
            error_body = "<unable to read response>"
        raise RuntimeError(
            f"ClickHouse error {resp.status_code}: {error_body}\n"
            f"Query: {query}\n"
            f"Data: {data[:500] if data else 'None'}"
        ) from e
    return resp


def init_tables():
    # Use PARTITION BY for time-based tables (monthly partitions) and
    # choose ORDER BY expressions that help the most common query patterns
    # Note: Cannot use Nullable columns in ORDER BY unless allow_nullable_key is enabled
    stmts = [
        "CREATE TABLE IF NOT EXISTS rooms (room_id UUID, name String, capacity Int32, has_equipment UInt8) ENGINE = MergeTree() ORDER BY (room_id)",
        "CREATE TABLE IF NOT EXISTS trainers (trainer_id UUID, name String, email Nullable(String), specialization String, rating Nullable(Float64), experience_years Nullable(Int32)) ENGINE = MergeTree() ORDER BY (trainer_id)",
        "CREATE TABLE IF NOT EXISTS payments (payment_id UUID, member_id String, class_id UUID, amount Float64, timestamp DateTime) ENGINE = MergeTree() PARTITION BY toYYYYMM(timestamp) ORDER BY (class_id, timestamp)",
        "CREATE TABLE IF NOT EXISTS classes (class_id UUID, name String, trainer_id Nullable(UUID), room_id Nullable(UUID), start_time DateTime, end_time DateTime, capacity Nullable(Int32), price Nullable(Float64), description Nullable(String)) ENGINE = MergeTree() PARTITION BY toYYYYMM(start_time) ORDER BY (start_time, class_id)",
        "CREATE TABLE IF NOT EXISTS attendances (event_id UUID, class_id UUID, member_id String, timestamp DateTime, status String) ENGINE = MergeTree() PARTITION BY toYYYYMM(timestamp) ORDER BY (class_id, timestamp, event_id)",
    ]
    for s in stmts:
        _http_post(s)


def select_all(table: str) -> List[Dict[str, Any]]:
    query = f"SELECT * FROM {table} FORMAT JSON"
    resp = _http_post(query)
    data = resp.json()
    # ClickHouse JSON returns 'data' key with rows
    return data.get("data", [])


def insert_one(table: str, obj: Dict[str, Any]):
    # use JSONEachRow format; provide single JSON object with newline
    query = f"INSERT INTO {table} FORMAT JSONEachRow"

    # before inserting, handle id generation and duplicate prevention
    id_field_map = {
        "rooms": "room_id",
        "trainers": "trainer_id",
        "payments": "payment_id",
        "classes": "class_id",
        "attendances": "event_id",
    }

    id_field = id_field_map.get(table)
    if id_field:
        # if id provided, ensure not duplicate
        if id_field in obj and obj.get(id_field) is not None:
            existing = select_one(table, id_field, str(obj[id_field]))
            if existing:
                raise ValueError(f"Duplicate {id_field} {obj[id_field]} for table {table}")
        else:
            # generate UUID for id
            obj[id_field] = str(uuid4())

    normalized = {k: _normalize(v) for k, v in obj.items()}
    body = json.dumps(normalized, default=str) + "\n"
    _http_post(query, data=body)
    
    # Return the generated or provided ID
    return obj.get(id_field) if id_field else None


def select_one(table: str, key: str, value: Any) -> Optional[Dict[str, Any]]:
    # naive equality select
    # For strings, add quotes
    if isinstance(value, (str, UUID)):
        val = f"'{value}'"
    else:
        val = str(value)
    query = f"SELECT * FROM {table} WHERE {key} = {val} FORMAT JSON"
    resp = _http_post(query)
    data = resp.json()
    rows = data.get("data", [])
    return rows[0] if rows else None


def select_by_filters(table: str, filters: Dict[str, Any], order_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """Select rows matching multiple filters with optional ordering"""
    if not filters:
        return select_all(table)
    
    where_clauses = []
    for key, value in filters.items():
        if value is None:
            continue
        if isinstance(value, (str, UUID)):
            where_clauses.append(f"{key} = '{value}'")
        elif isinstance(value, bool):
            where_clauses.append(f"{key} = {1 if value else 0}")
        else:
            where_clauses.append(f"{key} = {value}")
    
    if not where_clauses:
        return select_all(table)
    
    where_clause = " AND ".join(where_clauses)
    query = f"SELECT * FROM {table} WHERE {where_clause}"
    
    if order_by:
        query += f" ORDER BY {order_by}"
    
    query += " FORMAT JSON"
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


def update_one(table: str, key: str, value: Any, obj: Dict[str, Any]) -> bool:
    # Use ALTER TABLE UPDATE for updating records
    # mutations are async; this returns True if the request was accepted.
    normalized = {k: _normalize(v) for k, v in obj.items() if k != key}
    
    if not normalized:
        return True
    
    # Build SET clause
    set_clauses = []
    for col, val in normalized.items():
        if isinstance(val, str):
            set_clauses.append(f"{col} = '{val}'")
        elif val is None:
            set_clauses.append(f"{col} = NULL")
        else:
            set_clauses.append(f"{col} = {val}")
    
    set_clause = ", ".join(set_clauses)
    
    if isinstance(value, str):
        val = f"'{value}'"
    else:
        val = str(value)
    
    query = f"ALTER TABLE {table} UPDATE {set_clause} WHERE {key} = {val}"
    resp = _http_post(query)
    # If no exception was raised, consider the mutation accepted.
    return True


def delete_one(table: str, key: str, value: Any) -> bool:
    # mutations are async; this returns True if the request was accepted.
    if isinstance(value, str):
        val = f"'{value}'"
    else:
        val = str(value)
    query = f"ALTER TABLE {table} DELETE WHERE {key} = {val}"
    resp = _http_post(query)
    # If no exception was raised, consider the mutation accepted.
    return True

def _normalize(value: Any) -> Any:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        # Format without microseconds: YYYY-MM-DD HH:MM:SS
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value