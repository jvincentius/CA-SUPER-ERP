from __future__ import annotations

import html
import io
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "erp_beton.db"


MODULES = {
    "Dashboard": {"label": "Dashboard", "group": "Overview"},
    "Master": {"label": "Master", "group": "Core"},
    "Inventory": {"label": "Inventory", "group": "Core"},
    "Sales": {"label": "Sales", "group": "Operation"},
    "Purchase": {"label": "Purchase", "group": "Operation"},
    "Accounting": {"label": "Accounting", "group": "Finance"},
    "Transport": {"label": "Transport", "group": "Operation"},
    "HR": {"label": "HR", "group": "People"},
    "Reporting": {"label": "Reporting", "group": "Finance"},
    "Settings": {"label": "Settings", "group": "Admin"},
}


MASTER_PAGES = [
    "Customer",
    "Item",
    "Supplier",
    "Service",
    "Employee",
    "Chart of Account",
    "Plant",
    "Storage",
    "Driver",
    "Transportation",
]


st.set_page_config(
    page_title="ERP Beton Pracetak",
    page_icon="ERP",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --erp-bg: #f6f4f0;
            --erp-panel: #ffffff;
            --erp-border: #ddd8cf;
            --erp-text: #24201d;
            --erp-muted: #6d665d;
            --erp-accent: #2f7d57;
            --erp-accent-2: #b85c38;
            --erp-soft: #edf6f1;
            --erp-warning: #fff5df;
            --erp-sidebar: #26221f;
        }

        .stApp {
            background: var(--erp-bg);
            color: var(--erp-text);
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1440px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--erp-text);
        }

        h1 {
            font-size: 1.85rem;
            margin-bottom: 0.35rem;
        }

        h2 {
            font-size: 1.35rem;
        }

        h3 {
            font-size: 1.05rem;
        }

        section[data-testid="stSidebar"] {
            background: var(--erp-sidebar);
            border-right: 1px solid #3b3530;
        }

        section[data-testid="stSidebar"] * {
            color: #f7f2ea;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #cfc5b8;
        }

        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] .stMultiSelect label {
            color: #efe7dc !important;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] span,
        section[data-testid="stSidebar"] div[data-baseweb="select"] input,
        section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
            color: #24201d !important;
            fill: #24201d !important;
        }

        header[data-testid="stHeader"] {
            background: rgba(246, 244, 240, 0.92);
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: rgba(255, 255, 255, 0.055);
            border: 1px solid rgba(255, 255, 255, 0.075);
            border-radius: 8px;
            padding: 7px 9px;
            margin: 3px 0;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.11);
        }

        .erp-brand {
            padding: 12px 12px 10px;
            border-radius: 10px;
            background: #322d28;
            border: 1px solid rgba(255, 255, 255, 0.09);
            margin-bottom: 10px;
        }

        .erp-brand-title {
            font-size: 1.15rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .erp-brand-subtitle {
            color: #cfc5b8;
            font-size: 0.78rem;
            margin-top: 4px;
        }

        .erp-user-card {
            display: flex;
            gap: 10px;
            align-items: center;
            padding: 10px;
            border-radius: 10px;
            background: #f7f2ea;
            border: 1px solid #d6cab9;
            margin-bottom: 14px;
        }

        .erp-user-card * {
            color: #24201d !important;
        }

        .erp-avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--erp-accent);
            color: #ffffff !important;
            font-weight: 800;
            overflow: hidden;
            flex: 0 0 auto;
        }

        .erp-avatar img {
            width: 44px;
            height: 44px;
            object-fit: cover;
        }

        .erp-user-name {
            font-weight: 800;
            font-size: 0.95rem;
        }

        .erp-user-role {
            color: #6d665d !important;
            font-size: 0.78rem;
            margin-top: 2px;
        }

        .erp-note {
            background: var(--erp-soft);
            border: 1px solid #c9e5d6;
            border-left: 5px solid var(--erp-accent);
            border-radius: 8px;
            padding: 12px 14px;
            color: #244a37;
            margin: 0.6rem 0 1rem;
        }

        .erp-warning {
            background: var(--erp-warning);
            border: 1px solid #eed7a5;
            border-left: 5px solid #c7822f;
            border-radius: 8px;
            padding: 12px 14px;
            color: #624719;
            margin: 0.6rem 0 1rem;
        }

        .erp-page-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.4rem;
        }

        .erp-page-kicker {
            color: var(--erp-muted);
            font-size: 0.94rem;
            margin-top: -0.1rem;
            margin-bottom: 0.9rem;
        }

        .erp-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border-radius: 999px;
            border: 1px solid #d8d0c5;
            background: #fffdf9;
            color: #534b43;
            padding: 5px 10px;
            font-size: 0.78rem;
            font-weight: 700;
        }

        div[data-testid="stMetric"] {
            background: var(--erp-panel);
            border: 1px solid var(--erp-border);
            border-radius: 8px;
            padding: 12px 14px;
            box-shadow: 0 8px 20px rgba(46, 38, 30, 0.045);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--erp-border);
            border-radius: 8px;
            overflow: hidden;
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {
            border-radius: 8px !important;
            font-weight: 700 !important;
        }

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: var(--erp-accent) !important;
            border-color: var(--erp-accent) !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        textarea {
            border-radius: 8px !important;
        }

        .small-muted {
            color: var(--erp-muted);
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------


@st.cache_resource
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute(sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return get_conn().execute(sql, params).fetchone()


def fetch_df(sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_conn(), params=params)


def table_columns(table: str) -> set[str]:
    rows = get_conn().execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def ensure_column(table: str, column: str, definition: str) -> None:
    if column not in table_columns(table):
        execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            avatar_url TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );

        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            module_key TEXT NOT NULL,
            can_access INTEGER DEFAULT 1,
            UNIQUE(role_id, module_key),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            tax_id TEXT,
            payment_terms INTEGER DEFAULT 30,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            tax_id TEXT,
            payment_terms INTEGER DEFAULT 30,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            normal_balance TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            uom TEXT NOT NULL,
            unit_weight REAL DEFAULT 0,
            std_cost REAL DEFAULT 0,
            sales_price REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            uom TEXT DEFAULT 'Lot',
            unit_price REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT,
            department TEXT,
            phone TEXT,
            join_date TEXT,
            status TEXT DEFAULT 'Active',
            salary REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS storages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            plant_id INTEGER,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        );

        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            license_no TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transport_units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            plate_no TEXT NOT NULL,
            type TEXT,
            capacity_ton REAL DEFAULT 0,
            status TEXT DEFAULT 'Ready',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            movement_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            storage_id INTEGER NOT NULL,
            qty_in REAL DEFAULT 0,
            qty_out REAL DEFAULT 0,
            unit_cost REAL DEFAULT 0,
            ref_type TEXT,
            ref_no TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (storage_id) REFERENCES storages(id)
        );

        CREATE TABLE IF NOT EXISTS inventory_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count_no TEXT UNIQUE NOT NULL,
            count_date TEXT NOT NULL,
            storage_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Open',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (storage_id) REFERENCES storages(id)
        );

        CREATE TABLE IF NOT EXISTS inventory_count_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            system_qty REAL DEFAULT 0,
            counted_qty REAL DEFAULT 0,
            diff_qty REAL DEFAULT 0,
            FOREIGN KEY (count_id) REFERENCES inventory_counts(id),
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE TABLE IF NOT EXISTS sales_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            customer_id INTEGER NOT NULL,
            project_name TEXT,
            valid_until TEXT,
            status TEXT DEFAULT 'Submitted',
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS sales_estimate_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estimate_id INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            item_id INTEGER,
            service_id INTEGER,
            description TEXT,
            qty REAL DEFAULT 0,
            uom TEXT,
            price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (estimate_id) REFERENCES sales_estimates(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS sales_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            customer_id INTEGER NOT NULL,
            estimate_id INTEGER,
            project_name TEXT,
            delivery_date TEXT,
            status TEXT DEFAULT 'Submitted',
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (estimate_id) REFERENCES sales_estimates(id)
        );

        CREATE TABLE IF NOT EXISTS sales_order_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sales_order_id INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            item_id INTEGER,
            service_id INTEGER,
            description TEXT,
            qty REAL DEFAULT 0,
            uom TEXT,
            price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS production_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            sales_order_id INTEGER,
            item_id INTEGER NOT NULL,
            storage_id INTEGER,
            qty REAL DEFAULT 0,
            produced_qty REAL DEFAULT 0,
            due_date TEXT,
            status TEXT DEFAULT 'Open',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (storage_id) REFERENCES storages(id)
        );

        CREATE TABLE IF NOT EXISTS delivery_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            sales_order_id INTEGER,
            customer_id INTEGER NOT NULL,
            driver_id INTEGER,
            transport_unit_id INTEGER,
            status TEXT DEFAULT 'Posted',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (driver_id) REFERENCES drivers(id),
            FOREIGN KEY (transport_unit_id) REFERENCES transport_units(id)
        );

        CREATE TABLE IF NOT EXISTS delivery_order_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            storage_id INTEGER NOT NULL,
            qty REAL DEFAULT 0,
            uom TEXT,
            FOREIGN KEY (delivery_order_id) REFERENCES delivery_orders(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (storage_id) REFERENCES storages(id)
        );

        CREATE TABLE IF NOT EXISTS customer_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            customer_id INTEGER NOT NULL,
            sales_order_id INTEGER,
            due_date TEXT,
            status TEXT DEFAULT 'Posted',
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id)
        );

        CREATE TABLE IF NOT EXISTS customer_invoice_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            item_id INTEGER,
            service_id INTEGER,
            description TEXT,
            qty REAL DEFAULT 0,
            uom TEXT,
            price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES customer_invoices(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS purchase_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            employee_id INTEGER,
            required_date TEXT,
            status TEXT DEFAULT 'Submitted',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );

        CREATE TABLE IF NOT EXISTS purchase_request_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pr_id INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            item_id INTEGER,
            service_id INTEGER,
            description TEXT,
            qty REAL DEFAULT 0,
            uom TEXT,
            est_price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (pr_id) REFERENCES purchase_requests(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            supplier_id INTEGER NOT NULL,
            pr_id INTEGER,
            expected_date TEXT,
            status TEXT DEFAULT 'Submitted',
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (pr_id) REFERENCES purchase_requests(id)
        );

        CREATE TABLE IF NOT EXISTS purchase_order_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            item_id INTEGER,
            service_id INTEGER,
            description TEXT,
            qty REAL DEFAULT 0,
            uom TEXT,
            price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS supplier_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            supplier_id INTEGER NOT NULL,
            po_id INTEGER,
            storage_id INTEGER,
            due_date TEXT,
            status TEXT DEFAULT 'Posted',
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
            FOREIGN KEY (storage_id) REFERENCES storages(id)
        );

        CREATE TABLE IF NOT EXISTS supplier_invoice_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            item_id INTEGER,
            service_id INTEGER,
            description TEXT,
            qty REAL DEFAULT 0,
            uom TEXT,
            price REAL DEFAULT 0,
            total REAL DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES supplier_invoices(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            source_type TEXT,
            source_no TEXT,
            description TEXT,
            status TEXT DEFAULT 'Posted',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS journal_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            description TEXT,
            debit REAL DEFAULT 0,
            credit REAL DEFAULT 0,
            FOREIGN KEY (journal_id) REFERENCES journal_entries(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS cash_advances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            amount REAL DEFAULT 0,
            purpose TEXT,
            due_date TEXT,
            settlement_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Requested',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );

        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            acquisition_date TEXT,
            acquisition_cost REAL DEFAULT 0,
            useful_life_months INTEGER DEFAULT 60,
            accumulated_depr REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transport_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            usage_date TEXT NOT NULL,
            unit_id INTEGER NOT NULL,
            driver_id INTEGER,
            route TEXT,
            km_start REAL DEFAULT 0,
            km_end REAL DEFAULT 0,
            fuel_liter REAL DEFAULT 0,
            ref_doc TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES transport_units(id),
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        );

        CREATE TABLE IF NOT EXISTS delivery_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            cost_date TEXT NOT NULL,
            delivery_order_id INTEGER,
            unit_id INTEGER,
            cost_type TEXT,
            amount REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (delivery_order_id) REFERENCES delivery_orders(id),
            FOREIGN KEY (unit_id) REFERENCES transport_units(id)
        );

        CREATE TABLE IF NOT EXISTS hr_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_date TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Present',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """
    )
    conn.commit()
    migrate_db()
    seed_data()


def migrate_db() -> None:
    ensure_column("customers", "email", "TEXT")
    ensure_column("customers", "pic_name", "TEXT")
    ensure_column("customers", "pic_contact", "TEXT")
    ensure_column("suppliers", "email", "TEXT")
    ensure_column("suppliers", "pic_name", "TEXT")
    ensure_column("suppliers", "pic_contact", "TEXT")
    ensure_column("items", "conversion_factor", "REAL DEFAULT 1")
    ensure_column("services", "description", "TEXT")
    ensure_column("employees", "address", "TEXT")
    ensure_column("employees", "dob", "TEXT")
    ensure_column("employees", "birth_city", "TEXT")
    ensure_column("employees", "emergency_no", "TEXT")
    ensure_column("inventory_movements", "from_storage_id", "INTEGER")
    ensure_column("inventory_movements", "to_storage_id", "INTEGER")
    ensure_column("sales_estimates", "plant_id", "INTEGER")
    ensure_column("sales_estimates", "payment_terms_text", "TEXT")
    ensure_column("sales_estimates", "delivery_terms", "TEXT")
    ensure_column("sales_estimates", "qc_terms", "TEXT")
    ensure_column("sales_orders", "plant_id", "INTEGER")
    ensure_column("delivery_orders", "delivery_address", "TEXT")
    ensure_column("customer_invoices", "delivery_order_id", "INTEGER")
    ensure_column("cash_advances", "disbursed_at", "TEXT")
    ensure_column("cash_advances", "closed_at", "TEXT")
    ensure_column("cash_advances", "closing_notes", "TEXT")


def seed_data() -> None:
    conn = get_conn()

    if fetch_one("SELECT COUNT(*) AS c FROM roles")["c"] == 0:
        roles = [
            ("Administrator", "Akses penuh ke seluruh modul."),
            ("Sales Admin", "Sales, customer, delivery, dan reporting."),
            ("Warehouse", "Inventory, stock count, dan movement."),
            ("Finance", "Accounting, AP/AR, reporting."),
            ("Production", "Production order dan stock finished goods."),
            ("HR", "Employee dan attendance."),
        ]
        conn.executemany("INSERT INTO roles (name, description) VALUES (?, ?)", roles)

    role_rows = conn.execute("SELECT id, name FROM roles").fetchall()
    role_ids = {row["name"]: int(row["id"]) for row in role_rows}
    default_access = {
        "Administrator": list(MODULES.keys()),
        "Sales Admin": ["Dashboard", "Master", "Sales", "Inventory", "Transport", "Reporting"],
        "Warehouse": ["Dashboard", "Master", "Inventory", "Purchase", "Reporting"],
        "Finance": ["Dashboard", "Master", "Accounting", "Purchase", "Sales", "Reporting"],
        "Production": ["Dashboard", "Master", "Inventory", "Sales", "Reporting"],
        "HR": ["Dashboard", "Master", "HR", "Reporting"],
    }
    for role_name, modules in default_access.items():
        role_id = role_ids.get(role_name)
        if not role_id:
            continue
        for module_key in modules:
            conn.execute(
                """
                INSERT OR IGNORE INTO role_permissions (role_id, module_key, can_access)
                VALUES (?, ?, 1)
                """,
                (role_id, module_key),
            )

    if fetch_one("SELECT COUNT(*) AS c FROM users")["c"] == 0:
        conn.execute(
            """
            INSERT INTO users (username, full_name, role_id, avatar_url)
            VALUES (?, ?, ?, ?)
            """,
            ("admin", "Jason Admin", role_ids["Administrator"], ""),
        )

    if fetch_one("SELECT COUNT(*) AS c FROM accounts")["c"] == 0:
        accounts = [
            ("1000", "Cash / Bank", "Asset", "Debit"),
            ("1100", "Account Receivable", "Asset", "Debit"),
            ("1200", "Inventory", "Asset", "Debit"),
            ("1300", "Cash Advance", "Asset", "Debit"),
            ("1400", "Fixed Asset", "Asset", "Debit"),
            ("2000", "Account Payable", "Liability", "Credit"),
            ("2100", "VAT Output", "Liability", "Credit"),
            ("2200", "VAT Input", "Asset", "Debit"),
            ("3000", "Owner Equity", "Equity", "Credit"),
            ("4000", "Sales Revenue", "Revenue", "Credit"),
            ("5000", "Cost of Goods Sold", "Expense", "Debit"),
            ("5100", "Delivery Expense", "Expense", "Debit"),
            ("5200", "Payroll Expense", "Expense", "Debit"),
            ("5300", "Production Expense", "Expense", "Debit"),
            ("6000", "Operating Expense", "Expense", "Debit"),
        ]
        conn.executemany(
            "INSERT INTO accounts (code, name, type, normal_balance) VALUES (?, ?, ?, ?)",
            accounts,
        )

    if fetch_one("SELECT COUNT(*) AS c FROM plants")["c"] == 0:
        conn.execute(
            "INSERT INTO plants (code, name, address) VALUES (?, ?, ?)",
            ("PLT-01", "Plant Utama", "Area produksi utama"),
        )
        plant_id = conn.execute("SELECT id FROM plants WHERE code = 'PLT-01'").fetchone()["id"]
        conn.executemany(
            "INSERT INTO storages (code, name, plant_id) VALUES (?, ?, ?)",
            [
                ("STR-RM", "Gudang Raw Material", plant_id),
                ("STR-FG", "Yard Finished Goods", plant_id),
            ],
        )

    if fetch_one("SELECT COUNT(*) AS c FROM items")["c"] == 0:
        conn.executemany(
            """
            INSERT INTO items (code, name, category, uom, conversion_factor, unit_weight, std_cost, sales_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("RM-CEM", "Semen Bulk", "Raw Material", "Ton", 1, 1, 1050000, 0),
                ("RM-SND", "Pasir", "Raw Material", "M3", 1, 1.4, 220000, 0),
                ("RM-STN", "Batu Split", "Raw Material", "M3", 1, 1.5, 260000, 0),
                ("FG-UDT-60", "U-Ditch 60x60", "Finished Goods", "Pcs", 1, 0.42, 420000, 650000),
                ("FG-BC-100", "Box Culvert 100x100", "Finished Goods", "Pcs", 1, 1.2, 1250000, 1850000),
            ],
        )

    if fetch_one("SELECT COUNT(*) AS c FROM services")["c"] == 0:
        conn.executemany(
            "INSERT INTO services (code, name, uom, unit_price) VALUES (?, ?, ?, ?)",
            [
                ("SVC-DEL", "Jasa Pengiriman", "Trip", 1500000),
                ("SVC-CRN", "Sewa Crane", "Hari", 2500000),
            ],
        )

    if fetch_one("SELECT COUNT(*) AS c FROM customers")["c"] == 0:
        conn.execute(
            """
            INSERT INTO customers (code, name, phone, email, address, pic_name, pic_contact, tax_id, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "CUST-001",
                "PT Contoh Proyek Beton",
                "021-000000",
                "admin@customer.test",
                "Jakarta",
                "Ibu Rina",
                "0812000000",
                "",
                30,
            ),
        )

    if fetch_one("SELECT COUNT(*) AS c FROM suppliers")["c"] == 0:
        conn.execute(
            """
            INSERT INTO suppliers (code, name, phone, email, address, pic_name, pic_contact, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("SUP-001", "PT Supplier Material", "021-111111", "sales@supplier.test", "Bekasi", "Pak Agus", "0812111111", 30),
        )

    if fetch_one("SELECT COUNT(*) AS c FROM employees")["c"] == 0:
        conn.executemany(
            """
            INSERT INTO employees
            (code, name, address, phone, dob, birth_city, emergency_no, role, department, join_date, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "EMP-001",
                    "Budi Santoso",
                    "Bekasi",
                    "0812000001",
                    "1985-06-01",
                    "Bandung",
                    "0812999991",
                    "Admin Produksi",
                    "Production",
                    "2024-01-01",
                    6500000,
                ),
                (
                    "EMP-002",
                    "Siti Rahma",
                    "Jakarta",
                    "0812000002",
                    "1988-08-14",
                    "Jakarta",
                    "0812999992",
                    "Finance Staff",
                    "Finance",
                    "2024-02-01",
                    7000000,
                ),
            ],
        )

    if fetch_one("SELECT COUNT(*) AS c FROM drivers")["c"] == 0:
        conn.execute(
            "INSERT INTO drivers (code, name, phone, license_no) VALUES (?, ?, ?, ?)",
            ("DRV-001", "Agus", "0812333444", "SIM-B1-001"),
        )

    if fetch_one("SELECT COUNT(*) AS c FROM transport_units")["c"] == 0:
        conn.execute(
            "INSERT INTO transport_units (code, plate_no, type, capacity_ton) VALUES (?, ?, ?, ?)",
            ("TRK-001", "B 9001 ERP", "Truck", 12),
        )

    conn.commit()


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def money(value: float | int | None) -> str:
    amount = float(value or 0)
    return "Rp " + f"{amount:,.0f}".replace(",", ".")


def fmt_qty(value: float | int | None) -> str:
    return f"{float(value or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def today_iso() -> str:
    return date.today().isoformat()


def as_iso(value: date | datetime | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def parse_iso(value: str | None, fallback: date | None = None) -> date:
    if not value:
        return fallback or date.today()
    return datetime.fromisoformat(str(value)).date()


def next_doc_no(prefix: str, table: str, column: str = "doc_no") -> str:
    year = date.today().year
    like = f"{prefix}-{year}-%"
    row = fetch_one(
        f"SELECT {column} AS doc_no FROM {table} WHERE {column} LIKE ? ORDER BY {column} DESC LIMIT 1",
        (like,),
    )
    if row is None:
        seq = 1
    else:
        try:
            seq = int(str(row["doc_no"]).split("-")[-1]) + 1
        except ValueError:
            seq = 1
    return f"{prefix}-{year}-{seq:04d}"


def next_master_code(prefix: str, table: str) -> str:
    row = fetch_one("SELECT code FROM " + table + " WHERE code LIKE ? ORDER BY code DESC LIMIT 1", (f"{prefix}%",))
    if row is None:
        return f"{prefix}001"
    digits = "".join(ch for ch in row["code"] if ch.isdigit())
    seq = int(digits[-3:] or "0") + 1
    return f"{prefix}{seq:03d}"


def option_map(table: str, label_expr: str, where: str = "1=1", order_by: str = "id") -> dict[str, int]:
    df = fetch_df(f"SELECT id, {label_expr} AS label FROM {table} WHERE {where} ORDER BY {order_by}")
    return {str(row["label"]): int(row["id"]) for _, row in df.iterrows()}


def select_from_map(label: str, options: dict[str, int], key: str, default_id: int | None = None) -> int | None:
    if not options:
        st.warning(f"Data {label.lower()} belum tersedia.")
        return None
    labels = list(options.keys())
    index = 0
    if default_id:
        for i, item_label in enumerate(labels):
            if options[item_label] == default_id:
                index = i
                break
    return options[st.selectbox(label, labels, index=index, key=key)]


def show_df(df: pd.DataFrame, height: int = 360) -> None:
    if df.empty:
        st.info("Belum ada data.")
    else:
        st.dataframe(df, width="stretch", hide_index=True, height=height)


def note(text: str) -> None:
    st.markdown(f"<div class='erp-note'>{html.escape(text)}</div>", unsafe_allow_html=True)


def warning_note(text: str) -> None:
    st.markdown(f"<div class='erp-warning'>{html.escape(text)}</div>", unsafe_allow_html=True)


def page_title(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="erp-page-title">
            <div>
                <h1>{html.escape(title)}</h1>
                <div class="erp-page-kicker">{html.escape(subtitle)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_view(key: str) -> None:
    st.session_state[key] = "list"


def set_view(key: str, value: str) -> None:
    st.session_state[key] = value


def list_toolbar(title: str, create_label: str, view_key: str, edit_label: str | None = None) -> None:
    left, right = st.columns([0.62, 0.38])
    with left:
        st.subheader(title)
    with right:
        if edit_label:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(edit_label, width="stretch", key=f"{view_key}_edit_btn"):
                    set_view(view_key, "edit")
                    st.rerun()
            with c2:
                if st.button(create_label, type="primary", width="stretch", key=f"{view_key}_create_btn"):
                    set_view(view_key, "create")
                    st.rerun()
        else:
            if st.button(create_label, type="primary", width="stretch", key=f"{view_key}_create_btn"):
                set_view(view_key, "create")
                st.rerun()


def safe_text(value: Any, max_len: int = 90) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text[:max_len]


def df_to_excel_html_bytes(df: pd.DataFrame, title: str) -> bytes:
    safe_title = html.escape(title)
    body = df.to_html(index=False, escape=True)
    return f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body>
    <h2>{safe_title}</h2>
    {body}
    </body>
    </html>
    """.encode("utf-8")


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def df_to_simple_pdf_bytes(df: pd.DataFrame, title: str) -> bytes:
    cols = [str(c) for c in df.columns]
    lines = [title, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    lines.append(" | ".join(cols))
    lines.append("-" * 110)
    for _, row in df.head(45).iterrows():
        lines.append(" | ".join(safe_text(row.get(col, ""), 22) for col in cols))
    if len(df) > 45:
        lines.append(f"... {len(df) - 45} more rows")

    content_parts = ["BT", "/F1 8 Tf", "40 800 Td"]
    for idx, line in enumerate(lines):
        if idx:
            content_parts.append("0 -13 Td")
        content_parts.append(f"({pdf_escape(line)}) Tj")
    content_parts.append("ET")
    stream = "\n".join(content_parts).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode())
        out.write(obj)
        out.write(b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for offset in offsets:
        out.write(f"{offset:010d} 00000 n \n".encode())
    out.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return out.getvalue()


def export_buttons(df: pd.DataFrame, base_name: str, title: str) -> None:
    if df.empty:
        return
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Export Excel",
            data=df_to_excel_html_bytes(df, title),
            file_name=f"{base_name}.xls",
            mime="application/vnd.ms-excel",
            width="stretch",
        )
    with c2:
        st.download_button(
            "Export PDF",
            data=df_to_simple_pdf_bytes(df, title),
            file_name=f"{base_name}.pdf",
            mime="application/pdf",
            width="stretch",
        )


def current_stock(item_id: int, storage_id: int, as_of: str | None = None) -> float:
    params: list[Any] = [item_id, storage_id]
    date_filter = ""
    if as_of:
        date_filter = "AND doc_date <= ?"
        params.append(as_of)
    row = fetch_one(
        f"""
        SELECT COALESCE(SUM(qty_in - qty_out), 0) AS qty
        FROM inventory_movements
        WHERE item_id = ? AND storage_id = ? {date_filter}
        """,
        tuple(params),
    )
    return float(row["qty"] or 0)


def get_account_id(code: str) -> int:
    row = fetch_one("SELECT id FROM accounts WHERE code = ?", (code,))
    if not row:
        raise ValueError(f"Account {code} belum tersedia.")
    return int(row["id"])


def post_journal(
    *,
    doc_date: str,
    source_type: str,
    source_no: str,
    description: str,
    lines: list[dict[str, Any]],
) -> str:
    debit = round(sum(float(line.get("debit", 0) or 0) for line in lines), 2)
    credit = round(sum(float(line.get("credit", 0) or 0) for line in lines), 2)
    if abs(debit - credit) > 0.01:
        raise ValueError(f"Jurnal tidak balance. Debit {money(debit)}, Credit {money(credit)}.")

    doc_no = next_doc_no("GL", "journal_entries")
    conn = get_conn()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO journal_entries (doc_no, doc_date, source_type, source_no, description, status)
            VALUES (?, ?, ?, ?, ?, 'Posted')
            """,
            (doc_no, doc_date, source_type, source_no, description),
        )
        journal_id = cur.lastrowid
        for line in lines:
            conn.execute(
                """
                INSERT INTO journal_lines (journal_id, account_id, description, debit, credit)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    journal_id,
                    line.get("account_id") or get_account_id(str(line["account_code"])),
                    line.get("description", description),
                    float(line.get("debit", 0) or 0),
                    float(line.get("credit", 0) or 0),
                ),
            )
    return doc_no


def create_inventory_movement(
    *,
    doc_date: str,
    movement_type: str,
    item_id: int,
    storage_id: int,
    qty_in: float = 0,
    qty_out: float = 0,
    unit_cost: float = 0,
    ref_type: str = "",
    ref_no: str = "",
    notes: str = "",
    from_storage_id: int | None = None,
    to_storage_id: int | None = None,
) -> str:
    doc_no = next_doc_no("IM", "inventory_movements")
    execute(
        """
        INSERT INTO inventory_movements
        (doc_no, doc_date, movement_type, item_id, storage_id, qty_in, qty_out, unit_cost,
         ref_type, ref_no, notes, from_storage_id, to_storage_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc_no,
            doc_date,
            movement_type,
            item_id,
            storage_id,
            qty_in,
            qty_out,
            unit_cost,
            ref_type,
            ref_no,
            notes,
            from_storage_id,
            to_storage_id,
        ),
    )
    return doc_no


def catalog_options(include_services: bool = True, price_mode: str = "sales") -> dict[str, dict[str, Any]]:
    options: dict[str, dict[str, Any]] = {}
    items = fetch_df(
        """
        SELECT id, code, name, uom, std_cost, sales_price
        FROM items
        WHERE active = 1
        ORDER BY code
        """
    )
    for _, row in items.iterrows():
        label = f"ITEM | {row['code']} - {row['name']}"
        options[label] = {
            "line_type": "Item",
            "item_id": int(row["id"]),
            "service_id": None,
            "description": row["name"],
            "uom": row["uom"],
            "price": float(row["sales_price"] if price_mode == "sales" else row["std_cost"] or 0),
            "std_cost": float(row["std_cost"] or 0),
        }
    if include_services:
        services = fetch_df(
            "SELECT id, code, name, uom, unit_price FROM services WHERE active = 1 ORDER BY code"
        )
        for _, row in services.iterrows():
            label = f"SERVICE | {row['code']} - {row['name']}"
            options[label] = {
                "line_type": "Service",
                "item_id": None,
                "service_id": int(row["id"]),
                "description": row["name"],
                "uom": row["uom"],
                "price": float(row["unit_price"] or 0),
                "std_cost": 0,
            }
    return options


def line_editor(
    *,
    key: str,
    include_services: bool = True,
    price_mode: str = "sales",
    price_label: str = "Harga",
    initial_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    options = catalog_options(include_services=include_services, price_mode=price_mode)
    labels = list(options.keys())
    if not labels:
        st.warning("Item atau service belum tersedia.")
        return []

    if initial_rows:
        initial = pd.DataFrame(initial_rows)
    else:
        initial = pd.DataFrame(
            [{"catalog": labels[0], "description": "", "qty": 1.0, "uom": "", "price": 0.0}]
        )

    edited = st.data_editor(
        initial,
        key=key,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            "catalog": st.column_config.SelectboxColumn("Item / Service", options=labels, required=True, width="large"),
            "description": st.column_config.TextColumn("Deskripsi", width="large"),
            "qty": st.column_config.NumberColumn("Qty", min_value=0.0, step=1.0, format="%.2f"),
            "uom": st.column_config.TextColumn("Satuan"),
            "price": st.column_config.NumberColumn(price_label, min_value=0.0, step=1000.0, format="%.0f"),
        },
    )

    lines: list[dict[str, Any]] = []
    for _, row in edited.iterrows():
        catalog = row.get("catalog")
        if not catalog or catalog not in options:
            continue
        base = options[catalog]
        qty = float(row.get("qty") or 0)
        if qty <= 0:
            continue
        price = float(row.get("price") or 0) or float(base["price"] or 0)
        description = str(row.get("description") or "").strip() or str(base["description"])
        uom = str(row.get("uom") or "").strip() or str(base["uom"])
        lines.append(
            {
                "line_type": base["line_type"],
                "item_id": base["item_id"],
                "service_id": base["service_id"],
                "description": description,
                "qty": qty,
                "uom": uom,
                "price": price,
                "std_cost": float(base["std_cost"] or 0),
                "total": qty * price,
            }
        )
    if lines:
        st.caption(f"Total sementara: {money(sum(line['total'] for line in lines))}")
    return lines


def insert_lines(table: str, parent_col: str, parent_id: int, lines: list[dict[str, Any]], price_col: str = "price") -> None:
    conn = get_conn()
    for line in lines:
        conn.execute(
            f"""
            INSERT INTO {table}
            ({parent_col}, line_type, item_id, service_id, description, qty, uom, {price_col}, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                parent_id,
                line["line_type"],
                line["item_id"],
                line["service_id"],
                line["description"],
                line["qty"],
                line["uom"],
                line["price"],
                line["total"],
            ),
        )


# ---------------------------------------------------------------------------
# User, role, sidebar
# ---------------------------------------------------------------------------


def role_modules(role_id: int) -> list[str]:
    df = fetch_df(
        """
        SELECT module_key
        FROM role_permissions
        WHERE role_id = ? AND can_access = 1
        ORDER BY module_key
        """,
        (role_id,),
    )
    modules = [str(row["module_key"]) for _, row in df.iterrows() if row["module_key"] in MODULES]
    return modules or ["Dashboard"]


def get_current_user() -> sqlite3.Row:
    users = fetch_df(
        """
        SELECT u.id, u.username, u.full_name, u.avatar_url, r.id AS role_id, r.name AS role_name
        FROM users u
        JOIN roles r ON r.id = u.role_id
        WHERE u.active = 1
        ORDER BY u.full_name
        """
    )
    if users.empty:
        init_db()
        users = fetch_df(
            """
            SELECT u.id, u.username, u.full_name, u.avatar_url, r.id AS role_id, r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.active = 1
            ORDER BY u.full_name
            """
        )
    selected = st.session_state.get("current_user_id")
    if selected is None or int(selected) not in set(users["id"].tolist()):
        st.session_state["current_user_id"] = int(users.iloc[0]["id"])
    return fetch_one(
        """
        SELECT u.id, u.username, u.full_name, u.avatar_url, r.id AS role_id, r.name AS role_name
        FROM users u
        JOIN roles r ON r.id = u.role_id
        WHERE u.id = ?
        """,
        (int(st.session_state["current_user_id"]),),
    )


def initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    if not parts:
        return "U"
    return "".join(part[0].upper() for part in parts[:2])


def render_user_card(user: sqlite3.Row) -> None:
    name = str(user["full_name"])
    role = str(user["role_name"])
    avatar_url = str(user["avatar_url"] or "").strip()
    if avatar_url:
        avatar = f"<img src='{html.escape(avatar_url)}' alt='avatar'>"
    else:
        avatar = initials(name)
    st.sidebar.markdown(
        f"""
        <div class="erp-brand">
            <div class="erp-brand-title">ERP Beton</div>
            <div class="erp-brand-subtitle">Precast manufacturing system</div>
        </div>
        <div class="erp-user-card">
            <div class="erp-avatar">{avatar}</div>
            <div>
                <div class="erp-user-name">{html.escape(name)}</div>
                <div class="erp-user-role">{html.escape(role)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, sqlite3.Row]:
    user = get_current_user()
    render_user_card(user)

    users = fetch_df(
        """
        SELECT u.id, u.full_name || ' - ' || r.name AS label
        FROM users u
        JOIN roles r ON r.id = u.role_id
        WHERE u.active = 1
        ORDER BY u.full_name
        """
    )
    user_options = {str(row["label"]): int(row["id"]) for _, row in users.iterrows()}
    current_label = next((label for label, user_id in user_options.items() if user_id == int(user["id"])), list(user_options)[0])
    picked = st.sidebar.selectbox("User aktif", list(user_options.keys()), index=list(user_options.keys()).index(current_label))
    if user_options[picked] != int(user["id"]):
        st.session_state["current_user_id"] = user_options[picked]
        st.rerun()

    allowed = role_modules(int(user["role_id"]))
    grouped_labels = []
    for group in ["Overview", "Core", "Operation", "Finance", "People", "Admin"]:
        group_modules = [key for key, meta in MODULES.items() if meta["group"] == group and key in allowed]
        if group_modules:
            grouped_labels.extend(group_modules)

    st.sidebar.divider()
    module = st.sidebar.radio(
        "Menu",
        grouped_labels,
        format_func=lambda key: MODULES[key]["label"],
        key="main_module",
    )
    st.sidebar.divider()
    st.sidebar.caption(f"Role: {user['role_name']}")
    st.sidebar.caption(f"Database: {DB_PATH.name}")
    return module, get_current_user()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


def render_dashboard() -> None:
    page_title("Dashboard", "Ringkasan operasional untuk inventory, piutang, hutang, dan produksi.")
    ar = fetch_one("SELECT COALESCE(SUM(total - paid_amount), 0) AS amount FROM customer_invoices WHERE status = 'Posted'")[
        "amount"
    ]
    ap = fetch_one("SELECT COALESCE(SUM(total - paid_amount), 0) AS amount FROM supplier_invoices WHERE status = 'Posted'")[
        "amount"
    ]
    stock_sku = fetch_one(
        """
        SELECT COUNT(*) AS c
        FROM (
            SELECT item_id, SUM(qty_in - qty_out) AS qty
            FROM inventory_movements
            GROUP BY item_id
            HAVING qty > 0
        )
        """
    )["c"]
    open_prod = fetch_one("SELECT COUNT(*) AS c FROM production_orders WHERE status != 'Closed'")["c"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Outstanding AR", money(ar))
    c2.metric("Outstanding AP", money(ap))
    c3.metric("SKU Ada Stock", int(stock_sku or 0))
    c4.metric("Production Order Open", int(open_prod or 0))

    left, right = st.columns(2)
    with left:
        st.subheader("Stock per Item")
        stock_df = fetch_df(
            """
            SELECT i.code, i.name, COALESCE(SUM(m.qty_in - m.qty_out), 0) AS qty
            FROM items i
            LEFT JOIN inventory_movements m ON m.item_id = i.id
            GROUP BY i.id
            ORDER BY i.code
            """
        )
        if not stock_df.empty:
            st.bar_chart(stock_df.set_index("code")["qty"])
        show_df(stock_df, height=230)
    with right:
        st.subheader("Invoice Terakhir")
        inv_df = fetch_df(
            """
            SELECT ci.doc_no, ci.doc_date, c.name AS customer, ci.total,
                   ci.paid_amount, ci.total - ci.paid_amount AS outstanding
            FROM customer_invoices ci
            JOIN customers c ON c.id = ci.customer_id
            ORDER BY ci.id DESC
            LIMIT 10
            """
        )
        show_df(inv_df, height=320)


# ---------------------------------------------------------------------------
# Master
# ---------------------------------------------------------------------------


def master_list_df(page: str) -> pd.DataFrame:
    if page == "Customer":
        return fetch_df(
            """
            SELECT code AS Kode, name AS Nama, address AS Alamat, phone AS "No Telp",
                   email AS Email, pic_name AS PIC, pic_contact AS "Contact PIC", tax_id AS NPWP
            FROM customers
            ORDER BY id DESC
            """
        )
    if page == "Supplier":
        return fetch_df(
            """
            SELECT code AS Kode, name AS Nama, address AS Alamat, phone AS "No Telp",
                   email AS Email, pic_name AS PIC, pic_contact AS "Contact PIC"
            FROM suppliers
            ORDER BY id DESC
            """
        )
    if page == "Item":
        return fetch_df(
            """
            SELECT code AS Kode, name AS Nama, uom AS Satuan, conversion_factor AS Konversi,
                   category AS Kategori, std_cost AS "Std Cost", sales_price AS "Harga Jual"
            FROM items
            ORDER BY id DESC
            """
        )
    if page == "Service":
        return fetch_df("SELECT code AS Kode, name AS Nama, uom AS Satuan, unit_price AS Harga FROM services ORDER BY id DESC")
    if page == "Employee":
        return fetch_df(
            """
            SELECT code AS Kode, name AS Nama, address AS Alamat, phone AS "No Telepon",
                   dob AS DOB, birth_city AS "Kota Kelahiran", emergency_no AS "Emergency No"
            FROM employees
            ORDER BY id DESC
            """
        )
    if page == "Chart of Account":
        return fetch_df(
            """
            SELECT code AS Kode, name AS Nama, type AS Tipe, normal_balance AS "Saldo Normal", active AS Aktif
            FROM accounts
            ORDER BY code
            """
        )
    if page == "Plant":
        return fetch_df("SELECT code AS Kode, name AS Nama, address AS Alamat, active AS Aktif FROM plants ORDER BY id DESC")
    if page == "Storage":
        return fetch_df(
            """
            SELECT s.code AS Kode, s.name AS Nama, p.name AS Plant, s.active AS Aktif
            FROM storages s
            LEFT JOIN plants p ON p.id = s.plant_id
            ORDER BY s.id DESC
            """
        )
    if page == "Driver":
        return fetch_df("SELECT code AS Kode, name AS Nama, phone AS Telepon, license_no AS SIM, active AS Aktif FROM drivers ORDER BY id DESC")
    return fetch_df(
        """
        SELECT code AS Kode, plate_no AS "Nomor Polisi", type AS Tipe, capacity_ton AS "Kapasitas Ton", status AS Status
        FROM transport_units
        ORDER BY id DESC
        """
    )


def select_value(label: str, options: list[str], value: Any, key: str) -> str:
    current = str(value or "")
    index = options.index(current) if current in options else 0
    return st.selectbox(label, options, index=index, key=key)


def master_table(page: str) -> str:
    return {
        "Customer": "customers",
        "Supplier": "suppliers",
        "Item": "items",
        "Service": "services",
        "Employee": "employees",
        "Chart of Account": "accounts",
        "Plant": "plants",
        "Storage": "storages",
        "Driver": "drivers",
        "Transportation": "transport_units",
    }[page]


def master_record_options(page: str) -> dict[str, int]:
    table = master_table(page)
    if page == "Transportation":
        label_expr = "code || ' - ' || plate_no"
    else:
        label_expr = "code || ' - ' || name"
    return option_map(table, label_expr, "1=1", "code")


def render_master_create(page: str, view_key: str) -> None:
    if st.button("Kembali ke list", key=f"{view_key}_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader(f"Create New {page}")
    with st.form(f"create_{page}"):
        payload: dict[str, Any] = {}
        if page == "Customer":
            st.caption(f"Kode otomatis: {next_master_code('CUST-', 'customers')}")
            payload["code"] = next_master_code("CUST-", "customers")
            payload["name"] = st.text_input("Nama")
            payload["address"] = st.text_area("Alamat")
            payload["phone"] = st.text_input("No Telp")
            payload["email"] = st.text_input("Alamat Email")
            payload["pic_name"] = st.text_input("PIC")
            payload["pic_contact"] = st.text_input("Contact PIC")
            payload["tax_id"] = st.text_input("NPWP")
            table = "customers"
        elif page == "Supplier":
            st.caption(f"Kode otomatis: {next_master_code('SUP-', 'suppliers')}")
            payload["code"] = next_master_code("SUP-", "suppliers")
            payload["name"] = st.text_input("Nama")
            payload["address"] = st.text_area("Alamat")
            payload["phone"] = st.text_input("No Telp")
            payload["email"] = st.text_input("Alamat Email")
            payload["pic_name"] = st.text_input("PIC")
            payload["pic_contact"] = st.text_input("Contact PIC")
            table = "suppliers"
        elif page == "Item":
            payload["code"] = st.text_input("Kode", value="ITEM-")
            payload["name"] = st.text_input("Nama")
            payload["uom"] = st.selectbox("Satuan", ["Pcs", "M3", "Ton", "Kg", "Liter", "Lot", "Trip"])
            payload["conversion_factor"] = st.number_input("Konversi", min_value=0.0001, value=1.0, step=1.0)
            payload["category"] = st.selectbox("Kategori", ["Raw Material", "Finished Goods", "Consumable", "Asset"])
            payload["std_cost"] = st.number_input("Standard Cost", min_value=0.0, value=0.0, step=1000.0)
            payload["sales_price"] = st.number_input("Harga Jual", min_value=0.0, value=0.0, step=1000.0)
            table = "items"
        elif page == "Service":
            payload["code"] = st.text_input("Kode", value="SVC-")
            payload["name"] = st.text_input("Nama")
            payload["uom"] = st.selectbox("Satuan", ["Lot", "Trip", "Hari", "Jam", "Bulan"])
            payload["unit_price"] = st.number_input("Harga Referensi", min_value=0.0, value=0.0, step=1000.0)
            table = "services"
        elif page == "Employee":
            payload["code"] = st.text_input("Kode", value="EMP-")
            payload["name"] = st.text_input("Nama")
            payload["address"] = st.text_area("Alamat")
            payload["phone"] = st.text_input("No Telepon")
            payload["dob"] = as_iso(st.date_input("DOB", value=date(1990, 1, 1)))
            payload["birth_city"] = st.text_input("Kota Kelahiran")
            payload["emergency_no"] = st.text_input("Emergency No")
            payload["status"] = "Active"
            table = "employees"
        elif page == "Chart of Account":
            payload["code"] = st.text_input("Kode")
            payload["name"] = st.text_input("Nama")
            payload["type"] = st.selectbox("Tipe", ["Asset", "Liability", "Equity", "Revenue", "Expense"])
            payload["normal_balance"] = st.selectbox("Saldo Normal", ["Debit", "Credit"])
            payload["active"] = 1
            table = "accounts"
        elif page == "Plant":
            payload["code"] = st.text_input("Kode", value="PLT-")
            payload["name"] = st.text_input("Nama")
            payload["address"] = st.text_area("Alamat")
            payload["active"] = 1
            table = "plants"
        elif page == "Storage":
            payload["code"] = st.text_input("Kode", value="STR-")
            payload["name"] = st.text_input("Nama")
            payload["plant_id"] = select_from_map("Plant", option_map("plants", "code || ' - ' || name", "active = 1", "code"), "new_storage_plant")
            payload["active"] = 1
            table = "storages"
        elif page == "Driver":
            payload["code"] = st.text_input("Kode", value="DRV-")
            payload["name"] = st.text_input("Nama")
            payload["phone"] = st.text_input("Telepon")
            payload["license_no"] = st.text_input("Nomor SIM")
            payload["active"] = 1
            table = "drivers"
        else:
            payload["code"] = st.text_input("Kode Unit", value="TRK-")
            payload["plate_no"] = st.text_input("Nomor Polisi")
            payload["type"] = st.selectbox("Tipe", ["Truck", "Trailer", "Mixer", "Pickup", "Other"])
            payload["capacity_ton"] = st.number_input("Kapasitas Ton", min_value=0.0, value=0.0, step=1.0)
            payload["status"] = st.selectbox("Status", ["Ready", "Used", "Maintenance", "Inactive"])
            table = "transport_units"

        submitted = st.form_submit_button("Simpan", type="primary")
        if submitted:
            if not payload.get("name") and page not in {"Transportation"}:
                st.error("Nama wajib diisi.")
                return
            columns = ", ".join(payload.keys())
            placeholders = ", ".join(["?"] * len(payload))
            try:
                execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(payload.values()))
                st.success("Data berhasil disimpan.")
                reset_view(view_key)
                st.rerun()
            except sqlite3.IntegrityError as exc:
                st.error(f"Gagal menyimpan. Cek kode unik. Detail: {exc}")


def render_master_edit(page: str, view_key: str) -> None:
    if st.button("Kembali ke list", key=f"{view_key}_edit_back"):
        reset_view(view_key)
        st.rerun()

    table = master_table(page)
    options = master_record_options(page)
    if not options:
        st.info("Belum ada data untuk diedit.")
        return

    st.subheader(f"Edit {page}")
    selected_id = select_from_map("Pilih Data", options, f"{view_key}_edit_select")
    if not selected_id:
        return

    record = fetch_one(f"SELECT * FROM {table} WHERE id = ?", (selected_id,))
    if not record:
        st.error("Data tidak ditemukan.")
        return

    with st.form(f"edit_{page}_{selected_id}"):
        payload: dict[str, Any] = {}
        if page == "Customer":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["address"] = st.text_area("Alamat", value=record["address"] or "")
            payload["phone"] = st.text_input("No Telp", value=record["phone"] or "")
            payload["email"] = st.text_input("Alamat Email", value=record["email"] or "")
            payload["pic_name"] = st.text_input("PIC", value=record["pic_name"] or "")
            payload["pic_contact"] = st.text_input("Contact PIC", value=record["pic_contact"] or "")
            payload["tax_id"] = st.text_input("NPWP", value=record["tax_id"] or "")
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Supplier":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["address"] = st.text_area("Alamat", value=record["address"] or "")
            payload["phone"] = st.text_input("No Telp", value=record["phone"] or "")
            payload["email"] = st.text_input("Alamat Email", value=record["email"] or "")
            payload["pic_name"] = st.text_input("PIC", value=record["pic_name"] or "")
            payload["pic_contact"] = st.text_input("Contact PIC", value=record["pic_contact"] or "")
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Item":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["uom"] = select_value("Satuan", ["Pcs", "M3", "Ton", "Kg", "Liter", "Lot", "Trip"], record["uom"], f"{view_key}_uom")
            payload["conversion_factor"] = st.number_input(
                "Konversi", min_value=0.0001, value=float(record["conversion_factor"] or 1), step=1.0
            )
            payload["category"] = select_value(
                "Kategori",
                ["Raw Material", "Finished Goods", "Consumable", "Asset"],
                record["category"],
                f"{view_key}_category",
            )
            payload["std_cost"] = st.number_input("Standard Cost", min_value=0.0, value=float(record["std_cost"] or 0), step=1000.0)
            payload["sales_price"] = st.number_input("Harga Jual", min_value=0.0, value=float(record["sales_price"] or 0), step=1000.0)
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Service":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["uom"] = select_value("Satuan", ["Lot", "Trip", "Hari", "Jam", "Bulan"], record["uom"], f"{view_key}_svc_uom")
            payload["unit_price"] = st.number_input("Harga Referensi", min_value=0.0, value=float(record["unit_price"] or 0), step=1000.0)
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Employee":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["address"] = st.text_area("Alamat", value=record["address"] or "")
            payload["phone"] = st.text_input("No Telepon", value=record["phone"] or "")
            payload["dob"] = as_iso(st.date_input("DOB", value=parse_iso(record["dob"], date(1990, 1, 1))))
            payload["birth_city"] = st.text_input("Kota Kelahiran", value=record["birth_city"] or "")
            payload["emergency_no"] = st.text_input("Emergency No", value=record["emergency_no"] or "")
            payload["status"] = select_value("Status", ["Active", "Inactive", "Resigned"], record["status"], f"{view_key}_emp_status")
        elif page == "Chart of Account":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["type"] = select_value("Tipe", ["Asset", "Liability", "Equity", "Revenue", "Expense"], record["type"], f"{view_key}_acct_type")
            payload["normal_balance"] = select_value("Saldo Normal", ["Debit", "Credit"], record["normal_balance"], f"{view_key}_acct_normal")
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Plant":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["address"] = st.text_area("Alamat", value=record["address"] or "")
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Storage":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["plant_id"] = select_from_map(
                "Plant",
                option_map("plants", "code || ' - ' || name", "active = 1", "code"),
                f"{view_key}_storage_plant",
                default_id=int(record["plant_id"] or 0) or None,
            )
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        elif page == "Driver":
            payload["code"] = st.text_input("Kode", value=record["code"] or "")
            payload["name"] = st.text_input("Nama", value=record["name"] or "")
            payload["phone"] = st.text_input("Telepon", value=record["phone"] or "")
            payload["license_no"] = st.text_input("Nomor SIM", value=record["license_no"] or "")
            payload["active"] = 1 if st.checkbox("Aktif", value=bool(record["active"])) else 0
        else:
            payload["code"] = st.text_input("Kode Unit", value=record["code"] or "")
            payload["plate_no"] = st.text_input("Nomor Polisi", value=record["plate_no"] or "")
            payload["type"] = select_value("Tipe", ["Truck", "Trailer", "Mixer", "Pickup", "Other"], record["type"], f"{view_key}_unit_type")
            payload["capacity_ton"] = st.number_input("Kapasitas Ton", min_value=0.0, value=float(record["capacity_ton"] or 0), step=1.0)
            payload["status"] = select_value("Status", ["Ready", "Used", "Maintenance", "Inactive"], record["status"], f"{view_key}_unit_status")

        submitted = st.form_submit_button("Update", type="primary")
        if submitted:
            if page != "Transportation" and not str(payload.get("name") or "").strip():
                st.error("Nama wajib diisi.")
                return
            if page == "Transportation" and not str(payload.get("plate_no") or "").strip():
                st.error("Nomor Polisi wajib diisi.")
                return
            assignments = ", ".join([f"{column} = ?" for column in payload.keys()])
            try:
                execute(f"UPDATE {table} SET {assignments} WHERE id = ?", tuple(payload.values()) + (selected_id,))
                st.success("Data berhasil diupdate.")
                reset_view(view_key)
                st.rerun()
            except sqlite3.IntegrityError as exc:
                st.error(f"Gagal update. Cek kode unik. Detail: {exc}")


def render_master() -> None:
    page_title("Master", "Semua master data dibuka dari list terlebih dahulu, lalu user membuat data baru bila diperlukan.")
    page = st.sidebar.radio("Master Data", MASTER_PAGES, key="master_page")
    view_key = f"master_view_{page}"
    st.session_state.setdefault(view_key, "list")

    if st.session_state[view_key] == "list":
        list_toolbar(page, "Create New", view_key, edit_label="Edit Existing")
        df = master_list_df(page)
        show_df(df)
        export_buttons(df, f"master_{page.lower().replace(' ', '_')}", f"Master {page}")
    elif st.session_state[view_key] == "create":
        render_master_create(page, view_key)
    else:
        render_master_edit(page, view_key)


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


def stock_card_page() -> None:
    st.subheader("Stock Card")
    note("Filter stock card bisa berdasarkan kata kunci item, plant, storage, dan posisi stock per tanggal tertentu.")

    plants = {"Semua Plant": None}
    plants.update(option_map("plants", "code || ' - ' || name", "active = 1", "code"))
    storages = {"Semua Storage": None}
    storages.update(option_map("storages", "code || ' - ' || name", "active = 1", "code"))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        keyword = st.text_input("Cari Item", placeholder="Kode atau nama")
        match_mode = st.radio("Mode", ["Containing", "Start With"], horizontal=True)
    with c2:
        plant_label = st.selectbox("Plant", list(plants.keys()))
    with c3:
        storage_label = st.selectbox("Storage", list(storages.keys()))
    with c4:
        as_of = st.date_input("As Per Date", value=date.today())

    filters = ["m.doc_date <= ?"]
    params: list[Any] = [as_iso(as_of)]
    if keyword.strip():
        if match_mode == "Start With":
            filters.append("(i.code LIKE ? OR i.name LIKE ?)")
            params.extend([f"{keyword.strip()}%", f"{keyword.strip()}%"])
        else:
            filters.append("(i.code LIKE ? OR i.name LIKE ?)")
            params.extend([f"%{keyword.strip()}%", f"%{keyword.strip()}%"])
    if plants[plant_label]:
        filters.append("p.id = ?")
        params.append(plants[plant_label])
    if storages[storage_label]:
        filters.append("s.id = ?")
        params.append(storages[storage_label])

    where_sql = " AND ".join(filters)
    summary = fetch_df(
        f"""
        SELECT p.code AS plant, s.code AS storage, i.code AS item_code, i.name AS item_name,
               i.uom, COALESCE(SUM(m.qty_in - m.qty_out), 0) AS balance_qty,
               COALESCE(SUM((m.qty_in - m.qty_out) * m.unit_cost), 0) AS stock_value
        FROM inventory_movements m
        JOIN items i ON i.id = m.item_id
        JOIN storages s ON s.id = m.storage_id
        LEFT JOIN plants p ON p.id = s.plant_id
        WHERE {where_sql}
        GROUP BY p.id, s.id, i.id
        HAVING balance_qty != 0
        ORDER BY p.code, s.code, i.code
        """,
        tuple(params),
    )
    st.markdown("**Summary Stock**")
    show_df(summary, height=260)
    export_buttons(summary, "stock_card_summary", "Stock Card Summary")

    detail = fetch_df(
        f"""
        SELECT m.doc_date, m.doc_no, p.code AS plant, s.code AS storage,
               i.code AS item_code, i.name AS item_name, m.movement_type,
               m.qty_in, m.qty_out,
               SUM(m.qty_in - m.qty_out) OVER (
                   PARTITION BY m.item_id, m.storage_id
                   ORDER BY m.doc_date, m.id
               ) AS running_balance,
               m.ref_type, m.ref_no, m.notes
        FROM inventory_movements m
        JOIN items i ON i.id = m.item_id
        JOIN storages s ON s.id = m.storage_id
        LEFT JOIN plants p ON p.id = s.plant_id
        WHERE {where_sql}
        ORDER BY m.doc_date DESC, m.id DESC
        """,
        tuple(params),
    )
    st.markdown("**Detail Movement**")
    show_df(detail, height=360)
    export_buttons(detail, "stock_card_detail", "Stock Card Detail")


def stock_movement_page() -> None:
    view_key = "inventory_movement_view"
    st.session_state.setdefault(view_key, "list")

    if st.session_state[view_key] == "list":
        list_toolbar("Stock Movement", "Create New", view_key)
        df = fetch_df(
            """
            SELECT m.doc_no, m.doc_date, m.movement_type, p.code AS plant, s.code AS storage,
                   i.code AS item_code, i.name AS item_name, m.qty_in, m.qty_out,
                   m.ref_type, m.ref_no, m.notes
            FROM inventory_movements m
            JOIN items i ON i.id = m.item_id
            JOIN storages s ON s.id = m.storage_id
            LEFT JOIN plants p ON p.id = s.plant_id
            ORDER BY m.id DESC
            LIMIT 150
            """
        )
        show_df(df, height=420)
        export_buttons(df, "stock_movement", "Stock Movement")
        st.markdown("**Print dokumen terakhir**")
        for _, row in df.head(8).iterrows():
            c1, c2, c3 = st.columns([0.18, 0.62, 0.2])
            c1.write(row["doc_no"])
            c2.write(f"{row['movement_type']} - {row['item_code']} - {fmt_qty(row['qty_in'] - row['qty_out'])}")
            if c3.button("Print", key=f"print_movement_{row['doc_no']}"):
                printable = pd.DataFrame([row])
                st.download_button(
                    "Download PDF",
                    data=df_to_simple_pdf_bytes(printable, f"Stock Movement {row['doc_no']}"),
                    file_name=f"{row['doc_no']}.pdf",
                    mime="application/pdf",
                    key=f"download_movement_{row['doc_no']}",
                )
        return

    if st.button("Kembali ke list", key="movement_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Stock Movement")
    note("In Plant untuk stock masuk/keluar dalam satu plant. Cross Plant untuk transfer antar storage atau plant.")
    items = option_map("items", "code || ' - ' || name", "active = 1", "code")
    storages = option_map("storages", "code || ' - ' || name", "active = 1", "code")

    with st.form("stock_movement_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal", value=date.today())
            movement_scope = st.selectbox("Jenis", ["In Plant", "Cross Plant"])
        with c2:
            item_id = select_from_map("Item", items, "mv_item")
            qty = st.number_input("Qty", min_value=0.0, value=1.0, step=1.0)
        with c3:
            unit_cost = st.number_input("Unit Cost", min_value=0.0, value=0.0, step=1000.0)
            notes = st.text_area("Catatan")

        if movement_scope == "In Plant":
            storage_id = select_from_map("Storage", storages, "mv_storage")
            movement_type = st.selectbox("Movement", ["IN", "OUT", "ADJUSTMENT_IN", "ADJUSTMENT_OUT"])
            from_storage_id = None
            to_storage_id = None
        else:
            from_storage_id = select_from_map("From Storage", storages, "mv_from_storage")
            to_storage_id = select_from_map("To Storage", storages, "mv_to_storage")
            storage_id = None
            movement_type = "TRANSFER"

        submitted = st.form_submit_button("Post Movement", type="primary")

    if submitted and item_id:
        if qty <= 0:
            st.error("Qty harus lebih dari 0.")
            return
        if movement_scope == "In Plant":
            if not storage_id:
                return
            if movement_type in {"OUT", "ADJUSTMENT_OUT"} and current_stock(item_id, storage_id) < qty:
                st.error("Stock tidak cukup.")
                return
            doc_no = create_inventory_movement(
                doc_date=as_iso(doc_date),
                movement_type=movement_type,
                item_id=item_id,
                storage_id=storage_id,
                qty_in=qty if movement_type in {"IN", "ADJUSTMENT_IN"} else 0,
                qty_out=qty if movement_type in {"OUT", "ADJUSTMENT_OUT"} else 0,
                unit_cost=unit_cost,
                ref_type="MANUAL",
                notes=notes,
            )
            st.success(f"Movement berhasil diposting: {doc_no}")
        else:
            if not from_storage_id or not to_storage_id:
                return
            if from_storage_id == to_storage_id:
                st.error("Storage asal dan tujuan tidak boleh sama.")
                return
            if current_stock(item_id, from_storage_id) < qty:
                st.error("Stock asal tidak cukup.")
                return
            transfer_no = next_doc_no("TRF", "inventory_movements")
            out_no = create_inventory_movement(
                doc_date=as_iso(doc_date),
                movement_type="TRANSFER_OUT",
                item_id=item_id,
                storage_id=from_storage_id,
                qty_out=qty,
                unit_cost=unit_cost,
                ref_type="TRANSFER",
                ref_no=transfer_no,
                notes=notes,
                from_storage_id=from_storage_id,
                to_storage_id=to_storage_id,
            )
            in_no = create_inventory_movement(
                doc_date=as_iso(doc_date),
                movement_type="TRANSFER_IN",
                item_id=item_id,
                storage_id=to_storage_id,
                qty_in=qty,
                unit_cost=unit_cost,
                ref_type="TRANSFER",
                ref_no=transfer_no,
                notes=notes,
                from_storage_id=from_storage_id,
                to_storage_id=to_storage_id,
            )
            st.success(f"Transfer berhasil diposting: {out_no} dan {in_no}")
        reset_view(view_key)
        st.rerun()


def stock_count_page() -> None:
    view_key = "stock_count_view"
    st.session_state.setdefault(view_key, "list")

    if st.session_state[view_key] == "list":
        list_toolbar("Stock Count", "Create Job", view_key)
        df = fetch_df(
            """
            SELECT ic.count_no, ic.count_date, p.code AS plant, s.code AS storage,
                   ic.status, ic.notes, COUNT(icl.id) AS line_count
            FROM inventory_counts ic
            JOIN storages s ON s.id = ic.storage_id
            LEFT JOIN plants p ON p.id = s.plant_id
            LEFT JOIN inventory_count_lines icl ON icl.count_id = ic.id
            GROUP BY ic.id
            ORDER BY ic.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="stock_count_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Stock Count Job")
    storage_options = option_map("storages", "code || ' - ' || name", "active = 1", "code")
    storage_id = select_from_map("Storage", storage_options, "count_storage")
    if not storage_id:
        return
    item_df = fetch_df(
        """
        SELECT i.id AS item_id, i.code, i.name, i.uom,
               COALESCE(SUM(m.qty_in - m.qty_out), 0) AS system_qty
        FROM items i
        LEFT JOIN inventory_movements m ON m.item_id = i.id AND m.storage_id = ?
        WHERE i.active = 1
        GROUP BY i.id
        ORDER BY i.code
        """,
        (storage_id,),
    )
    item_df["counted_qty"] = item_df["system_qty"]
    edited = st.data_editor(
        item_df[["item_id", "code", "name", "uom", "system_qty", "counted_qty"]],
        width="stretch",
        hide_index=True,
        disabled=["item_id", "code", "name", "uom", "system_qty"],
        column_config={"item_id": None, "system_qty": "Qty Sistem", "counted_qty": "Qty Fisik"},
    )
    notes = st.text_area("Catatan")
    if st.button("Post Stock Count", type="primary"):
        count_no = next_doc_no("IC", "inventory_counts", "count_no")
        conn = get_conn()
        with conn:
            cur = conn.execute(
                "INSERT INTO inventory_counts (count_no, count_date, storage_id, status, notes) VALUES (?, ?, ?, 'Posted', ?)",
                (count_no, today_iso(), storage_id, notes),
            )
            count_id = cur.lastrowid
            for _, row in edited.iterrows():
                system_qty = float(row["system_qty"] or 0)
                counted_qty = float(row["counted_qty"] or 0)
                diff = counted_qty - system_qty
                conn.execute(
                    """
                    INSERT INTO inventory_count_lines (count_id, item_id, system_qty, counted_qty, diff_qty)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (count_id, int(row["item_id"]), system_qty, counted_qty, diff),
                )
                if abs(diff) > 0.0001:
                    item = fetch_one("SELECT std_cost FROM items WHERE id = ?", (int(row["item_id"]),))
                    create_inventory_movement(
                        doc_date=today_iso(),
                        movement_type="COUNT_ADJ_IN" if diff > 0 else "COUNT_ADJ_OUT",
                        item_id=int(row["item_id"]),
                        storage_id=storage_id,
                        qty_in=max(diff, 0),
                        qty_out=max(-diff, 0),
                        unit_cost=float(item["std_cost"] or 0),
                        ref_type="STOCK_COUNT",
                        ref_no=count_no,
                        notes=notes,
                    )
        st.success(f"Stock count berhasil diposting: {count_no}")
        reset_view(view_key)
        st.rerun()


def render_inventory() -> None:
    page_title("Inventory", "Stock card, stock movement, dan stock count dengan alur list-first.")
    page = st.sidebar.radio("Inventory", ["Stock Card", "Stock Movement", "Stock Count"], key="inventory_page")
    if page == "Stock Card":
        stock_card_page()
    elif page == "Stock Movement":
        stock_movement_page()
    else:
        stock_count_page()


# ---------------------------------------------------------------------------
# Sales
# ---------------------------------------------------------------------------


def estimate_list() -> pd.DataFrame:
    return fetch_df(
        """
        SELECT se.id, se.doc_no, se.doc_date, c.name AS customer, se.project_name,
               se.valid_until, se.status, se.subtotal, se.tax, se.total,
               CASE WHEN so.id IS NULL THEN 'No' ELSE 'Yes' END AS has_so
        FROM sales_estimates se
        JOIN customers c ON c.id = se.customer_id
        LEFT JOIN sales_orders so ON so.estimate_id = se.id
        ORDER BY se.id DESC
        """
    )


def make_so_from_estimate(estimate_id: int) -> str:
    est = fetch_one("SELECT * FROM sales_estimates WHERE id = ?", (estimate_id,))
    existing = fetch_one("SELECT doc_no FROM sales_orders WHERE estimate_id = ?", (estimate_id,))
    if existing:
        return existing["doc_no"]
    lines = fetch_df("SELECT * FROM sales_estimate_lines WHERE estimate_id = ?", (estimate_id,))
    doc_no = next_doc_no("SO", "sales_orders")
    conn = get_conn()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO sales_orders
            (doc_no, doc_date, customer_id, estimate_id, project_name, delivery_date, status, subtotal, tax, total, notes, plant_id)
            VALUES (?, ?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, ?)
            """,
            (
                doc_no,
                today_iso(),
                est["customer_id"],
                estimate_id,
                est["project_name"],
                (date.today() + timedelta(days=14)).isoformat(),
                est["subtotal"],
                est["tax"],
                est["total"],
                est["notes"],
                est["plant_id"],
            ),
        )
        so_id = cur.lastrowid
        for _, line in lines.iterrows():
            conn.execute(
                """
                INSERT INTO sales_order_lines
                (sales_order_id, line_type, item_id, service_id, description, qty, uom, price, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    so_id,
                    line["line_type"],
                    line["item_id"],
                    line["service_id"],
                    line["description"],
                    line["qty"],
                    line["uom"],
                    line["price"],
                    line["total"],
                ),
            )
    return doc_no


def sales_estimate_page() -> None:
    view_key = "estimate_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Estimate", "Create New", view_key)
        df = estimate_list()
        show_df(df.drop(columns=["id"]) if not df.empty else df)
        if not df.empty:
            st.markdown("**Action**")
            for _, row in df.head(12).iterrows():
                c1, c2, c3 = st.columns([0.22, 0.58, 0.2])
                c1.write(row["doc_no"])
                c2.write(f"{row['customer']} - {row['project_name']} - {money(row['total'])}")
                disabled = row["has_so"] == "Yes"
                if c3.button("Make SO", key=f"make_so_{row['id']}", disabled=disabled):
                    so_no = make_so_from_estimate(int(row["id"]))
                    st.success(f"Sales Order dibuat: {so_no}")
                    st.rerun()
        return

    if st.button("Kembali ke list", key="est_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Estimate")
    note("Template estimate memakai praktik umum precast: project, validitas, term pembayaran, term pengiriman, dan catatan QC.")
    customers = option_map("customers", "code || ' - ' || name", "active = 1", "code")
    plants = option_map("plants", "code || ' - ' || name", "active = 1", "code")
    with st.form("estimate_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal Estimate", value=date.today())
            customer_id = select_from_map("Customer", customers, "est_customer")
            plant_id = select_from_map("Plant Produksi", plants, "est_plant")
        with c2:
            project_name = st.text_input("Nama Project")
            valid_until = st.date_input("Valid Until", value=date.today() + timedelta(days=14))
            payment_terms_text = st.text_input("Payment Term", value="30 hari setelah invoice diterima")
        with c3:
            delivery_terms = st.text_input("Delivery Term", value="Franco proyek, unloading by customer")
            qc_terms = st.text_input("QC / Spec", value="Produk sesuai shop drawing dan approval QC")
            tax_rate = st.number_input("PPN %", min_value=0.0, max_value=100.0, value=11.0, step=0.5)
        notes = st.text_area("Catatan")
        lines = line_editor(key="estimate_lines", include_services=True, price_mode="sales")
        submitted = st.form_submit_button("Simpan Estimate", type="primary")

    if submitted and customer_id and plant_id:
        if not lines:
            st.error("Detail estimate masih kosong.")
            return
        subtotal = sum(line["total"] for line in lines)
        tax = subtotal * tax_rate / 100
        total = subtotal + tax
        doc_no = next_doc_no("EST", "sales_estimates")
        conn = get_conn()
        with conn:
            cur = conn.execute(
                """
                INSERT INTO sales_estimates
                (doc_no, doc_date, customer_id, project_name, valid_until, status, subtotal, tax, total,
                 notes, plant_id, payment_terms_text, delivery_terms, qc_terms)
                VALUES (?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_no,
                    as_iso(doc_date),
                    customer_id,
                    project_name,
                    as_iso(valid_until),
                    subtotal,
                    tax,
                    total,
                    notes,
                    plant_id,
                    payment_terms_text,
                    delivery_terms,
                    qc_terms,
                ),
            )
            insert_lines("sales_estimate_lines", "estimate_id", cur.lastrowid, lines)
        st.success(f"Estimate berhasil disimpan: {doc_no}")
        reset_view(view_key)
        st.rerun()


def sales_order_page() -> None:
    view_key = "sales_order_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Sales Order", "Create SO Tanpa Estimate", view_key)
        df = fetch_df(
            """
            SELECT so.doc_no, so.doc_date, c.name AS customer, so.project_name,
                   se.doc_no AS estimate_no, so.delivery_date, so.status, so.total
            FROM sales_orders so
            JOIN customers c ON c.id = so.customer_id
            LEFT JOIN sales_estimates se ON se.id = so.estimate_id
            ORDER BY so.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="so_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Sales Order Tanpa Estimate")
    note("Gunakan ini untuk pekerjaan jasa atau order cepat yang tidak melalui estimate.")
    customers = option_map("customers", "code || ' - ' || name", "active = 1", "code")
    plants = option_map("plants", "code || ' - ' || name", "active = 1", "code")
    with st.form("so_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal SO", value=date.today())
            customer_id = select_from_map("Customer", customers, "so_customer")
        with c2:
            project_name = st.text_input("Project / Pekerjaan")
            delivery_date = st.date_input("Rencana Delivery", value=date.today() + timedelta(days=7))
        with c3:
            plant_id = select_from_map("Plant", plants, "so_plant")
            tax_rate = st.number_input("PPN %", min_value=0.0, max_value=100.0, value=11.0, step=0.5)
        notes = st.text_area("Catatan")
        lines = line_editor(key="so_lines", include_services=True, price_mode="sales")
        submitted = st.form_submit_button("Simpan Sales Order", type="primary")

    if submitted and customer_id and plant_id:
        if not lines:
            st.error("Detail SO masih kosong.")
            return
        subtotal = sum(line["total"] for line in lines)
        tax = subtotal * tax_rate / 100
        total = subtotal + tax
        doc_no = next_doc_no("SO", "sales_orders")
        conn = get_conn()
        with conn:
            cur = conn.execute(
                """
                INSERT INTO sales_orders
                (doc_no, doc_date, customer_id, project_name, delivery_date, status, subtotal, tax, total, notes, plant_id)
                VALUES (?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, ?)
                """,
                (doc_no, as_iso(doc_date), customer_id, project_name, as_iso(delivery_date), subtotal, tax, total, notes, plant_id),
            )
            insert_lines("sales_order_lines", "sales_order_id", cur.lastrowid, lines)
        st.success(f"Sales Order berhasil disimpan: {doc_no}")
        reset_view(view_key)
        st.rerun()


def production_order_page() -> None:
    view_key = "production_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Production Order", "Create New", view_key)
        df = fetch_df(
            """
            SELECT po.doc_no, po.doc_date, so.doc_no AS sales_order, i.code AS item,
                   i.name AS item_name, po.qty, po.produced_qty, st.code AS storage,
                   po.due_date, po.status, po.notes
            FROM production_orders po
            LEFT JOIN sales_orders so ON so.id = po.sales_order_id
            JOIN items i ON i.id = po.item_id
            LEFT JOIN storages st ON st.id = po.storage_id
            ORDER BY po.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="prod_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Production Order")
    note("Best practice precast: PO produksi diturunkan dari SO, fokus ke item finished goods, storage hasil, due date, dan qty rencana.")
    so_options = {"Tanpa SO": None}
    so_options.update(option_map("sales_orders", "doc_no || ' - ' || project_name", "status != 'Cancelled'", "doc_no"))
    item_options = option_map("items", "code || ' - ' || name", "active = 1 AND category = 'Finished Goods'", "code")
    storage_options = option_map("storages", "code || ' - ' || name", "active = 1", "code")
    with st.form("prod_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal", value=date.today())
            so_label = st.selectbox("Sales Order", list(so_options.keys()))
        with c2:
            item_id = select_from_map("Finished Goods", item_options, "prod_item")
            qty = st.number_input("Qty Rencana", min_value=0.0, value=1.0, step=1.0)
        with c3:
            storage_id = select_from_map("Storage Hasil", storage_options, "prod_storage")
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=3))
        notes = st.text_area("Instruksi Produksi / QC")
        submitted = st.form_submit_button("Simpan Production Order", type="primary")
    if submitted and item_id and storage_id:
        doc_no = next_doc_no("PROD", "production_orders")
        execute(
            """
            INSERT INTO production_orders
            (doc_no, doc_date, sales_order_id, item_id, storage_id, qty, due_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Open', ?)
            """,
            (doc_no, as_iso(doc_date), so_options[so_label], item_id, storage_id, qty, as_iso(due_date), notes),
        )
        st.success(f"Production Order berhasil dibuat: {doc_no}")
        reset_view(view_key)
        st.rerun()

    st.markdown("**Post Hasil Produksi**")
    open_prod = option_map("production_orders", "doc_no || ' - Qty ' || qty", "status IN ('Open', 'In Progress')", "doc_no")
    if open_prod:
        with st.form("prod_post"):
            prod_id = select_from_map("Production Order", open_prod, "prod_post_id")
            produced_qty = st.number_input("Qty Selesai", min_value=0.0, value=1.0, step=1.0)
            unit_cost = st.number_input("Unit Cost Aktual", min_value=0.0, value=0.0, step=1000.0)
            if st.form_submit_button("Post Hasil Produksi"):
                prod = fetch_one("SELECT * FROM production_orders WHERE id = ?", (prod_id,))
                item = fetch_one("SELECT std_cost FROM items WHERE id = ?", (prod["item_id"],))
                cost = unit_cost or float(item["std_cost"] or 0)
                create_inventory_movement(
                    doc_date=today_iso(),
                    movement_type="PRODUCTION_IN",
                    item_id=int(prod["item_id"]),
                    storage_id=int(prod["storage_id"]),
                    qty_in=produced_qty,
                    unit_cost=cost,
                    ref_type="PRODUCTION_ORDER",
                    ref_no=prod["doc_no"],
                    notes="Hasil produksi",
                )
                execute(
                    """
                    UPDATE production_orders
                    SET produced_qty = produced_qty + ?,
                        status = CASE WHEN produced_qty + ? >= qty THEN 'Closed' ELSE 'In Progress' END
                    WHERE id = ?
                    """,
                    (produced_qty, produced_qty, prod_id),
                )
                st.success("Hasil produksi diposting.")
                st.rerun()


def delivery_order_page() -> None:
    view_key = "delivery_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Delivery Order", "Create New", view_key)
        df = fetch_df(
            """
            SELECT do.doc_no, do.doc_date, c.name AS customer, so.doc_no AS sales_order,
                   do.delivery_address, d.name AS driver, tu.plate_no, do.status
            FROM delivery_orders do
            JOIN customers c ON c.id = do.customer_id
            LEFT JOIN sales_orders so ON so.id = do.sales_order_id
            LEFT JOIN drivers d ON d.id = do.driver_id
            LEFT JOIN transport_units tu ON tu.id = do.transport_unit_id
            ORDER BY do.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="do_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Delivery Order")
    note("DO memakai SO sebagai sumber, hanya item barang yang dikirim keluar dari storage.")
    so_options = option_map("sales_orders", "doc_no || ' - ' || project_name", "status != 'Cancelled'", "doc_no")
    if not so_options:
        st.info("Belum ada Sales Order.")
        return
    so_id = select_from_map("Sales Order", so_options, "do_so")
    so = fetch_one("SELECT * FROM sales_orders WHERE id = ?", (so_id,))
    customer = fetch_one("SELECT * FROM customers WHERE id = ?", (so["customer_id"],))
    storage_options = option_map("storages", "code || ' - ' || name", "active = 1", "code")
    driver_options = option_map("drivers", "code || ' - ' || name", "active = 1", "code")
    unit_options = option_map("transport_units", "code || ' - ' || plate_no", "status != 'Inactive'", "code")
    lines_df = fetch_df(
        """
        SELECT sol.item_id, i.code, i.name, sol.qty AS so_qty, sol.uom
        FROM sales_order_lines sol
        JOIN items i ON i.id = sol.item_id
        WHERE sol.sales_order_id = ? AND sol.line_type = 'Item'
        ORDER BY sol.id
        """,
        (so_id,),
    )
    if lines_df.empty:
        st.warning("SO ini tidak memiliki item barang. Untuk pekerjaan jasa, invoice bisa dibuat langsung dari SO nanti.")
        return
    with st.form("do_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal DO", value=date.today())
            storage_id = select_from_map("Storage Keluar", storage_options, "do_storage")
        with c2:
            driver_id = select_from_map("Driver", driver_options, "do_driver")
            unit_id = select_from_map("Unit Transport", unit_options, "do_unit")
        with c3:
            delivery_address = st.text_area("Alamat Kirim", value=customer["address"] or "")
        do_lines = lines_df.copy()
        do_lines["ship_qty"] = do_lines["so_qty"]
        edited = st.data_editor(
            do_lines[["item_id", "code", "name", "so_qty", "uom", "ship_qty"]],
            width="stretch",
            hide_index=True,
            disabled=["item_id", "code", "name", "so_qty", "uom"],
            column_config={"item_id": None, "ship_qty": st.column_config.NumberColumn("Qty Kirim", min_value=0.0, step=1.0)},
        )
        notes = st.text_area("Catatan")
        submitted = st.form_submit_button("Post Delivery Order", type="primary")
    if submitted and storage_id:
        for _, row in edited.iterrows():
            qty = float(row["ship_qty"] or 0)
            if qty > 0 and current_stock(int(row["item_id"]), storage_id) < qty:
                st.error(f"Stock tidak cukup untuk {row['code']}.")
                return
        doc_no = next_doc_no("DO", "delivery_orders")
        conn = get_conn()
        cogs = 0.0
        with conn:
            cur = conn.execute(
                """
                INSERT INTO delivery_orders
                (doc_no, doc_date, sales_order_id, customer_id, driver_id, transport_unit_id, delivery_address, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Posted', ?)
                """,
                (doc_no, as_iso(doc_date), so_id, so["customer_id"], driver_id, unit_id, delivery_address, notes),
            )
            do_id = cur.lastrowid
            for _, row in edited.iterrows():
                qty = float(row["ship_qty"] or 0)
                if qty <= 0:
                    continue
                item = fetch_one("SELECT std_cost FROM items WHERE id = ?", (int(row["item_id"]),))
                cost = float(item["std_cost"] or 0)
                cogs += qty * cost
                conn.execute(
                    """
                    INSERT INTO delivery_order_lines (delivery_order_id, item_id, storage_id, qty, uom)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (do_id, int(row["item_id"]), storage_id, qty, row["uom"]),
                )
                create_inventory_movement(
                    doc_date=as_iso(doc_date),
                    movement_type="DELIVERY_OUT",
                    item_id=int(row["item_id"]),
                    storage_id=storage_id,
                    qty_out=qty,
                    unit_cost=cost,
                    ref_type="DELIVERY_ORDER",
                    ref_no=doc_no,
                    notes=notes,
                )
        if cogs > 0:
            post_journal(
                doc_date=as_iso(doc_date),
                source_type="DELIVERY_ORDER",
                source_no=doc_no,
                description=f"COGS {doc_no}",
                lines=[
                    {"account_code": "5000", "debit": cogs, "credit": 0},
                    {"account_code": "1200", "debit": 0, "credit": cogs},
                ],
            )
        st.success(f"Delivery Order diposting: {doc_no}")
        reset_view(view_key)
        st.rerun()


def customer_invoice_page() -> None:
    view_key = "invoice_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Invoice", "Create From DO", view_key)
        df = fetch_df(
            """
            SELECT ci.doc_no, ci.doc_date, do.doc_no AS delivery_order, c.name AS customer,
                   ci.due_date, ci.total, ci.paid_amount, ci.total - ci.paid_amount AS outstanding, ci.status
            FROM customer_invoices ci
            JOIN customers c ON c.id = ci.customer_id
            LEFT JOIN delivery_orders do ON do.id = ci.delivery_order_id
            ORDER BY ci.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="inv_back"):
        reset_view(view_key)
        st.rerun()

    st.subheader("Create Invoice Based on Delivery Order")
    do_options = option_map("delivery_orders", "doc_no", "status = 'Posted'", "doc_no")
    if not do_options:
        st.info("Belum ada Delivery Order yang bisa ditagihkan.")
        return
    with st.form("invoice_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            do_id = select_from_map("Delivery Order", do_options, "inv_do")
            doc_date = st.date_input("Tanggal Invoice", value=date.today())
        with c2:
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=30))
        with c3:
            tax_rate = st.number_input("PPN %", min_value=0.0, max_value=100.0, value=11.0, step=0.5)
        notes = st.text_area("Catatan")
        submitted = st.form_submit_button("Post Invoice", type="primary")
    if submitted and do_id:
        do = fetch_one("SELECT * FROM delivery_orders WHERE id = ?", (do_id,))
        do_lines = fetch_df(
            """
            SELECT dol.item_id, i.name, dol.qty, dol.uom,
                   COALESCE(sol.price, i.sales_price, 0) AS price
            FROM delivery_order_lines dol
            JOIN items i ON i.id = dol.item_id
            LEFT JOIN sales_order_lines sol ON sol.sales_order_id = ? AND sol.item_id = dol.item_id
            WHERE dol.delivery_order_id = ?
            """,
            (do["sales_order_id"], do_id),
        )
        if do_lines.empty:
            st.error("Delivery Order tidak memiliki detail item.")
            return
        subtotal = float((do_lines["qty"] * do_lines["price"]).sum())
        tax = subtotal * tax_rate / 100
        total = subtotal + tax
        doc_no = next_doc_no("INV", "customer_invoices")
        conn = get_conn()
        with conn:
            cur = conn.execute(
                """
                INSERT INTO customer_invoices
                (doc_no, doc_date, customer_id, sales_order_id, delivery_order_id, due_date, status,
                 subtotal, tax, total, paid_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, 'Posted', ?, ?, ?, 0, ?)
                """,
                (
                    doc_no,
                    as_iso(doc_date),
                    do["customer_id"],
                    do["sales_order_id"],
                    do_id,
                    as_iso(due_date),
                    subtotal,
                    tax,
                    total,
                    notes,
                ),
            )
            inv_id = cur.lastrowid
            for _, row in do_lines.iterrows():
                conn.execute(
                    """
                    INSERT INTO customer_invoice_lines
                    (invoice_id, line_type, item_id, service_id, description, qty, uom, price, total)
                    VALUES (?, 'Item', ?, NULL, ?, ?, ?, ?, ?)
                    """,
                    (
                        inv_id,
                        int(row["item_id"]),
                        row["name"],
                        float(row["qty"]),
                        row["uom"],
                        float(row["price"] or 0),
                        float(row["qty"] or 0) * float(row["price"] or 0),
                    ),
                )
        journal_lines = [
            {"account_code": "1100", "debit": total, "credit": 0},
            {"account_code": "4000", "debit": 0, "credit": subtotal},
        ]
        if tax > 0:
            journal_lines.append({"account_code": "2100", "debit": 0, "credit": tax})
        post_journal(
            doc_date=as_iso(doc_date),
            source_type="CUSTOMER_INVOICE",
            source_no=doc_no,
            description=f"Invoice {doc_no}",
            lines=journal_lines,
        )
        st.success(f"Invoice berhasil diposting: {doc_no}")
        reset_view(view_key)
        st.rerun()


def render_sales() -> None:
    page_title("Sales", "Estimate, SO, produksi, delivery, dan invoice dengan flow dokumen yang sederhana.")
    page = st.sidebar.radio(
        "Sales",
        ["Estimate", "Sales Order", "Production Order", "Delivery Order", "Invoice"],
        key="sales_page",
    )
    if page == "Estimate":
        sales_estimate_page()
    elif page == "Sales Order":
        sales_order_page()
    elif page == "Production Order":
        production_order_page()
    elif page == "Delivery Order":
        delivery_order_page()
    else:
        customer_invoice_page()


# ---------------------------------------------------------------------------
# Purchase
# ---------------------------------------------------------------------------


def purchase_request_page() -> None:
    view_key = "pr_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Purchase Request", "Create New", view_key)
        df = fetch_df(
            """
            SELECT pr.doc_no, pr.doc_date, e.name AS request_by, pr.required_date, pr.status, pr.notes
            FROM purchase_requests pr
            LEFT JOIN employees e ON e.id = pr.employee_id
            ORDER BY pr.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="pr_back"):
        reset_view(view_key)
        st.rerun()
    employees = option_map("employees", "code || ' - ' || name", "status = 'Active'", "code")
    with st.form("pr_create"):
        c1, c2 = st.columns(2)
        with c1:
            doc_date = st.date_input("Tanggal PR", value=date.today())
            employee_id = select_from_map("Request By", employees, "pr_employee")
        with c2:
            required_date = st.date_input("Required Date", value=date.today() + timedelta(days=7))
        notes = st.text_area("Catatan")
        lines = line_editor(key="pr_lines", include_services=True, price_mode="purchase", price_label="Estimasi Harga")
        submitted = st.form_submit_button("Simpan PR", type="primary")
    if submitted and employee_id:
        if not lines:
            st.error("Detail PR masih kosong.")
            return
        doc_no = next_doc_no("PR", "purchase_requests")
        conn = get_conn()
        with conn:
            cur = conn.execute(
                "INSERT INTO purchase_requests (doc_no, doc_date, employee_id, required_date, status, notes) VALUES (?, ?, ?, ?, 'Submitted', ?)",
                (doc_no, as_iso(doc_date), employee_id, as_iso(required_date), notes),
            )
            insert_lines("purchase_request_lines", "pr_id", cur.lastrowid, lines, price_col="est_price")
        st.success(f"PR berhasil dibuat: {doc_no}")
        reset_view(view_key)
        st.rerun()


def purchase_order_page() -> None:
    view_key = "po_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Purchase Order", "Create New", view_key)
        df = fetch_df(
            """
            SELECT po.doc_no, po.doc_date, s.name AS supplier, pr.doc_no AS pr_no,
                   po.expected_date, po.status, po.subtotal, po.tax, po.total
            FROM purchase_orders po
            JOIN suppliers s ON s.id = po.supplier_id
            LEFT JOIN purchase_requests pr ON pr.id = po.pr_id
            ORDER BY po.id DESC
            """
        )
        show_df(df)
        return

    if st.button("Kembali ke list", key="po_back"):
        reset_view(view_key)
        st.rerun()
    suppliers = option_map("suppliers", "code || ' - ' || name", "active = 1", "code")
    pr_options = {"Tanpa PR": None}
    pr_options.update(option_map("purchase_requests", "doc_no", "status != 'Cancelled'", "doc_no"))
    with st.form("po_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal PO", value=date.today())
            supplier_id = select_from_map("Supplier", suppliers, "po_supplier")
        with c2:
            pr_label = st.selectbox("Referensi PR", list(pr_options.keys()))
            expected_date = st.date_input("Expected Date", value=date.today() + timedelta(days=7))
        with c3:
            tax_rate = st.number_input("PPN %", min_value=0.0, max_value=100.0, value=11.0, step=0.5)
        notes = st.text_area("Catatan")
        lines = line_editor(key="po_lines", include_services=True, price_mode="purchase")
        submitted = st.form_submit_button("Simpan PO", type="primary")
    if submitted and supplier_id:
        if not lines:
            st.error("Detail PO masih kosong.")
            return
        subtotal = sum(line["total"] for line in lines)
        tax = subtotal * tax_rate / 100
        total = subtotal + tax
        doc_no = next_doc_no("PO", "purchase_orders")
        conn = get_conn()
        with conn:
            cur = conn.execute(
                """
                INSERT INTO purchase_orders
                (doc_no, doc_date, supplier_id, pr_id, expected_date, status, subtotal, tax, total, notes)
                VALUES (?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?)
                """,
                (doc_no, as_iso(doc_date), supplier_id, pr_options[pr_label], as_iso(expected_date), subtotal, tax, total, notes),
            )
            insert_lines("purchase_order_lines", "po_id", cur.lastrowid, lines)
        st.success(f"PO berhasil dibuat: {doc_no}")
        reset_view(view_key)
        st.rerun()


def supplier_invoice_page() -> None:
    view_key = "si_view"
    st.session_state.setdefault(view_key, "list")
    if st.session_state[view_key] == "list":
        list_toolbar("Supplier Invoice", "Create / Receive", view_key)
        df = fetch_df(
            """
            SELECT si.doc_no, si.doc_date, s.name AS supplier, po.doc_no AS po_no,
                   st.code AS storage, si.due_date, si.total, si.paid_amount,
                   si.total - si.paid_amount AS outstanding, si.status
            FROM supplier_invoices si
            JOIN suppliers s ON s.id = si.supplier_id
            LEFT JOIN purchase_orders po ON po.id = si.po_id
            LEFT JOIN storages st ON st.id = si.storage_id
            ORDER BY si.id DESC
            """
        )
        show_df(df)
        return
    if st.button("Kembali ke list", key="si_back"):
        reset_view(view_key)
        st.rerun()

    suppliers = option_map("suppliers", "code || ' - ' || name", "active = 1", "code")
    po_options = {"Tanpa PO": None}
    po_options.update(option_map("purchase_orders", "doc_no", "status != 'Cancelled'", "doc_no"))
    storages = option_map("storages", "code || ' - ' || name", "active = 1", "code")
    with st.form("supplier_invoice_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_date = st.date_input("Tanggal Invoice", value=date.today())
            supplier_id = select_from_map("Supplier", suppliers, "si_supplier")
        with c2:
            po_label = st.selectbox("PO", list(po_options.keys()))
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=30))
        with c3:
            storage_id = select_from_map("Storage Penerimaan", storages, "si_storage")
            tax_rate = st.number_input("PPN %", min_value=0.0, max_value=100.0, value=11.0, step=0.5)
        notes = st.text_area("Catatan")
        lines = line_editor(key="si_lines", include_services=True, price_mode="purchase")
        submitted = st.form_submit_button("Post Supplier Invoice", type="primary")
    if submitted and supplier_id and storage_id:
        if not lines:
            st.error("Detail invoice kosong.")
            return
        subtotal = sum(line["total"] for line in lines)
        tax = subtotal * tax_rate / 100
        total = subtotal + tax
        doc_no = next_doc_no("SIN", "supplier_invoices")
        conn = get_conn()
        item_total = 0.0
        service_total = 0.0
        with conn:
            cur = conn.execute(
                """
                INSERT INTO supplier_invoices
                (doc_no, doc_date, supplier_id, po_id, storage_id, due_date, status,
                 subtotal, tax, total, paid_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, 'Posted', ?, ?, ?, 0, ?)
                """,
                (doc_no, as_iso(doc_date), supplier_id, po_options[po_label], storage_id, as_iso(due_date), subtotal, tax, total, notes),
            )
            insert_lines("supplier_invoice_lines", "invoice_id", cur.lastrowid, lines)
            for line in lines:
                if line["line_type"] == "Item":
                    item_total += line["total"]
                    create_inventory_movement(
                        doc_date=as_iso(doc_date),
                        movement_type="PURCHASE_IN",
                        item_id=int(line["item_id"]),
                        storage_id=storage_id,
                        qty_in=float(line["qty"]),
                        unit_cost=float(line["price"]),
                        ref_type="SUPPLIER_INVOICE",
                        ref_no=doc_no,
                        notes=notes,
                    )
                else:
                    service_total += line["total"]
        journal_lines = []
        if item_total:
            journal_lines.append({"account_code": "1200", "debit": item_total, "credit": 0})
        if service_total:
            journal_lines.append({"account_code": "6000", "debit": service_total, "credit": 0})
        if tax:
            journal_lines.append({"account_code": "2200", "debit": tax, "credit": 0})
        journal_lines.append({"account_code": "2000", "debit": 0, "credit": total})
        post_journal(
            doc_date=as_iso(doc_date),
            source_type="SUPPLIER_INVOICE",
            source_no=doc_no,
            description=f"Supplier invoice {doc_no}",
            lines=journal_lines,
        )
        st.success(f"Supplier invoice diposting: {doc_no}")
        reset_view(view_key)
        st.rerun()


def render_purchase() -> None:
    page_title("Purchase", "PR dan PO default, plus supplier invoice untuk penerimaan barang dan AP.")
    page = st.sidebar.radio("Purchase", ["PR", "PO", "Supplier Invoice"], key="purchase_page")
    if page == "PR":
        purchase_request_page()
    elif page == "PO":
        purchase_order_page()
    else:
        supplier_invoice_page()


# ---------------------------------------------------------------------------
# Accounting
# ---------------------------------------------------------------------------


def journal_transaction_page() -> None:
    st.subheader("Journal Transaction")
    accounts = option_map("accounts", "code || ' - ' || name", "active = 1", "code")
    labels = list(accounts.keys())
    with st.form("journal_form"):
        c1, c2 = st.columns(2)
        with c1:
            doc_date = st.date_input("Tanggal Jurnal", value=date.today())
        with c2:
            description = st.text_input("Deskripsi")
        initial = pd.DataFrame(
            [
                {"account": labels[0] if labels else "", "description": "", "debit": 0.0, "credit": 0.0},
                {"account": labels[0] if labels else "", "description": "", "debit": 0.0, "credit": 0.0},
            ]
        )
        edited = st.data_editor(
            initial,
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            column_config={
                "account": st.column_config.SelectboxColumn("Account", options=labels, required=True, width="large"),
                "debit": st.column_config.NumberColumn("Debit", min_value=0.0, step=1000.0, format="%.0f"),
                "credit": st.column_config.NumberColumn("Credit", min_value=0.0, step=1000.0, format="%.0f"),
            },
        )
        submitted = st.form_submit_button("Post Journal", type="primary")
    if submitted:
        lines = []
        for _, row in edited.iterrows():
            debit = float(row["debit"] or 0)
            credit = float(row["credit"] or 0)
            if debit <= 0 and credit <= 0:
                continue
            if debit > 0 and credit > 0:
                st.error("Satu baris tidak boleh debit dan credit sekaligus.")
                return
            lines.append(
                {
                    "account_id": accounts[row["account"]],
                    "description": row["description"] or description,
                    "debit": debit,
                    "credit": credit,
                }
            )
        if len(lines) < 2:
            st.error("Jurnal minimal dua baris.")
            return
        try:
            doc_no = post_journal(
                doc_date=as_iso(doc_date),
                source_type="MANUAL",
                source_no="",
                description=description,
                lines=lines,
            )
            st.success(f"Jurnal diposting: {doc_no}")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

    show_df(
        fetch_df(
            """
            SELECT je.doc_no, je.doc_date, je.source_type, je.source_no, je.description,
                   SUM(jl.debit) AS debit, SUM(jl.credit) AS credit
            FROM journal_entries je
            JOIN journal_lines jl ON jl.journal_id = je.id
            GROUP BY je.id
            ORDER BY je.id DESC
            LIMIT 100
            """
        )
    )


def cash_advance_page() -> None:
    st.subheader("Cash Advance / Kasbon Kas")
    note("Flow kasbon: buat request, post pengeluaran kas, lalu closing berdasarkan realisasi biaya dan pengembalian.")
    employees = option_map("employees", "code || ' - ' || name", "status = 'Active'", "code")

    tab_list, tab_create, tab_disburse, tab_close = st.tabs(["List", "Request", "Pengeluaran", "Closing"])
    with tab_list:
        show_df(
            fetch_df(
                """
                SELECT ca.id, ca.doc_no, ca.doc_date, e.name AS employee, ca.amount,
                       ca.settlement_amount, ca.amount - ca.settlement_amount AS remaining,
                       ca.due_date, ca.status, ca.purpose
                FROM cash_advances ca
                JOIN employees e ON e.id = ca.employee_id
                ORDER BY ca.id DESC
                """
            )
        )

    with tab_create:
        with st.form("ca_request"):
            c1, c2, c3 = st.columns(3)
            with c1:
                doc_date = st.date_input("Tanggal Request", value=date.today())
                employee_id = select_from_map("Karyawan", employees, "ca_employee")
            with c2:
                amount = st.number_input("Jumlah Kasbon", min_value=0.0, value=0.0, step=1000.0)
                due_date = st.date_input("Due Date", value=date.today() + timedelta(days=7))
            with c3:
                purpose = st.text_area("Keperluan")
            submitted = st.form_submit_button("Simpan Request", type="primary")
        if submitted and employee_id:
            if amount <= 0:
                st.error("Jumlah harus lebih dari 0.")
                return
            doc_no = next_doc_no("CA", "cash_advances")
            execute(
                """
                INSERT INTO cash_advances (doc_no, doc_date, employee_id, amount, purpose, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Requested')
                """,
                (doc_no, as_iso(doc_date), employee_id, amount, purpose, as_iso(due_date)),
            )
            st.success(f"Request kasbon dibuat: {doc_no}")
            st.rerun()

    with tab_disburse:
        options = option_map("cash_advances", "doc_no || ' - ' || amount", "status = 'Requested'", "doc_no")
        if not options:
            st.info("Tidak ada kasbon yang menunggu pengeluaran.")
        else:
            with st.form("ca_disburse"):
                ca_id = select_from_map("Kasbon", options, "ca_disburse_id")
                pay_date = st.date_input("Tanggal Pengeluaran", value=date.today())
                submitted = st.form_submit_button("Post Pengeluaran", type="primary")
            if submitted and ca_id:
                ca = fetch_one("SELECT * FROM cash_advances WHERE id = ?", (ca_id,))
                post_journal(
                    doc_date=as_iso(pay_date),
                    source_type="CASH_ADVANCE_OUT",
                    source_no=ca["doc_no"],
                    description=f"Pengeluaran kasbon {ca['doc_no']}",
                    lines=[
                        {"account_code": "1300", "debit": ca["amount"], "credit": 0},
                        {"account_code": "1000", "debit": 0, "credit": ca["amount"]},
                    ],
                )
                execute("UPDATE cash_advances SET status = 'Disbursed', disbursed_at = ? WHERE id = ?", (as_iso(pay_date), ca_id))
                st.success("Pengeluaran kasbon berhasil diposting.")
                st.rerun()

    with tab_close:
        options = option_map("cash_advances", "doc_no || ' - ' || amount", "status = 'Disbursed'", "doc_no")
        if not options:
            st.info("Tidak ada kasbon yang siap closing.")
        else:
            with st.form("ca_close"):
                ca_id = select_from_map("Kasbon", options, "ca_close_id")
                close_date = st.date_input("Tanggal Closing", value=date.today())
                settlement = st.number_input("Realisasi Biaya", min_value=0.0, value=0.0, step=1000.0)
                closing_notes = st.text_area("Catatan Closing")
                submitted = st.form_submit_button("Closing Kasbon", type="primary")
            if submitted and ca_id:
                ca = fetch_one("SELECT * FROM cash_advances WHERE id = ?", (ca_id,))
                amount = float(ca["amount"] or 0)
                if settlement > amount:
                    st.error("MVP ini belum menangani klaim lebih bayar. Realisasi maksimal sebesar kasbon.")
                    return
                refund = amount - settlement
                lines = []
                if settlement:
                    lines.append({"account_code": "6000", "debit": settlement, "credit": 0})
                if refund:
                    lines.append({"account_code": "1000", "debit": refund, "credit": 0})
                lines.append({"account_code": "1300", "debit": 0, "credit": amount})
                post_journal(
                    doc_date=as_iso(close_date),
                    source_type="CASH_ADVANCE_CLOSE",
                    source_no=ca["doc_no"],
                    description=f"Closing kasbon {ca['doc_no']}",
                    lines=lines,
                )
                execute(
                    """
                    UPDATE cash_advances
                    SET status = 'Closed', settlement_amount = ?, closed_at = ?, closing_notes = ?
                    WHERE id = ?
                    """,
                    (settlement, as_iso(close_date), closing_notes, ca_id),
                )
                st.success("Kasbon berhasil diclosing.")
                st.rerun()


def ar_page() -> None:
    st.subheader("Account Receivable")
    df = fetch_df(
        """
        SELECT ci.id, ci.doc_no, ci.doc_date, c.name AS customer, ci.due_date,
               ci.total, ci.paid_amount, ci.total - ci.paid_amount AS outstanding
        FROM customer_invoices ci
        JOIN customers c ON c.id = ci.customer_id
        WHERE ci.status = 'Posted'
        ORDER BY ci.due_date
        """
    )
    show_df(df.drop(columns=["id"]) if not df.empty else df)
    outstanding = df[df["outstanding"] > 0] if not df.empty else df
    if outstanding.empty:
        return
    options = {f"{row['doc_no']} - {row['customer']} - {money(row['outstanding'])}": int(row["id"]) for _, row in outstanding.iterrows()}
    with st.form("ar_payment"):
        invoice_id = select_from_map("Invoice", options, "ar_invoice")
        pay_date = st.date_input("Tanggal Terima", value=date.today())
        amount = st.number_input("Jumlah Diterima", min_value=0.0, value=0.0, step=1000.0)
        submitted = st.form_submit_button("Post Penerimaan", type="primary")
    if submitted and invoice_id:
        inv = fetch_one("SELECT doc_no, total, paid_amount FROM customer_invoices WHERE id = ?", (invoice_id,))
        max_amount = float(inv["total"] or 0) - float(inv["paid_amount"] or 0)
        if amount <= 0 or amount > max_amount:
            st.error(f"Jumlah maksimal {money(max_amount)}.")
            return
        execute("UPDATE customer_invoices SET paid_amount = paid_amount + ? WHERE id = ?", (amount, invoice_id))
        post_journal(
            doc_date=as_iso(pay_date),
            source_type="AR_PAYMENT",
            source_no=inv["doc_no"],
            description=f"Penerimaan invoice {inv['doc_no']}",
            lines=[
                {"account_code": "1000", "debit": amount, "credit": 0},
                {"account_code": "1100", "debit": 0, "credit": amount},
            ],
        )
        st.success("Penerimaan berhasil diposting.")
        st.rerun()


def ap_page() -> None:
    st.subheader("Account Payable")
    df = fetch_df(
        """
        SELECT si.id, si.doc_no, si.doc_date, s.name AS supplier, si.due_date,
               si.total, si.paid_amount, si.total - si.paid_amount AS outstanding
        FROM supplier_invoices si
        JOIN suppliers s ON s.id = si.supplier_id
        WHERE si.status = 'Posted'
        ORDER BY si.due_date
        """
    )
    show_df(df.drop(columns=["id"]) if not df.empty else df)
    outstanding = df[df["outstanding"] > 0] if not df.empty else df
    if outstanding.empty:
        return
    options = {f"{row['doc_no']} - {row['supplier']} - {money(row['outstanding'])}": int(row["id"]) for _, row in outstanding.iterrows()}
    with st.form("ap_payment"):
        invoice_id = select_from_map("Invoice Supplier", options, "ap_invoice")
        pay_date = st.date_input("Tanggal Bayar", value=date.today())
        amount = st.number_input("Jumlah Dibayar", min_value=0.0, value=0.0, step=1000.0)
        submitted = st.form_submit_button("Post Pembayaran", type="primary")
    if submitted and invoice_id:
        inv = fetch_one("SELECT doc_no, total, paid_amount FROM supplier_invoices WHERE id = ?", (invoice_id,))
        max_amount = float(inv["total"] or 0) - float(inv["paid_amount"] or 0)
        if amount <= 0 or amount > max_amount:
            st.error(f"Jumlah maksimal {money(max_amount)}.")
            return
        execute("UPDATE supplier_invoices SET paid_amount = paid_amount + ? WHERE id = ?", (amount, invoice_id))
        post_journal(
            doc_date=as_iso(pay_date),
            source_type="AP_PAYMENT",
            source_no=inv["doc_no"],
            description=f"Pembayaran invoice supplier {inv['doc_no']}",
            lines=[
                {"account_code": "2000", "debit": amount, "credit": 0},
                {"account_code": "1000", "debit": 0, "credit": amount},
            ],
        )
        st.success("Pembayaran berhasil diposting.")
        st.rerun()


def asset_page() -> None:
    st.subheader("Asset")
    with st.form("asset_create"):
        c1, c2, c3 = st.columns(3)
        with c1:
            code = st.text_input("Kode Asset", value="AST-")
            name = st.text_input("Nama Asset")
        with c2:
            acquisition_date = st.date_input("Tanggal Perolehan", value=date.today())
            acquisition_cost = st.number_input("Nilai Perolehan", min_value=0.0, value=0.0, step=1000.0)
        with c3:
            useful_life = st.number_input("Umur Manfaat Bulan", min_value=1, value=60, step=1)
            status = st.selectbox("Status", ["Active", "Disposed", "Inactive"])
        submitted = st.form_submit_button("Simpan Asset")
    if submitted:
        execute(
            """
            INSERT INTO assets (code, name, acquisition_date, acquisition_cost, useful_life_months, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code, name, as_iso(acquisition_date), acquisition_cost, useful_life, status),
        )
        st.success("Asset berhasil disimpan.")
        st.rerun()
    show_df(fetch_df("SELECT * FROM assets ORDER BY id DESC"))


def render_accounting() -> None:
    page_title("Accounting", "Journal, cash advance, AP, AR, dan asset.")
    page = st.sidebar.radio(
        "Accounting",
        ["Journal Transaction", "Cash Advance", "AP", "AR", "Asset"],
        key="accounting_page",
    )
    if page == "Journal Transaction":
        journal_transaction_page()
    elif page == "Cash Advance":
        cash_advance_page()
    elif page == "AP":
        ap_page()
    elif page == "AR":
        ar_page()
    else:
        asset_page()


# ---------------------------------------------------------------------------
# Transport, HR, Reporting, Settings
# ---------------------------------------------------------------------------


def render_transport() -> None:
    page_title("Transport", "Unit, pemakaian kendaraan, dan biaya pengiriman.")
    page = st.sidebar.radio("Transport", ["Unit", "Usage", "Cost of Delivery"], key="transport_page")
    if page == "Unit":
        show_df(master_list_df("Transportation"))
        return
    if page == "Usage":
        units = option_map("transport_units", "code || ' - ' || plate_no", "status != 'Inactive'", "code")
        drivers = option_map("drivers", "code || ' - ' || name", "active = 1", "code")
        with st.form("transport_usage"):
            c1, c2, c3 = st.columns(3)
            with c1:
                usage_date = st.date_input("Tanggal", value=date.today())
                unit_id = select_from_map("Unit", units, "tu_unit")
            with c2:
                driver_id = select_from_map("Driver", drivers, "tu_driver")
                route = st.text_input("Rute")
            with c3:
                km_start = st.number_input("KM Start", min_value=0.0, value=0.0)
                km_end = st.number_input("KM End", min_value=0.0, value=0.0)
                fuel_liter = st.number_input("Solar Liter", min_value=0.0, value=0.0)
            ref_doc = st.text_input("Referensi")
            notes = st.text_area("Catatan")
            submitted = st.form_submit_button("Simpan Usage", type="primary")
        if submitted and unit_id:
            doc_no = next_doc_no("TU", "transport_usage")
            execute(
                """
                INSERT INTO transport_usage
                (doc_no, usage_date, unit_id, driver_id, route, km_start, km_end, fuel_liter, ref_doc, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (doc_no, as_iso(usage_date), unit_id, driver_id, route, km_start, km_end, fuel_liter, ref_doc, notes),
            )
            st.success(f"Usage disimpan: {doc_no}")
            st.rerun()
        show_df(
            fetch_df(
                """
                SELECT tu.doc_no, tu.usage_date, tr.plate_no, d.name AS driver, tu.route,
                       tu.km_start, tu.km_end, tu.km_end - tu.km_start AS km_used, tu.fuel_liter, tu.ref_doc
                FROM transport_usage tu
                JOIN transport_units tr ON tr.id = tu.unit_id
                LEFT JOIN drivers d ON d.id = tu.driver_id
                ORDER BY tu.id DESC
                """
            )
        )
        return

    do_options = {"Tanpa DO": None}
    do_options.update(option_map("delivery_orders", "doc_no", "status = 'Posted'", "doc_no"))
    units = option_map("transport_units", "code || ' - ' || plate_no", "status != 'Inactive'", "code")
    with st.form("delivery_cost"):
        c1, c2, c3 = st.columns(3)
        with c1:
            cost_date = st.date_input("Tanggal Biaya", value=date.today())
            do_label = st.selectbox("Delivery Order", list(do_options.keys()))
        with c2:
            unit_id = select_from_map("Unit", units, "dc_unit")
            cost_type = st.selectbox("Jenis Biaya", ["Solar", "Tol", "Uang Jalan", "Maintenance", "Lainnya"])
        with c3:
            amount = st.number_input("Jumlah", min_value=0.0, value=0.0, step=1000.0)
        notes = st.text_area("Catatan")
        submitted = st.form_submit_button("Post Biaya Kirim", type="primary")
    if submitted:
        doc_no = next_doc_no("DC", "delivery_costs")
        execute(
            """
            INSERT INTO delivery_costs (doc_no, cost_date, delivery_order_id, unit_id, cost_type, amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (doc_no, as_iso(cost_date), do_options[do_label], unit_id, cost_type, amount, notes),
        )
        post_journal(
            doc_date=as_iso(cost_date),
            source_type="DELIVERY_COST",
            source_no=doc_no,
            description=f"Biaya delivery {doc_no}",
            lines=[
                {"account_code": "5100", "debit": amount, "credit": 0},
                {"account_code": "1000", "debit": 0, "credit": amount},
            ],
        )
        st.success(f"Biaya delivery diposting: {doc_no}")
        st.rerun()
    show_df(
        fetch_df(
            """
            SELECT dc.doc_no, dc.cost_date, do.doc_no AS delivery_order, tu.plate_no, dc.cost_type, dc.amount, dc.notes
            FROM delivery_costs dc
            LEFT JOIN delivery_orders do ON do.id = dc.delivery_order_id
            LEFT JOIN transport_units tu ON tu.id = dc.unit_id
            ORDER BY dc.id DESC
            """
        )
    )


def render_hr() -> None:
    page_title("HR", "Employee dan attendance sederhana.")
    page = st.sidebar.radio("HR", ["Employee", "Attendance"], key="hr_page")
    if page == "Employee":
        show_df(master_list_df("Employee"))
        return
    employees = option_map("employees", "code || ' - ' || name", "status = 'Active'", "code")
    with st.form("attendance"):
        c1, c2 = st.columns(2)
        with c1:
            att_date = st.date_input("Tanggal", value=date.today())
            employee_id = select_from_map("Karyawan", employees, "att_employee")
        with c2:
            status = st.selectbox("Status", ["Present", "Leave", "Sick", "Absent"])
            notes = st.text_area("Catatan")
        submitted = st.form_submit_button("Simpan Attendance", type="primary")
    if submitted and employee_id:
        execute(
            "INSERT INTO hr_attendance (attendance_date, employee_id, status, notes) VALUES (?, ?, ?, ?)",
            (as_iso(att_date), employee_id, status, notes),
        )
        st.success("Attendance disimpan.")
        st.rerun()
    show_df(
        fetch_df(
            """
            SELECT ha.attendance_date, e.code, e.name, e.department, ha.status, ha.notes
            FROM hr_attendance ha
            JOIN employees e ON e.id = ha.employee_id
            ORDER BY ha.attendance_date DESC, e.code
            """
        )
    )


def aging_bucket(days: int) -> str:
    if days <= 0:
        return "Belum jatuh tempo"
    if days <= 30:
        return "1-30"
    if days <= 60:
        return "31-60"
    if days <= 90:
        return "61-90"
    return ">90"


def aging_report(kind: str) -> None:
    if kind == "AR":
        sql = """
            SELECT ci.doc_no, ci.doc_date, c.name AS partner, ci.due_date,
                   ci.total, ci.paid_amount, ci.total - ci.paid_amount AS outstanding
            FROM customer_invoices ci
            JOIN customers c ON c.id = ci.customer_id
            WHERE ci.status = 'Posted' AND ci.total - ci.paid_amount > 0
            ORDER BY ci.due_date
        """
    else:
        sql = """
            SELECT si.doc_no, si.doc_date, s.name AS partner, si.due_date,
                   si.total, si.paid_amount, si.total - si.paid_amount AS outstanding
            FROM supplier_invoices si
            JOIN suppliers s ON s.id = si.supplier_id
            WHERE si.status = 'Posted' AND si.total - si.paid_amount > 0
            ORDER BY si.due_date
        """
    df = fetch_df(sql)
    if df.empty:
        st.info(f"Tidak ada outstanding {kind}.")
        return
    today = date.today()
    df["days_overdue"] = df["due_date"].apply(lambda x: (today - parse_iso(str(x))).days)
    df["bucket"] = df["days_overdue"].apply(aging_bucket)
    c1, c2 = st.columns([0.3, 0.7])
    with c1:
        st.metric(f"Total {kind}", money(df["outstanding"].sum()))
        st.dataframe(df.groupby("bucket", as_index=False)["outstanding"].sum(), width="stretch", hide_index=True)
    with c2:
        show_df(df)
    export_buttons(df, f"aging_{kind.lower()}", f"Aging {kind}")


def pnl_report() -> None:
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Dari Tanggal", value=date(date.today().year, 1, 1))
    with c2:
        end = st.date_input("Sampai Tanggal", value=date.today())
    df = fetch_df(
        """
        SELECT a.code, a.name, a.type, SUM(jl.debit) AS debit, SUM(jl.credit) AS credit
        FROM journal_lines jl
        JOIN journal_entries je ON je.id = jl.journal_id
        JOIN accounts a ON a.id = jl.account_id
        WHERE je.status = 'Posted'
          AND je.doc_date BETWEEN ? AND ?
          AND a.type IN ('Revenue', 'Expense')
        GROUP BY a.id
        ORDER BY a.code
        """,
        (as_iso(start), as_iso(end)),
    )
    if df.empty:
        st.info("Belum ada jurnal revenue atau expense.")
        return
    df["amount"] = df.apply(
        lambda row: float(row["credit"] or 0) - float(row["debit"] or 0)
        if row["type"] == "Revenue"
        else float(row["debit"] or 0) - float(row["credit"] or 0),
        axis=1,
    )
    revenue = df[df["type"] == "Revenue"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", money(revenue))
    c2.metric("Expense", money(expense))
    c3.metric("Net Profit", money(revenue - expense))
    show_df(df[["code", "name", "type", "amount"]])
    export_buttons(df[["code", "name", "type", "amount"]], "pnl", "Profit and Loss")


def render_reporting() -> None:
    page_title("Reporting", "Aging AP, Aging AR, dan Profit & Loss.")
    page = st.sidebar.radio("Reporting", ["Aging AP", "Aging AR", "PnL"], key="report_page")
    if page == "Aging AP":
        aging_report("AP")
    elif page == "Aging AR":
        aging_report("AR")
    else:
        pnl_report()


def render_settings(user: sqlite3.Row) -> None:
    page_title("Settings", "Pengaturan user, role, dan akses module.")
    tab_profile, tab_users, tab_roles = st.tabs(["Profil User", "User", "Role Access"])

    with tab_profile:
        with st.form("profile_form"):
            full_name = st.text_input("Nama User", value=user["full_name"])
            avatar_url = st.text_input("URL Foto / Thumbnail", value=user["avatar_url"] or "")
            submitted = st.form_submit_button("Update Profil", type="primary")
        if submitted:
            execute("UPDATE users SET full_name = ?, avatar_url = ? WHERE id = ?", (full_name, avatar_url, int(user["id"])))
            st.success("Profil berhasil diupdate.")
            st.rerun()

    with tab_users:
        roles = option_map("roles", "name", "1=1", "name")
        with st.form("user_create"):
            c1, c2 = st.columns(2)
            with c1:
                username = st.text_input("Username")
                full_name = st.text_input("Nama Lengkap")
            with c2:
                role_id = select_from_map("Role", roles, "new_user_role")
                avatar_url = st.text_input("URL Foto")
            submitted = st.form_submit_button("Create User", type="primary")
        if submitted and role_id:
            execute(
                "INSERT INTO users (username, full_name, role_id, avatar_url, active) VALUES (?, ?, ?, ?, 1)",
                (username, full_name, role_id, avatar_url),
            )
            st.success("User berhasil dibuat.")
            st.rerun()
        show_df(
            fetch_df(
                """
                SELECT u.username, u.full_name, r.name AS role, u.active, u.avatar_url
                FROM users u
                JOIN roles r ON r.id = u.role_id
                ORDER BY u.full_name
                """
            )
        )

    with tab_roles:
        role_df = fetch_df("SELECT id, name FROM roles ORDER BY name")
        role_labels = {row["name"]: int(row["id"]) for _, row in role_df.iterrows()}
        selected_role = st.selectbox("Role", list(role_labels.keys()))
        role_id = role_labels[selected_role]
        current = set(role_modules(role_id))
        picked = st.multiselect(
            "Module yang boleh diakses",
            list(MODULES.keys()),
            default=[module for module in MODULES.keys() if module in current],
            format_func=lambda key: MODULES[key]["label"],
        )
        if st.button("Update Access", type="primary"):
            conn = get_conn()
            with conn:
                conn.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
                for module_key in picked:
                    conn.execute(
                        "INSERT INTO role_permissions (role_id, module_key, can_access) VALUES (?, ?, 1)",
                        (role_id, module_key),
                    )
            st.success("Akses role berhasil diupdate.")
            st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    init_db()
    module, user = render_sidebar()
    if module == "Dashboard":
        render_dashboard()
    elif module == "Master":
        render_master()
    elif module == "Inventory":
        render_inventory()
    elif module == "Sales":
        render_sales()
    elif module == "Purchase":
        render_purchase()
    elif module == "Accounting":
        render_accounting()
    elif module == "Transport":
        render_transport()
    elif module == "HR":
        render_hr()
    elif module == "Reporting":
        render_reporting()
    elif module == "Settings":
        render_settings(user)


if __name__ == "__main__":
    main()
