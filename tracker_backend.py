"""
Backend helper untuk Project Tracker.
Berisi fungsi operasional CRUD project & task yang terhubung ke Supabase.
Bisa dipakai oleh CLI, MCP server, atau script lain.
"""

import os
import json
import base64
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jvmuuxihmvtdchittwhq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_LSd7KnvdVjxWr1FZKFSnyg_laZKWYiI")

_supabase: Optional[Client] = None


def get_supabase() -> Client:
    """Singleton Supabase client."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


def format_task(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "project": row.get("project_name"),
        "text": row.get("task"),
        "caption": row.get("caption") or "",
        "urgent": bool(row.get("urgent")),
        "status": row.get("status"),
        "date_created": row.get("date_created"),
        "date_completed": row.get("date_completed"),
        "image_count": _image_count(row.get("image_data")),
    }


def _image_count(image_data) -> int:
    if not image_data:
        return 0
    s = str(image_data).strip()
    if s.startswith("["):
        try:
            return len(json.loads(s))
        except Exception:
            return 0
    return 1


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_images(image_paths: Optional[list]) -> Optional[list]:
    """Konversi daftar path gambar menjadi array base64 data URL."""
    if not image_paths:
        return None
    results = []
    for path in image_paths:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Gambar tidak ditemukan: {path}")
        data = p.read_bytes()
        mime = _guess_mime(p.suffix)
        b64 = base64.b64encode(data).decode("ascii")
        results.append(f"data:{mime};base64,{b64}")
    return results


def _guess_mime(ext: str) -> str:
    ext = ext.lower()
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".bmp": "image/bmp",
    }
    return mapping.get(ext, "image/png")


def list_projects() -> list[str]:
    """Kembalikan list nama project."""
    sb = get_supabase()
    resp = sb.table("projects").select("name").order("created_at").execute()
    return [row["name"] for row in resp.data]


def list_tasks(project: Optional[str] = None, status: str = "Belum") -> list[dict]:
    """Kembalikan list task. Filter berdasarkan project dan status."""
    sb = get_supabase()
    q = sb.table("tasks").select("*")
    if project:
        q = q.eq("project_name", project)
    if status != "all":
        q = q.eq("status", status)
    q = q.order("date_created")
    resp = q.execute()
    return [format_task(row) for row in resp.data]


def add_revision(
    project: str,
    text: str,
    urgent: bool = False,
    images: Optional[list] = None,
) -> dict:
    """Tambahkan revisi/task baru ke sebuah project."""
    sb = get_supabase()
    image_data = None
    caption = text

    encoded_images = _read_images(images)
    if encoded_images:
        if len(encoded_images) == 1:
            image_data = encoded_images[0]
        else:
            image_data = json.dumps(encoded_images)
        if not text:
            caption = f"Task dengan {len(encoded_images)} gambar"

    if not image_data and not text:
        raise ValueError("Minimal berikan teks revisi atau satu gambar.")

    payload = {
        "project_name": project,
        "task": caption,
        "caption": text or "",
        "image_data": image_data,
        "urgent": urgent,
        "status": "Belum",
        "date_created": _now_iso(),
    }
    resp = sb.table("tasks").insert(payload).execute()
    return format_task(resp.data[0])


def edit_task(task_id: str, text: Optional[str] = None, urgent: Optional[bool] = None) -> dict:
    """Edit caption dan/atau status urgent dari task."""
    sb = get_supabase()
    payload: dict = {}
    if text is not None:
        payload["task"] = text
        payload["caption"] = text
    if urgent is not None:
        payload["urgent"] = urgent
    if not payload:
        raise ValueError("Tidak ada field yang akan diubah.")
    resp = sb.table("tasks").update(payload).eq("id", task_id).execute()
    if not resp.data:
        raise ValueError(f"Task dengan id {task_id} tidak ditemukan.")
    return format_task(resp.data[0])


def delete_task(task_id: str) -> None:
    """Hapus task berdasarkan ID."""
    sb = get_supabase()
    sb.table("tasks").delete().eq("id", task_id).execute()


def complete_task(task_id: str) -> dict:
    """Tandai task selesai."""
    sb = get_supabase()
    payload = {"status": "Selesai", "date_completed": _now_iso()}
    resp = sb.table("tasks").update(payload).eq("id", task_id).execute()
    if not resp.data:
        raise ValueError(f"Task dengan id {task_id} tidak ditemukan.")
    return format_task(resp.data[0])


def add_project(name: str) -> str:
    """Buat project baru."""
    sb = get_supabase()
    existing = sb.table("projects").select("name").eq("name", name).execute()
    if existing.data:
        raise ValueError(f"Project '{name}' sudah ada.")
    sb.table("projects").insert({"name": name}).execute()
    return name


def delete_project(name: str) -> None:
    """Hapus project beserta semua task-nya."""
    sb = get_supabase()
    # Hapus task terlebih dahulu
    sb.table("tasks").delete().eq("project_name", name).execute()
    sb.table("projects").delete().eq("name", name).execute()
