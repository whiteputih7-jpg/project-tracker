#!/usr/bin/env python3
"""
MCP (Model Context Protocol) server untuk Project Tracker.
Transport: stdio
Tools yang tersedia:
  - list_projects
  - list_tasks
  - add_revision
  - edit_task
  - delete_task
  - complete_task
  - add_project
  - delete_project
"""

import asyncio
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.types import Tool, TextContent

import tracker_backend as tb

app = Server("project-tracker-mcp")


TOOLS = [
    Tool(
        name="list_projects",
        description="Tampilkan semua nama project yang ada di Project Tracker.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="list_tasks",
        description="Tampilkan daftar task. Bisa difilter per project dan status.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Nama project (opsional). Kalau tidak diisi, tampil semua.",
                },
                "status": {
                    "type": "string",
                    "enum": ["Belum", "Selesai", "all"],
                    "default": "Belum",
                    "description": "Status task yang ingin ditampilkan.",
                },
            },
        },
    ),
    Tool(
        name="add_revision",
        description="Tambahkan revisi/task baru ke dalam project. Bisa menyertakan gambar.",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Nama project tujuan.",
                },
                "text": {
                    "type": "string",
                    "description": "Isi revisi/caption task.",
                },
                "urgent": {
                    "type": "boolean",
                    "default": False,
                    "description": "Apakah revisi ini urgent?",
                },
                "images": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Path ke file gambar lokal (opsional). Bisa lebih dari satu.",
                },
            },
            "required": ["project", "text"],
        },
    ),
    Tool(
        name="edit_task",
        description="Edit caption dan/atau status urgent dari task.",
        inputSchema={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "ID task.",
                },
                "text": {
                    "type": "string",
                    "description": "Caption baru (opsional).",
                },
                "urgent": {
                    "type": "boolean",
                    "description": "Status urgent baru (opsional).",
                },
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="delete_task",
        description="Hapus task berdasarkan ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "ID task yang akan dihapus.",
                },
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="complete_task",
        description="Tandai task sebagai selesai.",
        inputSchema={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "ID task.",
                },
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="add_project",
        description="Buat project baru.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nama project baru.",
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="delete_project",
        description="Hapus project beserta seluruh task-nya.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nama project yang akan dihapus.",
                },
            },
            "required": ["name"],
        },
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    arguments = arguments or {}

    if name == "list_projects":
        projects = tb.list_projects()
        text = "\n".join(f"- {p}" for p in projects) if projects else "Belum ada project."
        return [TextContent(type="text", text=text)]

    if name == "list_tasks":
        tasks = tb.list_tasks(
            project=arguments.get("project"),
            status=arguments.get("status", "Belum"),
        )
        if not tasks:
            return [TextContent(type="text", text="Tidak ada task.")]
        lines = []
        for t in tasks:
            urgent = " [URGENT]" if t["urgent"] else ""
            img = f" | gambar: {t['image_count']}" if t["image_count"] else ""
            lines.append(
                f"- [{t['id']}] {t['project']}{urgent}: {t['text'] or t['caption']}{img}"
            )
        return [TextContent(type="text", text="\n".join(lines))]

    if name == "add_revision":
        images = arguments.get("images") or None
        result = tb.add_revision(
            project=arguments["project"],
            text=arguments["text"],
            urgent=bool(arguments.get("urgent", False)),
            images=images,
        )
        return [
            TextContent(
                type="text",
                text=f"Revisi berhasil ditambahkan ke project '{result['project']}' (id={result['id']}).",
            )
        ]

    if name == "edit_task":
        result = tb.edit_task(
            arguments["id"],
            text=arguments.get("text"),
            urgent=arguments.get("urgent"),
        )
        return [TextContent(type="text", text=f"Task {result['id']} berhasil diperbarui.")]

    if name == "delete_task":
        tb.delete_task(arguments["id"])
        return [TextContent(type="text", text=f"Task {arguments['id']} berhasil dihapus.")]

    if name == "complete_task":
        result = tb.complete_task(arguments["id"])
        return [
            TextContent(
                type="text", text=f"Task {result['id']} ditandai selesai."
            )
        ]

    if name == "add_project":
        tb.add_project(arguments["name"])
        return [
            TextContent(
                type="text", text=f"Project '{arguments['name']}' berhasil dibuat."
            )
        ]

    if name == "delete_project":
        tb.delete_project(arguments["name"])
        return [
            TextContent(
                type="text",
                text=f"Project '{arguments['name']}' beserta task-nya berhasil dihapus.",
            )
        ]

    raise ValueError(f"Tool '{name}' tidak dikenali.")


async def main():
    # Run MCP server over stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="project-tracker-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
