DROP TABLE feito_valoracion CASCADE CONSTRAINTS;
DROP TABLE ponte_hospedaxe_commodidade CASCADE CONSTRAINTS;
DROP TABLE ponte_hospedaxe_accesibilidade CASCADE CONSTRAINTS;
DROP TABLE dim_eventos CASCADE CONSTRAINTS;
DROP TABLE dim_hospedaxe CASCADE CONSTRAINTS;
DROP TABLE dim_valorador CASCADE CONSTRAINTS;
DROP TABLE dim_hospedador CASCADE CONSTRAINTS;
DROP TABLE dim_lugar CASCADE CONSTRAINTS;
DROP TABLE dim_tempo CASCADE CONSTRAINTS;
DROP TABLE ponte_evento_valoracion CASCADE CONSTRAINTS;


-- ---------------------------
-- DIM_TIEMPO
-- ---------------------------
CREATE TABLE dim_tempo (
    DATE_KEY  DATE PRIMARY KEY,
    DAY NUMBER NOT NULL,
    MONTH NUMBER NOT NULL,
    YEAR NUMBER NOT NULL,
    SEASSON VARCHAR2(10) NOT NULL,
    HIGH_SEASSON NUMBER(1) NOT NULL
);

-- ---------------------------
-- DIM_LUGAR
-- ---------------------------
CREATE TABLE dim_lugar (
    PLACE_ID VARCHAR2(400) PRIMARY KEY,
    STREET VARCHAR2(100) NOT NULL,
    CITY VARCHAR2(100) NOT NULL,
    COUNTRY VARCHAR2(100) NOT NULL,
    CONSTRAINT uk_lugar UNIQUE (STREET, CITY, COUNTRY)
);

-- ---------------------------
-- DIM_HOSPEDAXE
-- ---------------------------
CREATE TABLE dim_hospedaxe (
    HOSTING_ID NUMBER PRIMARY KEY,
    PRICE_NIGHT NUMBER(10,2) NOT NULL,
    PROPERTY_TYPE VARCHAR2(50) NOT NULL
);

-- ---------------------------
-- DIM_EVENTOS
-- ---------------------------
CREATE TABLE dim_eventos (
    EVENT_ID   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    EVENT_NAME VARCHAR2(200) NOT NULL,
    EVENT_TYPE VARCHAR2(50)  NOT NULL,
    IMPACT     VARCHAR2(20)  NOT NULL,
    PLACE_ID   VARCHAR2(400) NOT NULL,
    EVENT_DATE DATE NOT NULL,

    CONSTRAINT CHK_IMPACT CHECK (IMPACT IN ('Low', 'Medium', 'High')),
    CONSTRAINT UK_EVENT UNIQUE (EVENT_NAME, PLACE_ID, EVENT_DATE),

    CONSTRAINT FK_EVENT_PLACE FOREIGN KEY (PLACE_ID)
        REFERENCES dim_lugar(PLACE_ID),

    CONSTRAINT FK_EVENT_DATE FOREIGN KEY (EVENT_DATE)
        REFERENCES dim_tempo(DATE_KEY)
);

-- ---------------------------
-- DIM_VALORADOR_SCD2
-- ---------------------------
CREATE TABLE dim_valorador (
    REVIEWER_KEY NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Chave surrogada
    REVIEWER_ID NUMBER NOT NULL, -- ID do OLTP
    AGE NUMBER NOT NULL,
    SEX CHAR(1) DEFAULT 'D' NOT NULL, -- H=Home, M=Muller, D=Descoñecido O=Outro
    BIRTH_DATE DATE NOT NULL,
    DATE_START_VALID DATE NOT NULL,
    DATE_STOPPED_VALID DATE,
    ACTUAL NUMBER(1) DEFAULT 1 NOT NULL, -- 1=TRUE, 0=FALSE
    CONSTRAINT CHK_SEX CHECK (SEX IN ('H','M','D','O'))
);


-- ---------------------------
-- DIM_HOSPEDADOR
-- ---------------------------
CREATE TABLE dim_hospedador (
    HOST_KEY NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Chave surrogada
    HOST_ID NUMBER NOT NULL, -- ID do OLTP
    RESPONSE_TIME VARCHAR2(50) NOT NULL,
    AVG_SCORE NUMBER(3,2),
    TOTAL_HOSTINGS NUMBER NOT NULL,
    SUPERHOST NUMBER(1) DEFAULT 0 NOT NULL, -- 1=TRUE, 0=FALSE
    DATE_START_VALID DATE NOT NULL,
    DATE_STOPPED_VALID DATE,
    ACTUAL NUMBER(1) DEFAULT 1 NOT NULL -- 1=TRUE, 0=FALSE
);

-- ---------------------------
-- ponte_hospedaxe_commodidade
-- ---------------------------
CREATE TABLE ponte_hospedaxe_commodidade (
    HOSTING_ID NUMBER NOT NULL,
    COMMODITY VARCHAR2(500) NOT NULL,
    WEIGHT NUMBER(10,2) NOT NULL, 
    PRIMARY KEY (HOSTING_ID, COMMODITY),
    FOREIGN KEY (HOSTING_ID) REFERENCES dim_hospedaxe(HOSTING_ID)
);

-- ---------------------------
-- ponte_hospedaxe_accesibilidade
-- ---------------------------
CREATE TABLE ponte_hospedaxe_accesibilidade (
    HOSTING_ID NUMBER NOT NULL,
    ACCESSIBILITY VARCHAR2(50) NOT NULL,
    WEIGHT NUMBER(10,2) NOT NULL, 
    PRIMARY KEY (HOSTING_ID, ACCESSIBILITY),
    FOREIGN KEY (HOSTING_ID) REFERENCES dim_hospedaxe(HOSTING_ID)
);

-- ---------------------------
-- feito_valoracion
-- ---------------------------
CREATE TABLE feito_valoracion (
    REVIEW_ID        NUMBER PRIMARY KEY,     -- Desde OLTP
    HOSTING_ID       NUMBER NOT NULL,
    REVIEWER_ID      NUMBER NOT NULL,
    REVIEW_DATE      DATE NOT NULL,
    REVIEWER_KEY     NUMBER NOT NULL,        -- Chave surrogada (SCD Tipo 2)
    SCORE            NUMBER(3,2) NOT NULL,
    RAIN_MM          NUMBER(5,2) DEFAULT 0 NOT NULL, -- Dimensión dexenerada

    -- Chaves Foráneas
    FOREIGN KEY (HOSTING_ID)
        REFERENCES dim_hospedaxe(HOSTING_ID),

    FOREIGN KEY (REVIEW_DATE)
        REFERENCES dim_tempo(DATE_KEY),

    FOREIGN KEY (REVIEWER_KEY)
        REFERENCES dim_valorador(REVIEWER_KEY)
);

-- ---------------------------
-- ponte_evento_valoracion
-- ---------------------------
CREATE TABLE ponte_evento_valoracion (
    EVENT_ID NUMBER NOT NULL,
    REVIEW_ID NUMBER NOT NULL,
    IMPACT VARCHAR2(20)  NOT NULL,
    WEIGHT NUMBER(10,2) NOT NULL, 


    PRIMARY KEY (EVENT_ID, REVIEW_ID),
    FOREIGN KEY (EVENT_ID) REFERENCES dim_eventos(EVENT_ID),
    FOREIGN KEY (REVIEW_ID) REFERENCES feito_valoracion(REVIEW_ID)
);


-- ---------------------------
-- INDEX
-- ---------------------------
CREATE INDEX IDX_EVENT_DATE_CITY ON dim_eventos(EVENT_DATE, PLACE_ID);

-- ---------------------------
-- SELECTS
-- ---------------------------
SELECT * FROM dim_tempo;
SELECT * FROM dim_lugar;
SELECT * FROM dim_hospedaxe;
SELECT * FROM dim_eventos;
SELECT * FROM dim_valorador;
SELECT * FROM dim_hospedador;
SELECT * FROM ponte_hospedaxe_commodidade;
SELECT * FROM ponte_hospedaxe_accesibilidade;
SELECT * FROM feito_valoracion;
SELECT * FROM ponte_evento_valoracion;


