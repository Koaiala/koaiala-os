"""
KOAIALA ALERT OPERATIONS 22.2

Persistência dos alertas operacionais.
Não altera as tabelas do núcleo econômico.
"""

from src.database.connection import get_connection


def ensure_alert_table():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS koaiala_alerts (
                id BIGSERIAL PRIMARY KEY,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                code VARCHAR(120) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                source VARCHAR(80) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'NOVO'
            )
            """
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def save_alerts(alerts):
    ensure_alert_table()

    connection = get_connection()
    cursor = connection.cursor()
    try:
        for alert in alerts:
            cursor.execute(
                """
                INSERT INTO koaiala_alerts
                (code, severity, title, message, source)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    alert["code"],
                    alert["severity"],
                    alert["title"],
                    alert["message"],
                    alert["source"],
                ),
            )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_recent_alerts(limit=20):
    ensure_alert_table()

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT
                created_at,
                code,
                severity,
                title,
                message,
                source,
                status
            FROM koaiala_alerts
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (int(limit),),
        )

        rows = cursor.fetchall()

        return [
            {
                "created_at": row[0].isoformat(),
                "code": row[1],
                "severity": row[2],
                "title": row[3],
                "message": row[4],
                "source": row[5],
                "status": row[6],
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()
