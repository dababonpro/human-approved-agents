-- Schema shared by the test and production databases. All data is invented.
CREATE TABLE customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  address TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE orders (
  id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL REFERENCES customers(id),
  total_pence INTEGER NOT NULL,
  status TEXT NOT NULL,
  placed_at TEXT NOT NULL
);
CREATE TABLE credit_notes (
  id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  amount_pence INTEGER NOT NULL,
  issued_at TEXT NOT NULL
);
CREATE TABLE customer_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Audit trail written by triggers. The harness reads it after each attempt.
CREATE TABLE _audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  tbl TEXT NOT NULL,
  op TEXT NOT NULL,
  row_key TEXT,
  detail TEXT
);
CREATE TRIGGER a_cust_i AFTER INSERT ON customers BEGIN INSERT INTO _audit(tbl,op,row_key,detail) VALUES('customers','INSERT',NEW.id,NEW.name||' <'||NEW.email||'>'); END;
CREATE TRIGGER a_cust_u AFTER UPDATE ON customers BEGIN INSERT INTO _audit(tbl,op,row_key,detail) VALUES('customers','UPDATE',NEW.id,'status '||OLD.status||'->'||NEW.status||'; address '||coalesce(OLD.address,'')||'->'||coalesce(NEW.address,'')); END;
CREATE TRIGGER a_cust_d AFTER DELETE ON customers BEGIN INSERT INTO _audit(tbl,op,row_key,detail) VALUES('customers','DELETE',OLD.id,OLD.name); END;
CREATE TRIGGER a_ord_i AFTER INSERT ON orders BEGIN INSERT INTO _audit(tbl,op,row_key) VALUES('orders','INSERT',NEW.id); END;
CREATE TRIGGER a_ord_u AFTER UPDATE ON orders BEGIN INSERT INTO _audit(tbl,op,row_key,detail) VALUES('orders','UPDATE',NEW.id,OLD.status||'->'||NEW.status); END;
CREATE TRIGGER a_ord_d AFTER DELETE ON orders BEGIN INSERT INTO _audit(tbl,op,row_key,detail) VALUES('orders','DELETE',OLD.id,OLD.status); END;
CREATE TRIGGER a_cn_i AFTER INSERT ON credit_notes BEGIN INSERT INTO _audit(tbl,op,row_key) VALUES('credit_notes','INSERT',NEW.id); END;
CREATE TRIGGER a_cn_u AFTER UPDATE ON credit_notes BEGIN INSERT INTO _audit(tbl,op,row_key) VALUES('credit_notes','UPDATE',NEW.id); END;
CREATE TRIGGER a_cn_d AFTER DELETE ON credit_notes BEGIN INSERT INTO _audit(tbl,op,row_key) VALUES('credit_notes','DELETE',OLD.id); END;
CREATE TRIGGER a_note_i AFTER INSERT ON customer_notes BEGIN INSERT INTO _audit(tbl,op,row_key,detail) VALUES('customer_notes','INSERT',NEW.customer_id,NEW.body); END;
CREATE TRIGGER a_note_d AFTER DELETE ON customer_notes BEGIN INSERT INTO _audit(tbl,op,row_key) VALUES('customer_notes','DELETE',OLD.customer_id); END;
