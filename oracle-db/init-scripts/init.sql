
-- Drop tables if they exist (in correct order due to foreign keys)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE payments CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE attendances CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE classes CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE trainers CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE rooms CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

-- ============================================
-- 1. ROOMS (Prostorije)
-- ============================================
CREATE TABLE rooms (
    room_id         RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    name            VARCHAR2(100) NOT NULL,
    location        VARCHAR2(200),
    capacity        NUMBER(10) NOT NULL,
    has_equipment   NUMBER(1) DEFAULT 0 CHECK (has_equipment IN (0, 1)),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT rooms_capacity_positive CHECK (capacity > 0)
);

-- ============================================
-- 2. TRAINERS (Treneri)
-- ============================================
CREATE TABLE trainers (
    trainer_id      RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    name            VARCHAR2(100) NOT NULL,
    specialization  VARCHAR2(100),
    email           VARCHAR2(100),
    phone           VARCHAR2(20),
    rating          NUMBER(3, 2),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT trainers_rating_range CHECK (rating >= 0 AND rating <= 5)
);

-- ============================================
-- 3. CLASSES (Grupni časovi)
-- ============================================
CREATE TABLE classes (
    class_id        RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    name            VARCHAR2(100) NOT NULL,
    trainer_id      RAW(16),
    room_id         RAW(16),
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP NOT NULL,
    capacity        NUMBER(10),
    price           NUMBER(10, 2),
    description     VARCHAR2(500),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_classes_trainer FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id),
    CONSTRAINT fk_classes_room FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    CONSTRAINT classes_time_valid CHECK (end_time > start_time),
    CONSTRAINT classes_capacity_positive CHECK (capacity > 0),
    CONSTRAINT classes_price_positive CHECK (price >= 0)
);

-- ============================================
-- 4. ATTENDANCES (Evidencija prisustva)
-- ============================================
CREATE TABLE attendances (
    event_id        RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    class_id        RAW(16) NOT NULL,
    member_id       RAW(16) NOT NULL,
    timestamp       TIMESTAMP NOT NULL,
    status          VARCHAR2(20) NOT NULL,
    CONSTRAINT fk_attendances_class FOREIGN KEY (class_id) REFERENCES classes(class_id),
    CONSTRAINT attendances_status_valid CHECK (status IN ('checked-in', 'checked-out', 'cancelled'))
);

-- ============================================
-- 5. PAYMENTS (Plaćanja)
-- ============================================
CREATE TABLE payments (
    payment_id      RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    member_id       RAW(16) NOT NULL,
    class_id        RAW(16) NOT NULL,
    amount          NUMBER(10, 2) NOT NULL,
    timestamp       TIMESTAMP NOT NULL,
    CONSTRAINT fk_payments_class FOREIGN KEY (class_id) REFERENCES classes(class_id),
    CONSTRAINT payments_amount_positive CHECK (amount >= 0)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Rooms indexes
CREATE INDEX idx_rooms_capacity ON rooms(capacity);

-- Trainers indexes
CREATE INDEX idx_trainers_specialization ON trainers(specialization);
CREATE INDEX idx_trainers_rating ON trainers(rating);

-- Classes indexes
CREATE INDEX idx_classes_trainer ON classes(trainer_id);
CREATE INDEX idx_classes_room ON classes(room_id);
CREATE INDEX idx_classes_start_time ON classes(start_time);

-- Attendances indexes
CREATE INDEX idx_attendances_class ON attendances(class_id);
CREATE INDEX idx_attendances_member ON attendances(member_id);
CREATE INDEX idx_attendances_timestamp ON attendances(timestamp);

-- Payments indexes
CREATE INDEX idx_payments_member ON payments(member_id);
CREATE INDEX idx_payments_class ON payments(class_id);
CREATE INDEX idx_payments_timestamp ON payments(timestamp);

COMMIT;
