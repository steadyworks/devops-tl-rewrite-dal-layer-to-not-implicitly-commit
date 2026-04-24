--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.5 (Homebrew)

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
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    asset_key_original text NOT NULL,
    asset_key_display text NOT NULL,
    asset_key_llm text NOT NULL,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'queued'::text NOT NULL,
    input_payload jsonb,
    result_payload jsonb,
    error_message text,
    user_id uuid,
    photobook_id uuid,
    created_at timestamp without time zone DEFAULT now(),
    started_at timestamp without time zone,
    completed_at timestamp without time zone
);


--
-- Name: pages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    photobook_id uuid,
    page_number integer NOT NULL,
    user_message text,
    layout text,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: pages_assets_rel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pages_assets_rel (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    page_id uuid,
    asset_id uuid,
    order_index integer,
    caption text
);


--
-- Name: photobooks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.photobooks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    title text NOT NULL,
    caption text,
    theme text,
    status text DEFAULT 'draft'::text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assets (id, user_id, asset_key_original, asset_key_display, asset_key_llm, metadata, created_at) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (id, job_type, status, input_payload, result_payload, error_message, user_id, photobook_id, created_at, started_at, completed_at) FROM stdin;
\.


--
-- Data for Name: pages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pages (id, photobook_id, page_number, user_message, layout, created_at) FROM stdin;
\.


--
-- Data for Name: pages_assets_rel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pages_assets_rel (id, page_id, asset_id, order_index, caption) FROM stdin;
\.


--
-- Data for Name: photobooks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.photobooks (id, user_id, title, caption, theme, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schema_migrations (version) FROM stdin;
20250703021505
20250703025351
\.


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: pages_assets_rel pages_assets_rel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages_assets_rel
    ADD CONSTRAINT pages_assets_rel_pkey PRIMARY KEY (id);


--
-- Name: pages pages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages
    ADD CONSTRAINT pages_pkey PRIMARY KEY (id);


--
-- Name: photobooks photobooks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photobooks
    ADD CONSTRAINT photobooks_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: pages_assets_rel pages_assets_rel_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pages_assets_rel
    ADD CONSTRAINT pages_assets_rel_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id);


--
-- PostgreSQL database dump complete
--

