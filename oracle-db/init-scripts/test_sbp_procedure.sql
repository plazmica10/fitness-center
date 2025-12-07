
    SET SERVEROUTPUT ON SIZE 1000000;
    PROMPT
    PROMPT ===============================
    PROMPT STARTING sbp_procedure TESTS
    PROMPT ===============================

    PROMPT Creating test trainer, room and class (idempotent MERGE)...

    MERGE INTO trainers t
    USING (
    SELECT HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000001','-','')) AS id,
            'Test Trainer' AS name,
            'Fitness' AS specialization,
            'trainer@example.com' AS email
    FROM dual
    ) src
    ON (t.trainer_id = src.id)
    WHEN NOT MATCHED THEN
    INSERT (trainer_id, name, specialization, email)
    VALUES (src.id, src.name, src.specialization, src.email);

    MERGE INTO rooms r
    USING (
    SELECT HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000002','-','')) AS id,
            'Test Room' AS name,
            '1st floor' AS location,
            20 AS capacity
    FROM dual
    ) src
    ON (r.room_id = src.id)
    WHEN NOT MATCHED THEN
    INSERT (room_id, name, location, capacity)
    VALUES (src.id, src.name, src.location, src.capacity);

    -- For class start/end times use current date/time
    MERGE INTO classes c
    USING (
    SELECT HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-','')) AS id,
            'Test Class' AS name,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000001','-','')) AS trainer_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000002','-','')) AS room_id,
            SYSTIMESTAMP AS start_time,
            SYSTIMESTAMP + NUMTODSINTERVAL(1,'HOUR') AS end_time,
            20 AS capacity,
            15.00 AS price
    FROM dual
    ) src
    ON (c.class_id = src.id)
    WHEN NOT MATCHED THEN
    INSERT (class_id, name, trainer_id, room_id, start_time, end_time, capacity, price)
    VALUES (src.id, src.name, src.trainer_id, src.room_id, src.start_time, src.end_time, src.capacity, src.price);

    COMMIT;

    PROMPT Inserting test payments and attendances (idempotent MERGE)...

    -- Insert two payments for the same member
    MERGE INTO payments p
    USING (
    SELECT HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-','')) AS member_id,
            SYS_GUID() AS payment_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-','')) AS class_id,
            20.00 AS amount,
            SYSTIMESTAMP AS ts
    FROM dual
    ) src
    ON (1=0) -- force insert via WHEN NOT MATCHED (unique payment_id prevents duplicate on reruns)
    WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (src.payment_id, src.member_id, src.class_id, src.amount, src.ts);

    MERGE INTO payments p2
    USING (
    SELECT SYS_GUID() AS payment_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-','')) AS member_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-','')) AS class_id,
            10.00 AS amount,
            SYSTIMESTAMP - NUMTODSINTERVAL(1,'DAY') AS ts
    FROM dual
    ) src
    ON (1=0)
    WHEN NOT MATCHED THEN
    INSERT (payment_id, member_id, class_id, amount, timestamp)
    VALUES (src.payment_id, src.member_id, src.class_id, src.amount, src.ts);

    COMMIT;

    -- Insert attendances to trigger classes.total_attendance update
    PROMPT Inserting two attendances to test trigger...

    MERGE INTO attendances a
    USING (
    SELECT SYS_GUID() AS event_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-','')) AS class_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-','')) AS member_id,
            SYSTIMESTAMP AS ts,
            'checked-in' AS status
    FROM dual
    ) src
    ON (1=0)
    WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (src.event_id, src.class_id, src.member_id, src.ts, src.status);

    MERGE INTO attendances a2
    USING (
    SELECT SYS_GUID() AS event_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-','')) AS class_id,
            HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-','')) AS member_id,
            SYSTIMESTAMP - NUMTODSINTERVAL(1,'DAY') AS ts,
            'checked-in' AS status
    FROM dual
    ) src
    ON (1=0)
    WHEN NOT MATCHED THEN
    INSERT (event_id, class_id, member_id, timestamp, status)
    VALUES (src.event_id, src.class_id, src.member_id, src.ts, src.status);

    COMMIT;

    PROMPT Checking results: function IZRACUNAJ_IZDATKE_CLANA and classes.total_attendance

    SET SERVEROUTPUT ON;
    DECLARE
    v_total NUMBER;
    v_attendance NUMBER;
    BEGIN
    v_total := IZRACUNAJ_IZDATKE_CLANA(HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-','')));
    DBMS_OUTPUT.PUT_LINE('IZRACUNAJ_IZDATKE_CLANA returned: ' || v_total);

    SELECT NVL(total_attendance,0) INTO v_attendance FROM classes WHERE class_id = HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-',''));
    DBMS_OUTPUT.PUT_LINE('classes.total_attendance for test class: ' || v_attendance);
    EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error checking results: ' || SQLERRM);
    END;
    /

    PROMPT Calling GENERISI_MESECNI_IZVESTAJ_TRENERA for current month/year...
    BEGIN
    GENERISI_MESECNI_IZVESTAJ_TRENERA(EXTRACT(MONTH FROM SYSDATE), EXTRACT(YEAR FROM SYSDATE), HEXTORAW(REPLACE('00000000-0000-0000-0000-0000000000FF','-','')));
    DBMS_OUTPUT.PUT_LINE('GENERISI_MESECNI_IZVESTAJ_TRENERA executed.');
    END;
    /
    PROMPT Showing most recent report content (short preview)...
    SET PAGESIZE 200
    COLUMN created_at FORMAT A30
    SELECT report_id, report_type, DBMS_LOB.SUBSTR(content, 2000, 1) AS content_preview, created_at
    FROM reports
    WHERE report_type = 'mesecni_treneri'
    ORDER BY created_at DESC;

    PROMPT Tests complete.

    -- Cleanup (optional): uncomment to remove test rows
    DELETE FROM reports WHERE created_by = HEXTORAW(REPLACE('00000000-0000-0000-0000-0000000000FF','-',''));
    DELETE FROM attendances WHERE member_id = HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-',''));
    DELETE FROM payments WHERE member_id = HEXTORAW(REPLACE('00000000-0000-0000-0000-00000000000A','-',''));
    DELETE FROM classes WHERE class_id = HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000003','-',''));
    DELETE FROM trainers WHERE trainer_id = HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000001','-',''));
    DELETE FROM rooms WHERE room_id = HEXTORAW(REPLACE('00000000-0000-0000-0000-000000000002','-',''));
    COMMIT;
