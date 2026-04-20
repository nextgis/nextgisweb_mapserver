/*** {
    "revision": "5289adc0", "parents": ["00000000"],
    "date": "2026-04-14T17:33:44",
    "message": "Add render postprocess settings"
} ***/

ALTER TABLE mapserver_style ADD COLUMN postprocess jsonb;
