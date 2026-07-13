#!/usr/bin/env python3
"""
CLI untuk mengelola Project Tracker dari terminal.
Dapat dipanggil langsung oleh AI agent maupun user untuk input revisi,
melihat list project/task, mengedit, atau menghapus.
"""

import argparse
import json
import sys
from pathlib import Path

import tracker_backend as tb


def cmd_list_projects(args):
    projects = tb.list_projects()
    if not projects:
        print("Belum ada project.")
        return
    for i, name in enumerate(projects, 1):
        print(f"{i}. {name}")


def cmd_list_tasks(args):
    tasks = tb.list_tasks(project=args.project, status=args.status)
    if not tasks:
        print("Tidak ada task.")
        return
    for t in tasks:
        urgent = " [URGENT]" if t["urgent"] else ""
        img = f" (gambar: {t['image_count']})" if t["image_count"] else ""
        print(f"- [{t['id']}] {t['project']}{urgent}: {t['text'] or t['caption']}{img}")


def cmd_add_revision(args):
    images = [p.strip() for p in (args.images or []) if p.strip()]
    result = tb.add_revision(
        project=args.project,
        text=args.text,
        urgent=args.urgent,
        images=images or None,
    )
    print(f"Revisi berhasil ditambahkan (id={result['id']}).")


def cmd_add_project(args):
    tb.add_project(args.name)
    print(f"Project '{args.name}' berhasil ditambahkan.")


def cmd_edit_task(args):
    text = args.text if args.text is not None else None
    urgent = args.urgent if args.urgent is not None else None
    result = tb.edit_task(args.id, text=text, urgent=urgent)
    print(f"Task {result['id']} berhasil diperbarui.")


def cmd_delete_task(args):
    tb.delete_task(args.id)
    print(f"Task {args.id} berhasil dihapus.")


def cmd_complete_task(args):
    result = tb.complete_task(args.id)
    print(f"Task {result['id']} ditandai selesai.")


def cmd_delete_project(args):
    tb.delete_project(args.name)
    print(f"Project '{args.name}' beserta task-nya berhasil dihapus.")


def main():
    parser = argparse.ArgumentParser(
        description="Tracker CLI untuk Project Tracker (Supabase)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-projects", help="Tampilkan semua project")
    p.set_defaults(func=cmd_list_projects)

    p = sub.add_parser("list-tasks", help="Tampilkan task")
    p.add_argument("--project", help="Filter berdasarkan nama project")
    p.add_argument("--status", choices=["Belum", "Selesai", "all"], default="Belum")
    p.set_defaults(func=cmd_list_tasks)

    p = sub.add_parser("add-project", help="Buat project baru")
    p.add_argument("name", help="Nama project")
    p.set_defaults(func=cmd_add_project)

    p = sub.add_parser("delete-project", help="Hapus project")
    p.add_argument("name", help="Nama project")
    p.set_defaults(func=cmd_delete_project)

    p = sub.add_parser("add-revision", help="Tambah revisi/task ke project")
    p.add_argument("project", help="Nama project")
    p.add_argument("text", help="Isi revisi/caption")
    p.add_argument("--urgent", action="store_true", help="Tandai urgent")
    p.add_argument("--images", nargs="+", help="Satu atau lebih path gambar")
    p.set_defaults(func=cmd_add_revision)

    p = sub.add_parser("edit-task", help="Edit caption/urgent task")
    p.add_argument("id", help="ID task")
    p.add_argument("--text", help="Caption baru")
    p.add_argument("--urgent", type=lambda x: x.lower() in ("true", "1", "yes"), help="Urgent (true/false)")
    p.set_defaults(func=cmd_edit_task)

    p = sub.add_parser("delete-task", help="Hapus task")
    p.add_argument("id", help="ID task")
    p.set_defaults(func=cmd_delete_task)

    p = sub.add_parser("complete-task", help="Tandai task selesai")
    p.add_argument("id", help="ID task")
    p.set_defaults(func=cmd_complete_task)

    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
