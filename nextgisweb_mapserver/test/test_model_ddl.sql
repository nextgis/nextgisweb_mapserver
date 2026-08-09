/*** Table: mapserver_style ***/

CREATE TABLE mapserver_style (
    id integer NOT NULL,
    xml character varying NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (id) REFERENCES resource (id)
);

COMMENT ON TABLE mapserver_style IS 'mapserver';
