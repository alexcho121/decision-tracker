"""Flask application for the cleaned Decision Tracker MVP."""

import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request, send_from_directory
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.db import decisions, make_engine, metadata, options, pros_cons

load_dotenv()


def utcnow():
    return datetime.utcnow()


def iso(value):
    return value.isoformat() + "Z" if value else None


def clean_text(value, max_length):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or len(value) > max_length:
        return None
    return value


def create_app(testing: bool = False, database_url: str | None = None) -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    frontend_dir = project_root / "frontend"

    app = Flask(__name__, static_folder=None)
    app.config["TESTING"] = bool(testing)
    app.config["DATABASE_URL"] = (
        database_url
        or os.getenv("DATABASE_URL", "").strip()
        or f"sqlite:///{project_root / 'decision_tracker.db'}"
    )

    engine = make_engine(app.config["DATABASE_URL"])
    app.config["DB_ENGINE"] = engine
    metadata.create_all(engine)

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "decision-tracker"}), 200

    @app.post("/api/decisions")
    def create_decision():
        data = request.get_json(silent=True) or {}
        title = clean_text(data.get("title"), 500)
        if not title:
            return jsonify({"error": "Title is required and must be 1-500 characters."}), 400

        now = utcnow()
        decision_id = str(uuid.uuid4())
        try:
            with engine.begin() as conn:
                conn.execute(insert(decisions).values(
                    id=decision_id,
                    title=title,
                    created_at=now,
                    updated_at=now,
                ))
        except SQLAlchemyError:
            return jsonify({"error": "Failed to save decision."}), 500

        return jsonify({
            "id": decision_id,
            "title": title,
            "created_at": iso(now),
            "updated_at": iso(now),
        }), 201

    @app.get("/api/decisions")
    def list_decisions():
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    select(decisions).order_by(decisions.c.created_at.desc())
                ).mappings().all()
        except SQLAlchemyError:
            return jsonify({"error": "Failed to load decisions."}), 500

        return jsonify([
            {
                "id": row["id"],
                "title": row["title"],
                "created_at": iso(row["created_at"]),
                "updated_at": iso(row["updated_at"]),
            }
            for row in rows
        ]), 200

    @app.get("/api/decisions/<decision_id>")
    def get_decision(decision_id):
        try:
            with engine.connect() as conn:
                decision = conn.execute(
                    select(decisions).where(decisions.c.id == decision_id)
                ).mappings().first()
                if not decision:
                    return jsonify({"error": "Decision not found."}), 404

                option_rows = conn.execute(
                    select(options)
                    .where(options.c.decision_id == decision_id)
                    .order_by(options.c.created_at.asc())
                ).mappings().all()

                option_ids = [row["id"] for row in option_rows]
                pc_by_option = {option_id: [] for option_id in option_ids}
                if option_ids:
                    pc_rows = conn.execute(
                        select(pros_cons)
                        .where(pros_cons.c.option_id.in_(option_ids))
                        .order_by(pros_cons.c.created_at.asc())
                    ).mappings().all()
                    for row in pc_rows:
                        pc_by_option[row["option_id"]].append({
                            "id": row["id"],
                            "option_id": row["option_id"],
                            "type": row["type"],
                            "text": row["text"],
                            "created_at": iso(row["created_at"]),
                            "updated_at": iso(row["updated_at"]),
                        })
        except SQLAlchemyError:
            return jsonify({"error": "Failed to load decision."}), 500

        return jsonify({
            "id": decision["id"],
            "title": decision["title"],
            "created_at": iso(decision["created_at"]),
            "updated_at": iso(decision["updated_at"]),
            "options": [
                {
                    "id": row["id"],
                    "decision_id": row["decision_id"],
                    "title": row["title"],
                    "is_selected": bool(row["is_selected"]),
                    "created_at": iso(row["created_at"]),
                    "updated_at": iso(row["updated_at"]),
                    "pros_and_cons": pc_by_option.get(row["id"], []),
                }
                for row in option_rows
            ],
        }), 200

    @app.delete("/api/decisions/<decision_id>")
    def delete_decision(decision_id):
        try:
            with engine.begin() as conn:
                result = conn.execute(delete(decisions).where(decisions.c.id == decision_id))
                if result.rowcount == 0:
                    return jsonify({"error": "Decision not found."}), 404
        except SQLAlchemyError:
            return jsonify({"error": "Failed to delete decision."}), 500
        return "", 204

    @app.post("/api/decisions/<decision_id>/options")
    def add_option(decision_id):
        data = request.get_json(silent=True) or {}
        title = clean_text(data.get("title"), 255)
        if not title:
            return jsonify({"error": "Option title is required and must be 1-255 characters."}), 400

        now = utcnow()
        option_id = str(uuid.uuid4())
        try:
            with engine.begin() as conn:
                exists = conn.execute(
                    select(decisions.c.id).where(decisions.c.id == decision_id)
                ).first()
                if not exists:
                    return jsonify({"error": "Decision not found."}), 404
                conn.execute(insert(options).values(
                    id=option_id,
                    decision_id=decision_id,
                    title=title,
                    is_selected=False,
                    created_at=now,
                    updated_at=now,
                ))
        except IntegrityError:
            return jsonify({"error": "Could not add option because the decision is invalid."}), 400
        except SQLAlchemyError:
            return jsonify({"error": "Failed to add option."}), 500

        return jsonify({
            "id": option_id,
            "decision_id": decision_id,
            "title": title,
            "is_selected": False,
            "created_at": iso(now),
            "updated_at": iso(now),
        }), 201

    @app.delete("/api/options/<option_id>")
    def delete_option(option_id):
        try:
            with engine.begin() as conn:
                result = conn.execute(delete(options).where(options.c.id == option_id))
                if result.rowcount == 0:
                    return jsonify({"error": "Option not found."}), 404
        except SQLAlchemyError:
            return jsonify({"error": "Failed to remove option."}), 500
        return "", 204

    @app.post("/api/options/<option_id>/pros-cons")
    def add_pro_con(option_id):
        data = request.get_json(silent=True) or {}
        item_type = data.get("type")
        item_text = clean_text(data.get("text"), 1000)
        if item_type not in {"pro", "con"}:
            return jsonify({"error": "Type must be 'pro' or 'con'."}), 400
        if not item_text:
            return jsonify({"error": "Text is required and must be 1-1000 characters."}), 400

        now = utcnow()
        item_id = str(uuid.uuid4())
        try:
            with engine.begin() as conn:
                exists = conn.execute(
                    select(options.c.id).where(options.c.id == option_id)
                ).first()
                if not exists:
                    return jsonify({"error": "Option not found."}), 404
                conn.execute(insert(pros_cons).values(
                    id=item_id,
                    option_id=option_id,
                    type=item_type,
                    text=item_text,
                    created_at=now,
                    updated_at=now,
                ))
        except SQLAlchemyError:
            return jsonify({"error": "Failed to save pro/con item."}), 500

        return jsonify({
            "id": item_id,
            "option_id": option_id,
            "type": item_type,
            "text": item_text,
            "created_at": iso(now),
            "updated_at": iso(now),
        }), 201

    @app.delete("/api/pros-cons/<item_id>")
    def delete_pro_con(item_id):
        try:
            with engine.begin() as conn:
                result = conn.execute(delete(pros_cons).where(pros_cons.c.id == item_id))
                if result.rowcount == 0:
                    return jsonify({"error": "Pro/con item not found."}), 404
        except SQLAlchemyError:
            return jsonify({"error": "Failed to remove pro/con item."}), 500
        return "", 204

    @app.post("/api/decisions/<decision_id>/select")
    def select_option(decision_id):
        data = request.get_json(silent=True) or {}
        option_id = data.get("option_id")
        if not isinstance(option_id, str) or not option_id.strip():
            return jsonify({"error": "option_id is required."}), 400

        try:
            with engine.begin() as conn:
                target = conn.execute(
                    select(options.c.id).where(
                        (options.c.id == option_id) &
                        (options.c.decision_id == decision_id)
                    )
                ).first()
                if not target:
                    return jsonify({"error": "Option not found for this decision."}), 404

                now = utcnow()
                conn.execute(
                    update(options)
                    .where(options.c.decision_id == decision_id)
                    .values(is_selected=False, updated_at=now)
                )
                conn.execute(
                    update(options)
                    .where(options.c.id == option_id)
                    .values(is_selected=True, updated_at=now)
                )
        except SQLAlchemyError:
            return jsonify({"error": "Failed to save final choice."}), 500

        return jsonify({"decision_id": decision_id, "selected_option_id": option_id}), 200

    @app.get("/")
    def frontend_index():
        return send_from_directory(frontend_dir, "index.html")

    @app.get("/<path:path>")
    def frontend_files(path):
        if path.startswith("api/"):
            abort(404)
        candidate = frontend_dir / path
        if not candidate.is_file():
            abort(404)
        return send_from_directory(frontend_dir, path)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
