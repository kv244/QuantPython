-- Table: public.Collection

-- DROP TABLE IF EXISTS public."Collection";

CREATE TABLE IF NOT EXISTS public."Collection"
(
    pky integer NOT NULL DEFAULT nextval('"Collection_pky_seq"'::regclass),
    instrument_ref integer,
    date date,
    updated date,
    updated_time time with time zone,
    instrument_name character varying(10) COLLATE pg_catalog."default",
    signal character varying(5) COLLATE pg_catalog."default",
    open numeric,
    close numeric,
    signal_benchmark numeric,
    CONSTRAINT "Collection_pkey" PRIMARY KEY (pky),
    CONSTRAINT "UniqueDateInstrument" UNIQUE (date, instrument_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Collection"
    OWNER to postgres;