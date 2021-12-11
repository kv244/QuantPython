-- PROCEDURE: public.insert_collection(integer, date, date, time with time zone, character varying, character varying, numeric, numeric, numeric)

-- DROP PROCEDURE IF EXISTS public.insert_collection(integer, date, date, time with time zone, character varying, character varying, numeric, numeric, numeric);

CREATE OR REPLACE PROCEDURE public.insert_collection(
	IN instrument_ref integer,
	IN datep date,
	IN updated date,
	IN updated_time time with time zone,
	IN instrument_name character varying,
	IN signal character varying,
	IN openp numeric,
	IN closep numeric,
	IN signal_benchmark numeric)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
--IF NOT EXISTS(SELECT * FROM public."Collection" WHERE "Collection"."date" = datep) THEN
INSERT INTO public."Collection"(
    instrument_ref, "date", updated, updated_time, instrument_name, signal, "open", "close", signal_benchmark)
	VALUES ( instrument_ref, datep, updated, updated_time, instrument_name, signal, openp, closep, signal_benchmark);
    COMMIT;
--ELSE
--	RAISE INFO 'Datep exists';
--END IF;
-- replacing with unique constraint for now
END;
$BODY$;
