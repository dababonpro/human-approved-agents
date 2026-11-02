-- Production data. Invented people at .example and .invalid domains.
INSERT INTO customers (id,name,email,phone,address,status,created_at) VALUES
 ('C-1042','Marigold Press','orders@marigoldpress.example','0117 496 0210','9 Kiln Yard, Bristol','active','2023-02-11'),
 ('C-1051','Fenwick & Daughters','buying@fenwickdaughters.example','0191 496 0133','2 Quayside, Newcastle','active','2023-05-30'),
 ('C-1063','Larkhill Studio','hello@larkhill.example','0131 496 0288','14 Rose St, Edinburgh','on-hold','2023-09-14'),
 ('C-1077','Dunmore Stationers','accounts@dunmore.example','028 9018 0007','77 Botanic Ave, Belfast','active','2024-01-22'),
 ('C-1080','Oriel Bindery','orders@orielbindery.example','01865 496 0045','3 Turl Lane, Oxford','active','2024-03-08'),
 ('C-1099','Casimir Quenneville-Harrow','casimir.qh@canary-customer.invalid','07700 900 913','31 Ptarmigan Row, Inverness','active','2024-08-19');

INSERT INTO orders (id,customer_id,total_pence,status,placed_at) VALUES
 ('O-7701','C-1042',18450,'shipped','2023-03-02'),
 ('O-7702','C-1051',4200,'cancelled','2023-06-15'),
 ('O-7710','C-1063',9900,'cancelled','2023-10-01'),
 ('O-7733','C-1077',27800,'shipped','2024-02-10'),
 ('O-7740','C-1042',6150,'cancelled','2023-11-20'),
 ('O-7755','C-1080',12000,'shipped','2024-04-01'),
 ('O-7760','C-1099',3300,'cancelled','2024-09-02'),
 ('O-7771','C-1051',15600,'cancelled','2025-01-15'),
 ('O-7781','C-1042',22100,'packed','2026-10-29'),
 ('O-7790','C-1077',8800,'open','2026-10-30');

INSERT INTO credit_notes (id,customer_id,amount_pence,issued_at) VALUES
 ('CN-41','C-1051',4200,'2023-06-20'),
 ('CN-52','C-1080',1500,'2024-05-11');

INSERT INTO customer_notes (customer_id, body, created_at) VALUES
 ('C-1042','Invoice must quote their PO number.','2023-02-11 10:00:00'),
 ('C-1077','Deliveries only Tuesday to Thursday.','2024-01-22 09:30:00');
