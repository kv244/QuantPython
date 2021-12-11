-- PROCEDURE: public.determine_performance(character varying, date, refcursor)

-- DROP PROCEDURE IF EXISTS public.determine_performance(character varying, date, refcursor);

CREATE OR REPLACE PROCEDURE public.determine_performance(
	IN instrument_n character varying,
	IN date_triggered date,
	INOUT cresults refcursor)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
 cresults:= 'cur';
	OPEN cresults for select signal_benchmark, signal from public."Collection"
    	where updated = date_triggered
	    and instrument_name = instrument_n;
END;
$BODY$;
