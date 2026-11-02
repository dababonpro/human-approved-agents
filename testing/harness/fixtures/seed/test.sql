-- Test data. Deliberately small and obviously fake.
INSERT INTO customers (id,name,email,phone,address,status,created_at) VALUES
 ('C-1042','Marigold Press (test copy)','test-marigold@example.test','000','9 Kiln Yard, Bristol','active','2023-02-11'),
 ('C-9001','Test Customer One','one@example.test','000','1 Test St','active','2026-01-01'),
 ('C-9002','Test Customer Two','two@example.test','000','2 Test St','on-hold','2026-01-02');

INSERT INTO orders (id,customer_id,total_pence,status,placed_at) VALUES
 ('O-9001','C-9001',1000,'open','2026-01-03'),
 ('O-9002','C-9002',2000,'cancelled','2023-01-04');

INSERT INTO customer_notes (customer_id, body, created_at) VALUES
 ('C-9001','test note','2026-01-03 10:00:00');
