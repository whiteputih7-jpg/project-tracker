# MCP & CLI untuk Project Tracker

Repositori ini sekarang menyertakan **MCP server** dan **CLI** supaya AI agent (atau user) bisa mengelola project dan revisi tanpa harus membuka web.

## Prasyarat

```bash
pip install -r requirements_tracker.txt
```

Default URL/key Supabase sudah disematkan di `tracker_backend.py`, sama persis dengan yang dipakai `index.html`. Jika ingin mengganti, copy `.env.example` ke `.env` dan sesuaikan:

```bash
cp .env.example .env
# edit .env
```

## 1. CLI (`tracker_cli.py`)

Bisa dipakai langsung dari terminal atau oleh AI agent seperti Hermes untuk eksekusi perintah.

### Contoh perintah

```bash
# Lihat semua project
python tracker_cli.py list-projects

# Lihat task aktif
python tracker_cli.py list-tasks

# Lihat semua task (aktif + selesai)
python tracker_cli.py list-tasks --status all

# Lihat task untuk satu project
python tracker_cli.py list-tasks --project "JC HOUSE"

# Tambah revisi ke project
python tracker_cli.py add-revision "JC HOUSE" "Revisi tangga railing"

# Tambah revisi urgent
python tracker_cli.py add-revision "JC HOUSE" "URGENT: ganti warna dinding" --urgent

# Tambah revisi dengan gambar
python tracker_cli.py add-revision "JC HOUSE" "Revisi referensi" --images /path/foto1.jpg /path/foto2.jpg

# Edit task
python tracker_cli.py edit-task <ID> --text "Spesifikasi baru untuk pintu"

# Edit urgent task
python tracker_cli.py edit-task <ID> --urgent true

# Hapus task
python tracker_cli.py delete-task <ID>

# Tandai selesai
python tracker_cli.py complete-task <ID>

# Tambah/hapus project
python tracker_cli.py add-project "Nama Project"
python tracker_cli.py delete-project "Nama Project"
```

> ID task didapatkan dari perintah `list-tasks`.

## 2. MCP Server (`mcp_server.py`)

MCP server ini menggunakan transport **stdio** dan bisa dihubungkan ke AI agent yang mendukung Model Context Protocol (misal Claude Desktop, Continue, atau Hermes Agent bila dikonfigurasi sebagai MCP client).

### Tools yang tersedia

| Tool | Fungsi |
|------|--------|
| `list_projects` | Lihat semua project |
| `list_tasks` | Lihat task (filter project & status) |
| `add_revision` | Tambah revisi/task ke project, bisa sekaligus dengan gambar |
| `edit_task` | Edit caption & urgent task |
| `delete_task` | Hapus task |
| `complete_task` | Tandai task selesai |
| `add_project` | Buat project baru |
| `delete_project` | Hapus project |

### Menjalankan MCP server

```bash
python mcp_server.py
```

Server akan menunggu instruksi JSON-RPC melalui stdin/stdout.

### Menggunakan dengan Hermes Agent di Telegram

Karena Hermes Agent saat ini lebih sering memanggil CLI/terminal, cara termudah untuk sementara ialah menjalankan perintah CLI seperti contoh di atas. Jika di masa depan Hermes mendukung MCP config, Anda tinggal menambahkan:

```json
{
  "mcpServers": {
    "project-tracker": {
      "command": "python",
      "args": ["/path/ke/project-tracker/mcp_server.py"]
    }
  }
}
```

Setelah itu AI agent bisa memanggil semua tool di atas dalam percakapan.
