    -- ============================================
-- 1. ROOMS (8 prostorija)
-- ============================================

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Yoga Studio', 'Floor 1', 20, 0);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Spin Room', 'Floor 1', 15, 1);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Weight Room', 'Floor 2', 30, 1);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Cardio Zone', 'Floor 2', 25, 1);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Group Fitness Studio', 'Floor 1', 25, 0);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Pilates Studio', 'Floor 3', 12, 1);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Boxing Ring', 'Floor 2', 10, 1);

MERGE INTO rooms r
USING (SELECT HEXTORAW(REPLACE('b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e', '-', '')) AS id FROM dual) src
ON (r.room_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity, has_equipment)
    VALUES (src.id, 'Dance Studio', 'Floor 3', 30, 0);

-- ============================================
-- 2. TRAINERS (8 trenera)
-- ============================================

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('11111111-2222-4333-8444-555555555555', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'Sarah Martinez', 'Yoga', 'sarah.m@fitness.com', '+1-555-0101', 4.8);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('22222222-3333-4444-8555-666666666666', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'Mike Johnson', 'Strength Training', 'mike.j@fitness.com', '+1-555-0102', 4.9);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('33333333-4444-4555-8666-777777777777', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'Emma Davis', 'HIIT', 'emma.d@fitness.com', '+1-555-0103', 4.7);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('44444444-5555-4666-8777-888888888888', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'John Smith', 'Boxing', 'john.s@fitness.com', '+1-555-0104', 4.6);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('55555555-6666-4777-8888-999999999999', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'Lisa Anderson', 'Pilates', 'lisa.a@fitness.com', '+1-555-0105', 4.9);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('66666666-7777-4888-8999-aaaaaaaaaaaa', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'David Brown', 'CrossFit', 'david.b@fitness.com', '+1-555-0106', 4.5);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('77777777-8888-4999-8aaa-bbbbbbbbbbbb', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'Rachel Green', 'Dance', 'rachel.g@fitness.com', '+1-555-0107', 4.8);

MERGE INTO trainers t
USING (SELECT HEXTORAW(REPLACE('88888888-9999-4aaa-8bbb-cccccccccccc', '-', '')) AS id FROM dual) src
ON (t.trainer_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email, phone, rating)
    VALUES (src.id, 'Tom Wilson', 'Spinning', 'tom.w@fitness.com', '+1-555-0108', 4.7);

-- ============================================
-- 3. CLASSES (10 časova - next 7 days)
-- ============================================

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Morning Yoga',
        HEXTORAW(REPLACE('11111111-2222-4333-8444-555555555555', '-', '')),
        HEXTORAW(REPLACE('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '-', '')),
        TO_TIMESTAMP('2025-12-08 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 09:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        20, 15.00, 'Start your day with energizing yoga flow'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0002-4000-8000-000000000002', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Strength Training',
        HEXTORAW(REPLACE('22222222-3333-4444-8555-666666666666', '-', '')),
        HEXTORAW(REPLACE('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', '-', '')),
        TO_TIMESTAMP('2025-12-08 10:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 11:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        15, 18.00, 'Build muscle and strength'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0003-4000-8000-000000000003', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Spin Class',
        HEXTORAW(REPLACE('88888888-9999-4aaa-8bbb-cccccccccccc', '-', '')),
        HEXTORAW(REPLACE('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '-', '')),
        TO_TIMESTAMP('2025-12-08 12:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 12:45:00', 'YYYY-MM-DD HH24:MI:SS'),
        15, 20.00, 'Indoor cycling workout'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0004-4000-8000-000000000004', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'HIIT Cardio',
        HEXTORAW(REPLACE('33333333-4444-4555-8666-777777777777', '-', '')),
        HEXTORAW(REPLACE('e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b', '-', '')),
        TO_TIMESTAMP('2025-12-08 17:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 17:45:00', 'YYYY-MM-DD HH24:MI:SS'),
        25, 12.00, 'High intensity interval training'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0005-4000-8000-000000000005', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Pilates Core',
        HEXTORAW(REPLACE('55555555-6666-4777-8888-999999999999', '-', '')),
        HEXTORAW(REPLACE('f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c', '-', '')),
        TO_TIMESTAMP('2025-12-08 18:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 18:50:00', 'YYYY-MM-DD HH24:MI:SS'),
        12, 22.00, 'Core strengthening and flexibility'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0006-4000-8000-000000000006', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Boxing Basics',
        HEXTORAW(REPLACE('44444444-5555-4666-8777-888888888888', '-', '')),
        HEXTORAW(REPLACE('a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d', '-', '')),
        TO_TIMESTAMP('2025-12-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 20:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        10, 25.00, 'Learn boxing fundamentals'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0007-4000-8000-000000000007', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Dance Fitness',
        HEXTORAW(REPLACE('77777777-8888-4999-8aaa-bbbbbbbbbbbb', '-', '')),
        HEXTORAW(REPLACE('b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e', '-', '')),
        TO_TIMESTAMP('2025-12-08 19:30:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-08 20:15:00', 'YYYY-MM-DD HH24:MI:SS'),
        30, 10.00, 'Fun dance-based cardio workout'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0008-4000-8000-000000000008', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Morning Yoga',
        HEXTORAW(REPLACE('11111111-2222-4333-8444-555555555555', '-', '')),
        HEXTORAW(REPLACE('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '-', '')),
        TO_TIMESTAMP('2025-12-09 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-09 09:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        20, 15.00, 'Start your day with energizing yoga flow'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0009-4000-8000-000000000009', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Strength Training',
        HEXTORAW(REPLACE('22222222-3333-4444-8555-666666666666', '-', '')),
        HEXTORAW(REPLACE('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', '-', '')),
        TO_TIMESTAMP('2025-12-09 10:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-09 11:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        15, 18.00, 'Build muscle and strength'
    );

MERGE INTO classes c
USING (SELECT HEXTORAW(REPLACE('c1000000-0010-4000-8000-000000000010', '-', '')) AS id FROM dual) src
ON (c.class_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price, description)
    VALUES (
        src.id,
        'Spin Class',
        HEXTORAW(REPLACE('88888888-9999-4aaa-8bbb-cccccccccccc', '-', '')),
        HEXTORAW(REPLACE('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '-', '')),
        TO_TIMESTAMP('2025-12-09 12:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        TO_TIMESTAMP('2025-12-09 12:45:00', 'YYYY-MM-DD HH24:MI:SS'),
        15, 20.00, 'Indoor cycling workout'
    );

-- ============================================
-- 4. ATTENDANCES (10 attendance records)
-- ============================================

-- Mock member IDs (simulating members from member service)
MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000001-0000-4000-8000-000000000001', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')),
        HEXTORAW(REPLACE('00000001-0000-4000-8000-000000000001', '-', '')),
        TO_TIMESTAMP('2025-12-08 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000002-0000-4000-8000-000000000002', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')),
        HEXTORAW(REPLACE('00000002-0000-4000-8000-000000000002', '-', '')),
        TO_TIMESTAMP('2025-12-08 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000003-0000-4000-8000-000000000003', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')),
        HEXTORAW(REPLACE('00000003-0000-4000-8000-000000000003', '-', '')),
        TO_TIMESTAMP('2025-12-08 08:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000004-0000-4000-8000-000000000004', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0002-4000-8000-000000000002', '-', '')),
        HEXTORAW(REPLACE('00000004-0000-4000-8000-000000000004', '-', '')),
        TO_TIMESTAMP('2025-12-08 10:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000005-0000-4000-8000-000000000005', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0002-4000-8000-000000000002', '-', '')),
        HEXTORAW(REPLACE('00000005-0000-4000-8000-000000000005', '-', '')),
        TO_TIMESTAMP('2025-12-08 10:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000006-0000-4000-8000-000000000006', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0003-4000-8000-000000000003', '-', '')),
        HEXTORAW(REPLACE('00000006-0000-4000-8000-000000000006', '-', '')),
        TO_TIMESTAMP('2025-12-08 12:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000007-0000-4000-8000-000000000007', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0004-4000-8000-000000000004', '-', '')),
        HEXTORAW(REPLACE('00000007-0000-4000-8000-000000000007', '-', '')),
        TO_TIMESTAMP('2025-12-08 17:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000008-0000-4000-8000-000000000008', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0004-4000-8000-000000000004', '-', '')),
        HEXTORAW(REPLACE('00000008-0000-4000-8000-000000000008', '-', '')),
        TO_TIMESTAMP('2025-12-08 17:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000009-0000-4000-8000-000000000009', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0005-4000-8000-000000000005', '-', '')),
        HEXTORAW(REPLACE('00000009-0000-4000-8000-000000000009', '-', '')),
        TO_TIMESTAMP('2025-12-08 18:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

MERGE INTO attendances a
USING (SELECT HEXTORAW(REPLACE('a0000010-0000-4000-8000-000000000010', '-', '')) AS id FROM dual) src
ON (a.event_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('c1000000-0006-4000-8000-000000000006', '-', '')),
        HEXTORAW(REPLACE('00000010-0000-4000-8000-000000000010', '-', '')),
        TO_TIMESTAMP('2025-12-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),
        'checked-in'
    );

-- ============================================
-- 5. PAYMENTS (10 payment records)
-- ============================================

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000001-0000-4000-8000-000000000001', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000001-0000-4000-8000-000000000001', '-', '')),
        HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')),
        15.00,
        TO_TIMESTAMP('2025-12-08 07:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000002-0000-4000-8000-000000000002', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000002-0000-4000-8000-000000000002', '-', '')),
        HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')),
        15.00,
        TO_TIMESTAMP('2025-12-08 07:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000003-0000-4000-8000-000000000003', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000003-0000-4000-8000-000000000003', '-', '')),
        HEXTORAW(REPLACE('c1000000-0001-4000-8000-000000000001', '-', '')),
        15.00,
        TO_TIMESTAMP('2025-12-08 07:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000004-0000-4000-8000-000000000004', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000004-0000-4000-8000-000000000004', '-', '')),
        HEXTORAW(REPLACE('c1000000-0002-4000-8000-000000000002', '-', '')),
        18.00,
        TO_TIMESTAMP('2025-12-08 09:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000005-0000-4000-8000-000000000005', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000005-0000-4000-8000-000000000005', '-', '')),
        HEXTORAW(REPLACE('c1000000-0002-4000-8000-000000000002', '-', '')),
        18.00,
        TO_TIMESTAMP('2025-12-08 09:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000006-0000-4000-8000-000000000006', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000006-0000-4000-8000-000000000006', '-', '')),
        HEXTORAW(REPLACE('c1000000-0003-4000-8000-000000000003', '-', '')),
        20.00,
        TO_TIMESTAMP('2025-12-08 11:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000007-0000-4000-8000-000000000007', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000007-0000-4000-8000-000000000007', '-', '')),
        HEXTORAW(REPLACE('c1000000-0004-4000-8000-000000000004', '-', '')),
        12.00,
        TO_TIMESTAMP('2025-12-08 16:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000008-0000-4000-8000-000000000008', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000008-0000-4000-8000-000000000008', '-', '')),
        HEXTORAW(REPLACE('c1000000-0004-4000-8000-000000000004', '-', '')),
        12.00,
        TO_TIMESTAMP('2025-12-08 16:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000009-0000-4000-8000-000000000009', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000009-0000-4000-8000-000000000009', '-', '')),
        HEXTORAW(REPLACE('c1000000-0005-4000-8000-000000000005', '-', '')),
        22.00,
        TO_TIMESTAMP('2025-12-08 17:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

MERGE INTO payments p
USING (SELECT HEXTORAW(REPLACE('00000010-0000-4000-8000-000000000010', '-', '')) AS id FROM dual) src
ON (p.payment_id = src.id)
WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (
        src.id,
        HEXTORAW(REPLACE('00000010-0000-4000-8000-000000000010', '-', '')),
        HEXTORAW(REPLACE('c1000000-0006-4000-8000-000000000006', '-', '')),
        25.00,
        TO_TIMESTAMP('2025-12-08 18:30:00', 'YYYY-MM-DD HH24:MI:SS')
    );

COMMIT;
