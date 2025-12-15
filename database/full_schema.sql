--
-- PostgreSQL database dump
--

\restrict pQg2L0zSVCHCVG66MNkansPKqIFZdlBhS4MeZFYhiqRx143v5q6N2ZMqyO5h55X

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: analytics_analytics; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA analytics_analytics;


--
-- Name: dbo; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA dbo;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dim_guests; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.dim_guests (
    profile_id bigint NOT NULL,
    first_name text,
    last_name text NOT NULL,
    email text,
    country text,
    is_vip integer NOT NULL,
    lifetime_spend numeric,
    total_stays integer NOT NULL,
    total_room_revenue numeric NOT NULL
);


--
-- Name: fct_booking_trends; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_booking_trends (
    stay_id bigint NOT NULL,
    arrival_date timestamp with time zone NOT NULL,
    total_revenue numeric
);


--
-- Name: fct_daily_business_performance; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_daily_business_performance (
    business_date date,
    room_revenue numeric NOT NULL,
    food_beverage_revenue numeric NOT NULL,
    spa_revenue numeric NOT NULL,
    golf_revenue numeric NOT NULL,
    total_daily_revenue numeric
);


--
-- Name: fct_daily_operations_forecast; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_daily_operations_forecast (
    forecast_date date,
    expected_arrivals integer NOT NULL,
    expected_guests integer NOT NULL,
    dining_reservations integer NOT NULL,
    dining_covers integer NOT NULL
);


--
-- Name: fct_dining_analytics; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_dining_analytics (
    restaurant_name text NOT NULL,
    total_reservations integer,
    avg_party_size integer,
    total_revenue numeric,
    cancellation_count integer
);


--
-- Name: fct_golf_analytics; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_golf_analytics (
    booking_id bigint NOT NULL,
    profile_id bigint NOT NULL,
    first_name text,
    last_name text,
    is_vip integer,
    course_name text,
    tee_time timestamp with time zone,
    players smallint,
    holes smallint,
    revenue numeric,
    day_of_week text,
    hour_of_day integer
);


--
-- Name: fct_recreation_analytics; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_recreation_analytics (
    booking_id bigint NOT NULL,
    profile_id bigint NOT NULL,
    first_name text,
    last_name text,
    is_vip integer,
    activity_type text NOT NULL,
    activity_name text,
    start_time timestamp with time zone,
    revenue numeric,
    day_of_week text,
    hour_of_day integer
);


--
-- Name: fct_spa_analytics; Type: TABLE; Schema: analytics_analytics; Owner: -
--

CREATE TABLE analytics_analytics.fct_spa_analytics (
    booking_id bigint NOT NULL,
    profile_id bigint NOT NULL,
    first_name text,
    last_name text,
    is_vip integer,
    treatment_name text,
    therapist_name text,
    spa_location text,
    start_time timestamp with time zone NOT NULL,
    revenue numeric,
    day_of_week text,
    hour_of_day integer
);


--
-- Name: courtbookings; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.courtbookings (
    cbid bigint NOT NULL,
    courtbookingsource text NOT NULL,
    courtbookingpropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    courtbookingconfid text NOT NULL,
    bookingtypeid text,
    bookingtypedescription text,
    bookingstatus text NOT NULL,
    startwhen timestamp with time zone NOT NULL,
    endwhen timestamp with time zone,
    courttypeid text,
    courttypedescription text,
    numberofplayers smallint,
    bookingsalesvalue numeric,
    playersalesvalue numeric,
    istbdplayer boolean,
    isnoshow boolean,
    ischeckedin boolean,
    onsite boolean,
    location text,
    courtname text,
    instructorid text,
    instructorname text,
    cancellationnumber text,
    cancellationfee numeric,
    profileid bigint NOT NULL
);


--
-- Name: lessonbookings; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.lessonbookings (
    lbid bigint NOT NULL,
    lessonbookingsource text NOT NULL,
    lessonbookingpropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    lessonbookingconfid text NOT NULL,
    startwhen timestamp with time zone,
    endwhen timestamp with time zone,
    lessontype text NOT NULL,
    instructorname text,
    lessondescription text,
    facilityname text,
    onsite boolean,
    location text,
    facilityinfo text,
    equipmentprovided text,
    bookingstatus text NOT NULL,
    ispaid boolean,
    lessonsalesvalue numeric,
    reservationid text,
    reservationstatus text,
    reservationsource text,
    cancellationnumber text,
    cancellationfee numeric,
    istbdplayer boolean,
    isnoshow boolean,
    ischeckedin boolean,
    profileid bigint NOT NULL,
    totalspent numeric
);


--
-- Name: otherreservations; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.otherreservations (
    orid bigint NOT NULL,
    profileid bigint NOT NULL,
    reservationsource text NOT NULL,
    reservationsourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    reservationid text NOT NULL,
    reservationconfid text,
    activityname text NOT NULL,
    activitydescription text,
    partysize integer,
    startwhen timestamp with time zone,
    facilityname text,
    onsite boolean NOT NULL,
    location text,
    totalspent numeric
);


--
-- Name: pmspreferences; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.pmspreferences (
    pmsprefid bigint NOT NULL,
    profileid bigint NOT NULL,
    pmssource text NOT NULL,
    pmssourcepropertycode text,
    pmssid bigint,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    preferencename text NOT NULL,
    preferencedescription text,
    preferencevalue text,
    details text
);


--
-- Name: pmsstayprofileassociations; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.pmsstayprofileassociations (
    pspaid bigint NOT NULL,
    pmsconfid text,
    masterprofileid bigint,
    associatedprofileid bigint,
    createdwhen timestamp with time zone NOT NULL
);


--
-- Name: pmsstays; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.pmsstays (
    pmssid bigint NOT NULL,
    profileid bigint NOT NULL,
    pmssource text NOT NULL,
    pmssourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    pmsstayid text NOT NULL,
    pmsconfid text,
    pmscrsid text,
    pmsfolioid text,
    firstname text,
    lastname text,
    arrivalwhen timestamp with time zone NOT NULL,
    departurewhen timestamp with time zone NOT NULL,
    staystatus text,
    roomnumber text,
    roomtype text,
    roomtypedescription text,
    roomdetail text,
    adults integer,
    arrivalratecode text,
    totalrevenue numeric,
    cancellationnumber text,
    childover integer,
    childunder integer,
    groupcode text,
    iscancelled boolean
);


--
-- Name: poolbeachamenityreservations; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.poolbeachamenityreservations (
    pbarid bigint NOT NULL,
    profileid bigint NOT NULL,
    pbasource text NOT NULL,
    pbasourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    pbatype text NOT NULL,
    poolbeachname text NOT NULL,
    pbanumber text,
    maxguests smallint,
    startwhen timestamp with time zone,
    completeswhen timestamp with time zone,
    cancellationnumber text,
    confid text,
    location text,
    pricequoted numeric
);


--
-- Name: preferences; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.preferences (
    prefid bigint NOT NULL,
    profileid bigint NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    preferencename text NOT NULL,
    preferencedescription text,
    preferencevalue text,
    details text,
    preferencesource text NOT NULL,
    preferencesourcepropertycode text,
    mergedfrom bigint
);


--
-- Name: profileassociationrelationships; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.profileassociationrelationships (
    parid bigint NOT NULL,
    relationa text,
    relationb text
);


--
-- Name: profileassociations; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.profileassociations (
    paid bigint NOT NULL,
    profile1id bigint NOT NULL,
    profile2id bigint NOT NULL,
    relation text NOT NULL,
    details text,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    assocsource text NOT NULL,
    assocsourcepropertycode text
);


--
-- Name: profilemonthlyspend; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.profilemonthlyspend (
    pmsid bigint NOT NULL,
    profileid bigint NOT NULL,
    month smallint NOT NULL,
    year integer NOT NULL,
    revenue numeric,
    revenuetype text
);


--
-- Name: profiles; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.profiles (
    pid bigint NOT NULL,
    publicguid uuid NOT NULL,
    publichashid numeric NOT NULL,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    isactive boolean NOT NULL,
    retentionrevoked boolean,
    mergedto bigint,
    profilesource text NOT NULL,
    profilesourcepropertycode text,
    pronouns text,
    salutation text,
    firstname text,
    lastname text NOT NULL,
    middlename text,
    nickname text,
    suffix text,
    birthdate timestamp with time zone,
    sosh text,
    gender text,
    primaryemail text,
    primaryphone text,
    businesstitle text,
    profession text,
    primarycategory text,
    comments text,
    primaryaddresstype text,
    primaryaddress1 text,
    primaryaddress2 text,
    primarycity text,
    primarystate text,
    primarypostalcode text,
    primarycountry text,
    vipstatus text,
    goldenrecord bigint,
    profiletype text,
    isanonymized boolean NOT NULL,
    anonymizedby text,
    anonymizeddate timestamp with time zone,
    anniversarydate timestamp with time zone,
    vipstatusdescription text,
    primaryphonetype text,
    primarystatecode text,
    primarycountrycode text,
    isvip boolean,
    primaryloyaltyid text,
    primaryloyaltylevel text,
    primaryloyaltyprogram text,
    primaryphonetechtype text,
    primaryphonecountrycode text,
    isplaceholder boolean NOT NULL,
    averagevisitsperyear double precision,
    averagespendpervisit numeric,
    averagedailyspend numeric,
    averageactivitiesperyear double precision,
    totalspent numeric
);


--
-- Name: profilevisitsperyear; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.profilevisitsperyear (
    pvpyid bigint NOT NULL,
    profileid bigint NOT NULL,
    visitcount integer
);


--
-- Name: removedprofilemergecandidates; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.removedprofilemergecandidates (
    rpmcid bigint NOT NULL,
    profileid bigint NOT NULL,
    removedmergecandidatepid bigint NOT NULL,
    removedwhen timestamp with time zone NOT NULL
);


--
-- Name: restaurantreservations; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.restaurantreservations (
    rrid bigint NOT NULL,
    profileid bigint NOT NULL,
    restaurantsource text NOT NULL,
    restaurantsourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    restaurantreservationid text NOT NULL,
    restaurantconfid text NOT NULL,
    reservationstatus text,
    onsite boolean NOT NULL,
    partysize integer NOT NULL,
    startwhen timestamp with time zone,
    specialoccasion text,
    customerdietaryrestrictions text,
    guestdietaryrestrictions text,
    restaurantname text NOT NULL,
    restaurantdetails text,
    cancellationnumber text,
    totalspent numeric,
    iscancelled boolean
);


--
-- Name: settings; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.settings (
    settingid bigint NOT NULL,
    settingname text NOT NULL,
    stringvalue text,
    bitvalue boolean,
    datetimevalue timestamp with time zone,
    intvalue integer,
    bigintvalue bigint,
    moneyvalue numeric,
    numericvalue numeric
);


--
-- Name: spabookings; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.spabookings (
    sbid bigint NOT NULL,
    profileid bigint NOT NULL,
    spasource text NOT NULL,
    spasourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    spabookingid text NOT NULL,
    spaconfid text,
    startwhen timestamp with time zone NOT NULL,
    endwhen timestamp with time zone NOT NULL,
    bookingstatus text,
    activitytype text,
    activityname text,
    activitydescription text,
    providername text,
    providergender text,
    facilityname text,
    price numeric,
    cancellationnumber text,
    cancellationfee numeric,
    spaname text,
    spaaddress1 text,
    spaaddress2 text,
    spacity text,
    spastate text,
    spapostalcode text,
    healthnotes text,
    reservationnotes text,
    appointmentnotes text,
    guestnotes text,
    cancellationpolicy text,
    providergenderpreference text,
    facilitygenderpreference text,
    mainguesttype text,
    wellnessformcompleted boolean,
    wellnessformexpired boolean,
    wellnessformsent boolean,
    firsttimeguest boolean,
    iscancelled boolean
);


--
-- Name: spapreferences; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.spapreferences (
    spaprefid bigint NOT NULL,
    profileid bigint NOT NULL,
    spasource text NOT NULL,
    spasourcepropertycode text NOT NULL,
    sbid bigint,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone,
    preferencename text NOT NULL,
    preferencedescription text,
    preferencevalue text,
    details text
);


--
-- Name: sysdiagrams; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.sysdiagrams (
    name text NOT NULL,
    principal_id integer NOT NULL,
    diagram_id bigint NOT NULL,
    version integer,
    definition bytea
);


--
-- Name: sysdiagrams_diagram_id_seq; Type: SEQUENCE; Schema: dbo; Owner: -
--

CREATE SEQUENCE dbo.sysdiagrams_diagram_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sysdiagrams_diagram_id_seq; Type: SEQUENCE OWNED BY; Schema: dbo; Owner: -
--

ALTER SEQUENCE dbo.sysdiagrams_diagram_id_seq OWNED BY dbo.sysdiagrams.diagram_id;


--
-- Name: teetimebookings; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.teetimebookings (
    ttbid bigint NOT NULL,
    profileid bigint NOT NULL,
    teetimesource text NOT NULL,
    teetimesourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    bookingtype text,
    isgroupbooking boolean,
    groupbookingid text,
    teetimeconfid text NOT NULL,
    bookingstatus text NOT NULL,
    coursename text,
    bookeddate timestamp with time zone,
    startinghole smallint,
    cancellationpolicytext text,
    cancellationdeadlinedatetime timestamp with time zone,
    bookingnotes text,
    disclaimer text,
    courseinformation text,
    numberofplayers smallint,
    bookingsalesvalue numeric,
    playersalesvalue numeric,
    istbdplayer boolean,
    numberofholes smallint,
    transportation text,
    caddy text,
    didnotplay boolean,
    ischeckedin boolean,
    iscancelled boolean
);


--
-- Name: transportationreservations; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.transportationreservations (
    reservationsource text NOT NULL,
    reservationsourcepropertycode text,
    versionstamp bytea NOT NULL,
    createdwhen timestamp with time zone NOT NULL,
    lastmodifiedwhen timestamp with time zone NOT NULL,
    reservationtype text NOT NULL,
    driver text,
    destination text,
    numberofguests integer,
    pickuplocation text,
    startwhen timestamp with time zone,
    profileid bigint NOT NULL,
    totalspent numeric
);


--
-- Name: vipcodes; Type: TABLE; Schema: dbo; Owner: -
--

CREATE TABLE dbo.vipcodes (
    vcid bigint NOT NULL,
    code text NOT NULL
);


--
-- Name: sysdiagrams diagram_id; Type: DEFAULT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.sysdiagrams ALTER COLUMN diagram_id SET DEFAULT nextval('dbo.sysdiagrams_diagram_id_seq'::regclass);


--
-- Name: courtbookings idx_18883_pk_courtbookings; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.courtbookings
    ADD CONSTRAINT idx_18883_pk_courtbookings PRIMARY KEY (cbid);


--
-- Name: lessonbookings idx_18897_pk_lessonbookings; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.lessonbookings
    ADD CONSTRAINT idx_18897_pk_lessonbookings PRIMARY KEY (lbid);


--
-- Name: otherreservations idx_18911_pk_otherreservations; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.otherreservations
    ADD CONSTRAINT idx_18911_pk_otherreservations PRIMARY KEY (orid);


--
-- Name: pmspreferences idx_18925_pk_pmspreferences; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.pmspreferences
    ADD CONSTRAINT idx_18925_pk_pmspreferences PRIMARY KEY (pmsprefid);


--
-- Name: pmsstays idx_18942_pk_pmsstays; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.pmsstays
    ADD CONSTRAINT idx_18942_pk_pmsstays PRIMARY KEY (pmssid);


--
-- Name: poolbeachamenityreservations idx_18955_pk_poolbeachamenityreservations; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.poolbeachamenityreservations
    ADD CONSTRAINT idx_18955_pk_poolbeachamenityreservations PRIMARY KEY (pbarid);


--
-- Name: preferences idx_18968_pk_preferences; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.preferences
    ADD CONSTRAINT idx_18968_pk_preferences PRIMARY KEY (prefid);


--
-- Name: profileassociations idx_18984_pk_profileassociations; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.profileassociations
    ADD CONSTRAINT idx_18984_pk_profileassociations PRIMARY KEY (paid);


--
-- Name: profiles idx_19004_pk_profiles; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.profiles
    ADD CONSTRAINT idx_19004_pk_profiles PRIMARY KEY (pid);


--
-- Name: removedprofilemergecandidates idx_19024_pk_removedprofilemergecandidates; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.removedprofilemergecandidates
    ADD CONSTRAINT idx_19024_pk_removedprofilemergecandidates PRIMARY KEY (rpmcid);


--
-- Name: restaurantreservations idx_19031_pk_restaurantreservations; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.restaurantreservations
    ADD CONSTRAINT idx_19031_pk_restaurantreservations PRIMARY KEY (rrid);


--
-- Name: settings idx_19047_pk_settings; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.settings
    ADD CONSTRAINT idx_19047_pk_settings PRIMARY KEY (settingid);


--
-- Name: spabookings idx_19054_pk_spabookings; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.spabookings
    ADD CONSTRAINT idx_19054_pk_spabookings PRIMARY KEY (sbid);


--
-- Name: spapreferences idx_19067_pk_spapreferences; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.spapreferences
    ADD CONSTRAINT idx_19067_pk_spapreferences PRIMARY KEY (spaprefid);


--
-- Name: sysdiagrams idx_19079_pk__sysdiagr__c2b05b61c5d6a409; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.sysdiagrams
    ADD CONSTRAINT idx_19079_pk__sysdiagr__c2b05b61c5d6a409 PRIMARY KEY (diagram_id);


--
-- Name: teetimebookings idx_19088_pk_teetimebookings; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.teetimebookings
    ADD CONSTRAINT idx_19088_pk_teetimebookings PRIMARY KEY (ttbid);


--
-- Name: vipcodes idx_19112_pk_vipcodes; Type: CONSTRAINT; Schema: dbo; Owner: -
--

ALTER TABLE ONLY dbo.vipcodes
    ADD CONSTRAINT idx_19112_pk_vipcodes PRIMARY KEY (vcid);


--
-- Name: idx_18821_analytics_analytics_dim_guests__dbt_tmp_cci; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18821_analytics_analytics_dim_guests__dbt_tmp_cci ON analytics_analytics.dim_guests USING btree (profile_id, first_name, last_name, email, country, is_vip, lifetime_spend, total_stays, total_room_revenue);


--
-- Name: idx_18831_analytics_analytics_fct_booking_trends__dbt_tmp_cci; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18831_analytics_analytics_fct_booking_trends__dbt_tmp_cci ON analytics_analytics.fct_booking_trends USING btree (stay_id, arrival_date, total_revenue);


--
-- Name: idx_18838_analytics_analytics_fct_daily_business_performance__d; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18838_analytics_analytics_fct_daily_business_performance__d ON analytics_analytics.fct_daily_business_performance USING btree (business_date, room_revenue, food_beverage_revenue, spa_revenue, golf_revenue, total_daily_revenue);


--
-- Name: idx_18847_analytics_analytics_fct_daily_operations_forecast__db; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18847_analytics_analytics_fct_daily_operations_forecast__db ON analytics_analytics.fct_daily_operations_forecast USING btree (forecast_date, expected_arrivals, expected_guests, dining_reservations, dining_covers);


--
-- Name: idx_18854_analytics_analytics_fct_dining_analytics__dbt_tmp_cci; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18854_analytics_analytics_fct_dining_analytics__dbt_tmp_cci ON analytics_analytics.fct_dining_analytics USING btree (restaurant_name, total_reservations, avg_party_size, total_revenue, cancellation_count);


--
-- Name: idx_18860_analytics_analytics_fct_golf_analytics__dbt_tmp_cci; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18860_analytics_analytics_fct_golf_analytics__dbt_tmp_cci ON analytics_analytics.fct_golf_analytics USING btree (booking_id, profile_id, first_name, last_name, is_vip, course_name, tee_time, players, holes, revenue, day_of_week, hour_of_day);


--
-- Name: idx_18867_analytics_analytics_fct_recreation_analytics__dbt_tmp; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18867_analytics_analytics_fct_recreation_analytics__dbt_tmp ON analytics_analytics.fct_recreation_analytics USING btree (booking_id, profile_id, first_name, last_name, is_vip, activity_type, activity_name, start_time, revenue, day_of_week, hour_of_day);


--
-- Name: idx_18875_analytics_analytics_fct_spa_analytics__dbt_tmp_cci; Type: INDEX; Schema: analytics_analytics; Owner: -
--

CREATE INDEX idx_18875_analytics_analytics_fct_spa_analytics__dbt_tmp_cci ON analytics_analytics.fct_spa_analytics USING btree (booking_id, profile_id, first_name, last_name, is_vip, treatment_name, therapist_name, spa_location, start_time, revenue, day_of_week, hour_of_day);


--
-- Name: idx_18925_ix_pmspreferences_pmssource; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18925_ix_pmspreferences_pmssource ON dbo.pmspreferences USING btree (pmssource);


--
-- Name: idx_18925_ix_pmspreferences_prefname; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18925_ix_pmspreferences_prefname ON dbo.pmspreferences USING btree (preferencename);


--
-- Name: idx_18925_ix_pmspreferences_profileid; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18925_ix_pmspreferences_profileid ON dbo.pmspreferences USING btree (profileid);


--
-- Name: idx_18968_ix_preferences_pofidandprefname; Type: INDEX; Schema: dbo; Owner: -
--

CREATE UNIQUE INDEX idx_18968_ix_preferences_pofidandprefname ON dbo.preferences USING btree (profileid, preferencename);


--
-- Name: idx_18968_ix_preferences_prefname; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18968_ix_preferences_prefname ON dbo.preferences USING btree (preferencename);


--
-- Name: idx_18968_ix_preferences_profileid; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18968_ix_preferences_profileid ON dbo.preferences USING btree (profileid);


--
-- Name: idx_18984_ix_profileassociations_prof1id; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18984_ix_profileassociations_prof1id ON dbo.profileassociations USING btree (profile1id);


--
-- Name: idx_18984_ix_profileassociations_prof2id; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18984_ix_profileassociations_prof2id ON dbo.profileassociations USING btree (profile2id);


--
-- Name: idx_18984_ix_profileassociations_relation; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_18984_ix_profileassociations_relation ON dbo.profileassociations USING btree (relation);


--
-- Name: idx_19004_ix_profiles_createdwhen; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19004_ix_profiles_createdwhen ON dbo.profiles USING btree (createdwhen);


--
-- Name: idx_19004_ix_profiles_isactive; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19004_ix_profiles_isactive ON dbo.profiles USING btree (isactive);


--
-- Name: idx_19004_ix_profiles_lastname; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19004_ix_profiles_lastname ON dbo.profiles USING btree (lastname);


--
-- Name: idx_19004_ix_profiles_mergedto; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19004_ix_profiles_mergedto ON dbo.profiles USING btree (mergedto);


--
-- Name: idx_19004_ix_profiles_profilesource; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19004_ix_profiles_profilesource ON dbo.profiles USING btree (profilesource);


--
-- Name: idx_19004_ix_profiles_profilesrcpropcode; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19004_ix_profiles_profilesrcpropcode ON dbo.profiles USING btree (profilesourcepropertycode);


--
-- Name: idx_19004_ix_profiles_pubguid; Type: INDEX; Schema: dbo; Owner: -
--

CREATE UNIQUE INDEX idx_19004_ix_profiles_pubguid ON dbo.profiles USING btree (publicguid);


--
-- Name: idx_19004_ix_profiles_pubhashid; Type: INDEX; Schema: dbo; Owner: -
--

CREATE UNIQUE INDEX idx_19004_ix_profiles_pubhashid ON dbo.profiles USING btree (publichashid);


--
-- Name: idx_19067_ix_spapreferences_prefname; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19067_ix_spapreferences_prefname ON dbo.spapreferences USING btree (preferencename);


--
-- Name: idx_19067_ix_spapreferences_profileid; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19067_ix_spapreferences_profileid ON dbo.spapreferences USING btree (profileid);


--
-- Name: idx_19067_ix_spapreferences_sbid; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19067_ix_spapreferences_sbid ON dbo.spapreferences USING btree (sbid);


--
-- Name: idx_19067_ix_spapreferences_spapropcode; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19067_ix_spapreferences_spapropcode ON dbo.spapreferences USING btree (spasourcepropertycode);


--
-- Name: idx_19067_ix_spapreferences_spasource; Type: INDEX; Schema: dbo; Owner: -
--

CREATE INDEX idx_19067_ix_spapreferences_spasource ON dbo.spapreferences USING btree (spasource);


--
-- Name: idx_19079_uk_principal_name; Type: INDEX; Schema: dbo; Owner: -
--

CREATE UNIQUE INDEX idx_19079_uk_principal_name ON dbo.sysdiagrams USING btree (principal_id, name);


--
-- PostgreSQL database dump complete
--

\unrestrict pQg2L0zSVCHCVG66MNkansPKqIFZdlBhS4MeZFYhiqRx143v5q6N2ZMqyO5h55X

