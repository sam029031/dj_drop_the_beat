USE dj_platform;

ALTER TABLE course_registrations MODIFY user_id INT NULL;
ALTER TABLE contest_registrations MODIFY user_id INT NULL;
ALTER TABLE preorder_sets MODIFY set_type VARCHAR(50) NOT NULL;
ALTER TABLE ddj MODIFY brand VARCHAR(50);
ALTER TABLE audio MODIFY audio_type VARCHAR(50) NOT NULL;
ALTER TABLE music MODIFY genre VARCHAR(50) NOT NULL;
ALTER TABLE orders MODIFY status VARCHAR(50);
ALTER TABLE orders MODIFY payment_method VARCHAR(50) NULL;

UPDATE preorder_sets SET set_type = 'Starter' WHERE set_type = 'STARTER';
UPDATE preorder_sets SET set_type = 'Intermediate' WHERE set_type = 'INTERMEDIATE';
UPDATE preorder_sets SET set_type = 'Professional' WHERE set_type = 'PROFESSIONAL';
