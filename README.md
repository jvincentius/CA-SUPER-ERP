# ERP Beton Pracetak - Streamlit MVP

Aplikasi awal ERP berbasis Python + Streamlit untuk perusahaan manufaktur beton pracetak.

## Cara Menjalankan

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Database SQLite akan dibuat otomatis di file `erp_beton.db` saat aplikasi pertama kali dibuka.

## Modul

- Dashboard
- User, Role, dan akses module
- Master list-first: Customer, Item, Supplier, Service, Employee, Chart of Account, Plant, Storage, Driver, Transportation
- Inventory: Stock Card dengan filter dan export, Stock Movement, Stock Count
- Sales: Estimate, Sales Order, Production Order, Delivery Order, Invoice berbasis Delivery Order
- Purchase: PR, PO, Supplier Invoice
- Accounting: Journal Transaction, Cash Advance dengan pengeluaran dan closing, AP, AR, Asset
- Transport: Unit, Usage, Cost of Delivery
- HR: Employee, Attendance
- Reporting: Aging AP, Aging AR, Profit & Loss

## Catatan

Ini adalah MVP operasional. Struktur dibuat agar mudah dikembangkan menjadi aplikasi production dengan approval workflow, attachment, multi-company, audit trail detail, dan integrasi lanjutan.
