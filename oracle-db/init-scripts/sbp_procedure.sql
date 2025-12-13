/*
====================================================================================================================================
 ZADATAK 1: PL/SQL TRIGER
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Kreiranje jednog netrivijalnog trigera (AFTER INSERT).

 Triger koji se aktivira NAKON unosa novog prisustva (ATTENDANCE) i automatski
           preračunava i ažurira kolonu `total_attendance` na roditeljskoj tabeli `CLASSES`.
           Pre toga skripta dodaje potrebna kolone (ako ne postoje).
====================================================================================================================================
*/

-- Dodajemo kolone `total_attendance` i `total_revenue` u tabelu `CLASSES` ako već ne postoje
BEGIN
    EXECUTE IMMEDIATE 'ALTER TABLE classes ADD (total_attendance NUMBER DEFAULT 0)';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -01430 THEN -- ignore "column already exists" in some Oracle versions (-01430 may differ)
            NULL; -- tiho nastavi
        END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'ALTER TABLE classes ADD (total_revenue NUMBER(12,2) DEFAULT 0)';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -01430 THEN
            NULL;
        END IF;
END;
/
-- TRIGER: Nakon unosa novog reda u tabelu `ATTENDANCES` ažuriramo `classes.total_attendance`
CREATE OR REPLACE TRIGGER AZURIRAJ_CLASSES_NAKON_ATTENDANCE_INSERT
AFTER INSERT ON attendances
DECLARE
BEGIN
    -- Ažuriraj ukupan broj prisustava po času (grupišemo po class_id)
    MERGE INTO classes C
    USING (
        SELECT class_id, COUNT(*) AS total_att
        FROM attendances
        GROUP BY class_id
    ) A
    ON (C.class_id = A.class_id)
    WHEN MATCHED THEN
      UPDATE SET C.total_attendance = A.total_att;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška u trigeru AZURIRAJ_CLASSES_NAKON_ATTENDANCE_INSERT: ' || SQLERRM);
        RAISE;
END;
/

/*
====================================================================================================================================
 ZADATAK 2: PL/SQL FUNKCIJA
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Funkcija koja prima ID člana (`member_id`) i računa ukupan iznos koji je taj član platio
         (spoj payment i classes -> najmanje 2 tabele). Funkcija uključuje obradu izuzetaka.

 REŠENJE: Funkcija `IZRACUNAJ_IZDATKE_CLANA` vraća zbir kolone `amount` iz tabele `payments`
           za zadatog člana. Dodatno spajamo tabelu `classes` da bismo mogli filtrirati npr. po datumu časa.
====================================================================================================================================
*/

CREATE OR REPLACE FUNCTION IZRACUNAJ_IZDATKE_CLANA(
    p_member_id IN RAW
) RETURN NUMBER
IS
    v_total_spent NUMBER := 0;
BEGIN
    SELECT NVL(SUM(p.amount), 0)
    INTO v_total_spent
    FROM payments p
    JOIN classes c ON p.class_id = c.class_id
    WHERE p.member_id = p_member_id;

    RETURN v_total_spent;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška u funkciji IZRACUNAJ_IZDATKE_CLANA: ' || SQLERRM);
        RETURN -1;
END;
/
-- Primer poziva funkcije (preko HEXTORAW za hex string):
-- SELECT IZRACUNAJ_IZDATKE_CLANA(HEXTORAW('00000001000040008000000000000001')) FROM dual;


/*
====================================================================================================================================
 ZADATAK 3: SQL INDEKSI
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV:  A) Uupit sa filtriranjem (po datumu) i agregacijom nad tabelom `payments` (join sa `classes` i `trainers`).
         B) EXPLAIN PLAN pre indeksa.
         C) Kompozitni B-tree indeks koji optimizuje taj upit.
         D) EXPLAIN PLAN posle indeksa.

 Upit računa ukupnu zaradu i broj plaćanja po treneru za zadati period.
====================================================================================================================================
*/
-- E) Generisanje 100,000 mock redova u tabeli `payments` (koristimo SYS_GUID za payment_id i random članove)
DECLARE
    v_count NUMBER := 100000;
    v_batch NUMBER := 5000; -- ubacuj u batch-evima radi performansi
    v_done NUMBER := 0;
    v_random_class RAW(16);
    v_min_date DATE := SYSDATE - 365; -- unazad godinu dana
BEGIN
    DBMS_OUTPUT.PUT_LINE('Počinje generisanje ' || v_count || ' mock plaćanja...');

    WHILE v_done < v_count LOOP
        FOR i IN 1..v_batch LOOP
            -- Izaberemo nasumičan postojeći class_id (ako nema klasa, ubacićemo NULL pa će FK ako postoji puknuti)
            BEGIN
                SELECT class_id INTO v_random_class FROM (
                    SELECT class_id FROM classes ORDER BY DBMS_RANDOM.RANDOM
                ) WHERE ROWNUM = 1;
            EXCEPTION
                WHEN NO_DATA_FOUND THEN
                    v_random_class := NULL;
            END;

            INSERT /*+ APPEND */ INTO payments(payment_id, member_id, class_id, amount, timestamp)
            VALUES (
                SYS_GUID(),
                SYS_GUID(),
                v_random_class,
                TRUNC(DBMS_RANDOM.VALUE(5, 100), 2),
                v_min_date + DBMS_RANDOM.VALUE(0, 365)
            );
        END LOOP;

        v_done := v_done + v_batch;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Ubaceeno: ' || v_done);
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('Generisanje završeno. Ukupno ubaceno: ' || v_done);
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška pri generisanju mock plaćanja: ' || SQLERRM);
        ROLLBACK;
END;
/

--------------------------------------
PROMPT
PROMPT ============================================
PROMPT TESTIRANJE BEZ INDEKSA
PROMPT ============================================

SET TIMING ON;
-- A) Upit: ukupna zarada i broj plaćanja po treneru za prošli mesec
SELECT t.trainer_id, t.name, COUNT(p.payment_id) AS broj_placanja, SUM(p.amount) AS ukupna_zarada
FROM payments p
JOIN classes c ON p.class_id = c.class_id
JOIN trainers t ON c.trainer_id = t.trainer_id
WHERE p.timestamp >= TRUNC(ADD_MONTHS(SYSDATE, -1), 'MM')
  AND p.timestamp < TRUNC(SYSDATE, 'MM')
GROUP BY t.trainer_id, t.name;
SET TIMING OFF;

PROMPT
PROMPT Execution plan BEZ indeksa:
EXPLAIN PLAN FOR 
SELECT t.trainer_id, t.name, COUNT(p.payment_id) AS broj_placanja, SUM(p.amount) AS ukupna_zarada
FROM payments p
JOIN classes c ON p.class_id = c.class_id
JOIN trainers t ON c.trainer_id = t.trainer_id
WHERE p.timestamp >= TRUNC(ADD_MONTHS(SYSDATE, -1), 'MM')
  AND p.timestamp < TRUNC(SYSDATE, 'MM')
GROUP BY t.trainer_id, t.name;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY(NULL, NULL, 'BASIC +COST'));

PROMPT
PROMPT ============================================
PROMPT KREIRANJE INDEKSA
PROMPT ============================================

-- C) Kreiramo kompozitni indeks na kolonama koje se koriste za filtriranje i join
BEGIN
    EXECUTE IMMEDIATE 'CREATE INDEX IDX_PAYMENTS_TS_CLASS ON payments(timestamp, class_id)';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -955 THEN -- ORA-00955: name is already used by an existing object
            RAISE;
        END IF;
END;
/

PROMPT
PROMPT ============================================
PROMPT TESTIRANJE SA INDEKSOM
PROMPT ============================================

SET TIMING ON;
SELECT t.trainer_id, t.name, COUNT(p.payment_id) AS broj_placanja, SUM(p.amount) AS ukupna_zarada
FROM payments p
JOIN classes c ON p.class_id = c.class_id
JOIN trainers t ON c.trainer_id = t.trainer_id
WHERE p.timestamp >= TRUNC(ADD_MONTHS(SYSDATE, -1), 'MM')
  AND p.timestamp < TRUNC(SYSDATE, 'MM')
GROUP BY t.trainer_id, t.name;
SET TIMING OFF;

PROMPT
PROMPT Execution plan SA indeksom:
EXPLAIN PLAN FOR 
SELECT t.trainer_id, t.name, COUNT(p.payment_id) AS broj_placanja, SUM(p.amount) AS ukupna_zarada
FROM payments p
JOIN classes c ON p.class_id = c.class_id
JOIN trainers t ON c.trainer_id = t.trainer_id
WHERE p.timestamp >= TRUNC(ADD_MONTHS(SYSDATE, -1), 'MM')
  AND p.timestamp < TRUNC(SYSDATE, 'MM')
GROUP BY t.trainer_id, t.name;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY(NULL, NULL, 'BASIC +COST'));


COMMIT;


/*
====================================================================================================================================
 ZADATAK 4: IZVEŠTAJ KOJI KORISTI PL/SQL
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Procedura koja koristi RECORD, TABLE OF, BULK COLLECT, kompleksan upit (WITH + JOIN >=3 tabela + GROUP BY + HAVING),
         formatira kao JSON i upisuje u tabelu `REPORTS`.

    Procedura `GENERISI_MESECNI_IZVESTAJ_TRENERA` kreira mesečni izveštaj po trenerima (broj prisustava i prihod).
====================================================================================================================================
*/

-- Kreiramo tabelu REPORTS ako ne postoji
BEGIN
    EXECUTE IMMEDIATE 'CREATE TABLE reports (
        report_id NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY PRIMARY KEY,
        report_type VARCHAR2(100),
        content CLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by RAW(16)
    )';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -955 THEN -- ORA-00955: name is already used by an existing object
            NULL;
        END IF;
END;
/
CREATE OR REPLACE PROCEDURE GENERISI_MESECNI_IZVESTAJ_TRENERA(
    p_mesec IN NUMBER,
    p_godina IN NUMBER,
    p_kreator_id IN RAW
)
IS
    -- 1. Tipovi
    TYPE rec_trener_izv IS RECORD (
        trainer_id   trainers.trainer_id%TYPE,
        trainer_name trainers.name%TYPE,
        total_att    NUMBER,
        total_revenue NUMBER
    );
    TYPE tab_trener_izv IS TABLE OF rec_trener_izv;

    l_data tab_trener_izv;
    v_json CLOB := '{"izvestaj":"mesecni_treneri","mesec":' || p_mesec || ',"godina":' || p_godina || ',"stavke":[';

BEGIN
    -- 2. Kompleksan upit (WITH + JOIN >= 3 tabela)
    WITH class_att AS (
        SELECT c.class_id, c.trainer_id, COUNT(a.event_id) AS attend_count
        FROM classes c
        LEFT JOIN attendances a ON c.class_id = a.class_id
            AND EXTRACT(MONTH FROM a.timestamp) = p_mesec
            AND EXTRACT(YEAR FROM a.timestamp) = p_godina
        GROUP BY c.class_id, c.trainer_id
    ), class_pay AS (
        SELECT p.class_id, NVL(SUM(p.amount),0) AS revenue
        FROM payments p
        WHERE EXTRACT(MONTH FROM p.timestamp) = p_mesec
            AND EXTRACT(YEAR FROM p.timestamp) = p_godina
        GROUP BY p.class_id
    )
    SELECT t.trainer_id, t.name,
           NVL(SUM(ca.attend_count),0) AS total_att,
           NVL(SUM(cp.revenue),0) AS total_revenue
    BULK COLLECT INTO l_data
    FROM trainers t
    LEFT JOIN classes c ON t.trainer_id = c.trainer_id
    LEFT JOIN class_att ca ON c.class_id = ca.class_id
    LEFT JOIN class_pay cp ON c.class_id = cp.class_id
    GROUP BY t.trainer_id, t.name
    HAVING NVL(SUM(ca.attend_count),0) > 0
    ORDER BY NVL(SUM(cp.revenue),0) DESC;

    -- 3. Generisanje JSON izlaza
    FOR i IN 1..l_data.COUNT LOOP
        v_json := v_json || '{"trainer_id":"' || RAWTOHEX(l_data(i).trainer_id) || '",'
                  || '"trainer_name":"' || REPLACE(l_data(i).trainer_name, '"', '\"') || '",'
                  || '"total_att":' || l_data(i).total_att || ','
                  || '"total_revenue":' || l_data(i).total_revenue || '}';
        IF i < l_data.COUNT THEN
            v_json := v_json || ',';
        END IF;
    END LOOP;
    v_json := v_json || ']}';

    -- Lightweight pretty-print fallback (portable): insert newlines after commas between objects
    BEGIN
        BEGIN
            v_json := REPLACE(v_json, '},{', '},' || CHR(10) || '{');
            v_json := REPLACE(v_json, ',"', ',' || CHR(10) || '"');
            v_json := REPLACE(v_json, '[{', '[{' || CHR(10));
            v_json := REPLACE(v_json, '}]', CHR(10) || '}]');
        EXCEPTION
            WHEN OTHERS THEN
                NULL; -- on any failure keep compact JSON
        END;
    END;

    -- 4. Upis u tabelu reports
    INSERT INTO reports(report_type, content, created_by)
    VALUES ('mesecni_treneri', v_json, p_kreator_id);

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška prilikom generisanja izveštaja: ' || SQLERRM);
        ROLLBACK;
END;
/

-- Primer poziva procedure:
-- BEGIN
--   GENERISI_MESECNI_IZVESTAJ_TRENERA(EXTRACT(MONTH FROM SYSDATE), EXTRACT(YEAR FROM SYSDATE), SYS_GUID());
-- END;
/
COMMIT;
