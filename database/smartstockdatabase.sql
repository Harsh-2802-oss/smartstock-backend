--
-- PostgreSQL database dump
--

\restrict IKehCGCb8jQYrH7iS72LPvZwLuT2WI5VGluaeHqO8KE2L9cE64hrOJDGVmRyMdr

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-09-26 20:29:33

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 16403)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    store_id integer NOT NULL,
    category_name character varying(100) NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16402)
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_category_id_seq OWNER TO postgres;

--
-- TOC entry 5088 (class 0 OID 0)
-- Dependencies: 221
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- TOC entry 226 (class 1259 OID 16435)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    store_id integer NOT NULL,
    category_id integer,
    supplier_id integer,
    sku character varying(50) NOT NULL,
    product_name character varying(150) NOT NULL,
    selling_price numeric(10,2) NOT NULL,
    cost_price numeric(10,2) NOT NULL,
    current_stock integer DEFAULT 0 NOT NULL,
    reorder_threshold integer DEFAULT 5 NOT NULL
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16434)
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_product_id_seq OWNER TO postgres;

--
-- TOC entry 5089 (class 0 OID 0)
-- Dependencies: 225
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- TOC entry 230 (class 1259 OID 16484)
-- Name: sale_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale_items (
    sale_item_id integer NOT NULL,
    sale_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    unit_cost numeric(10,2) NOT NULL
);


ALTER TABLE public.sale_items OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16483)
-- Name: sale_items_sale_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sale_items_sale_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sale_items_sale_item_id_seq OWNER TO postgres;

--
-- TOC entry 5090 (class 0 OID 0)
-- Dependencies: 229
-- Name: sale_items_sale_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sale_items_sale_item_id_seq OWNED BY public.sale_items.sale_item_id;


--
-- TOC entry 228 (class 1259 OID 16467)
-- Name: sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales (
    sale_id integer NOT NULL,
    store_id integer NOT NULL,
    sale_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    total_revenue numeric(10,2) NOT NULL,
    total_profit numeric(10,2) NOT NULL
);


ALTER TABLE public.sales OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16466)
-- Name: sales_sale_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sales_sale_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_sale_id_seq OWNER TO postgres;

--
-- TOC entry 5091 (class 0 OID 0)
-- Dependencies: 227
-- Name: sales_sale_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sales_sale_id_seq OWNED BY public.sales.sale_id;


--
-- TOC entry 232 (class 1259 OID 16507)
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_movements (
    movement_id integer NOT NULL,
    product_id integer NOT NULL,
    movement_type character varying(20) NOT NULL,
    quantity integer NOT NULL,
    movement_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text
);


ALTER TABLE public.stock_movements OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16506)
-- Name: stock_movements_movement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_movements_movement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_movements_movement_id_seq OWNER TO postgres;

--
-- TOC entry 5092 (class 0 OID 0)
-- Dependencies: 231
-- Name: stock_movements_movement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_movements_movement_id_seq OWNED BY public.stock_movements.movement_id;


--
-- TOC entry 220 (class 1259 OID 16390)
-- Name: stores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stores (
    store_id integer NOT NULL,
    store_name character varying(100) NOT NULL,
    email character varying(100),
    phone character varying(20),
    address text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.stores OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16389)
-- Name: stores_store_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stores_store_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stores_store_id_seq OWNER TO postgres;

--
-- TOC entry 5093 (class 0 OID 0)
-- Dependencies: 219
-- Name: stores_store_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stores_store_id_seq OWNED BY public.stores.store_id;


--
-- TOC entry 224 (class 1259 OID 16418)
-- Name: suppliers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suppliers (
    supplier_id integer NOT NULL,
    store_id integer NOT NULL,
    supplier_name character varying(100) NOT NULL,
    category character varying(100),
    phone character varying(20),
    email character varying(100),
    total_orders integer DEFAULT 0
);


ALTER TABLE public.suppliers OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16417)
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suppliers_supplier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suppliers_supplier_id_seq OWNER TO postgres;

--
-- TOC entry 5094 (class 0 OID 0)
-- Dependencies: 223
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suppliers_supplier_id_seq OWNED BY public.suppliers.supplier_id;


--
-- TOC entry 4888 (class 2604 OID 16406)
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- TOC entry 4891 (class 2604 OID 16438)
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- TOC entry 4896 (class 2604 OID 16487)
-- Name: sale_items sale_item_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_items ALTER COLUMN sale_item_id SET DEFAULT nextval('public.sale_items_sale_item_id_seq'::regclass);


--
-- TOC entry 4894 (class 2604 OID 16470)
-- Name: sales sale_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales ALTER COLUMN sale_id SET DEFAULT nextval('public.sales_sale_id_seq'::regclass);


--
-- TOC entry 4897 (class 2604 OID 16510)
-- Name: stock_movements movement_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements ALTER COLUMN movement_id SET DEFAULT nextval('public.stock_movements_movement_id_seq'::regclass);


--
-- TOC entry 4886 (class 2604 OID 16393)
-- Name: stores store_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stores ALTER COLUMN store_id SET DEFAULT nextval('public.stores_store_id_seq'::regclass);


--
-- TOC entry 4889 (class 2604 OID 16421)
-- Name: suppliers supplier_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN supplier_id SET DEFAULT nextval('public.suppliers_supplier_id_seq'::regclass);


--
-- TOC entry 5072 (class 0 OID 16403)
-- Dependencies: 222
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (category_id, store_id, category_name) FROM stdin;
1	1	Groceries
2	1	Dairy
3	1	Snacks
4	1	Beverages
5	1	Personal Care
\.


--
-- TOC entry 5076 (class 0 OID 16435)
-- Dependencies: 226
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (product_id, store_id, category_id, supplier_id, sku, product_name, selling_price, cost_price, current_stock, reorder_threshold) FROM stdin;
6	1	1	\N	GRO-001	Basmati Rice 5kg	450.00	380.00	30	10
7	1	2	\N	DAI-001	Amul Milk 1L	60.00	50.00	50	15
8	1	3	\N	SNK-001	Lays Classic 90g	20.00	15.00	100	20
9	1	4	\N	BEV-001	Coca-Cola 750ml	40.00	30.00	60	15
10	1	5	\N	PC-001	Colgate Toothpaste 200g	95.00	75.00	40	10
\.


--
-- TOC entry 5080 (class 0 OID 16484)
-- Dependencies: 230
-- Data for Name: sale_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sale_items (sale_item_id, sale_id, product_id, quantity, unit_price, unit_cost) FROM stdin;
\.


--
-- TOC entry 5078 (class 0 OID 16467)
-- Dependencies: 228
-- Data for Name: sales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales (sale_id, store_id, sale_time, total_revenue, total_profit) FROM stdin;
\.


--
-- TOC entry 5082 (class 0 OID 16507)
-- Dependencies: 232
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_movements (movement_id, product_id, movement_type, quantity, movement_time, notes) FROM stdin;
\.


--
-- TOC entry 5070 (class 0 OID 16390)
-- Dependencies: 220
-- Data for Name: stores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stores (store_id, store_name, email, phone, address, created_at) FROM stdin;
1	SmartStock Demo Store	admin@smartstock.com	+91 98765 43210	Chennai, Tamil Nadu	2026-09-26 18:19:38.72623
\.


--
-- TOC entry 5074 (class 0 OID 16418)
-- Dependencies: 224
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suppliers (supplier_id, store_id, supplier_name, category, phone, email, total_orders) FROM stdin;
2	1	Chennai Wholesale Traders	Groceries	+91 98765 11111	contact@chennaiwholesale.com	12
3	1	FreshDairy Distributors	Dairy	+91 98765 22222	sales@freshdairy.com	8
\.


--
-- TOC entry 5095 (class 0 OID 0)
-- Dependencies: 221
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 6, true);


--
-- TOC entry 5096 (class 0 OID 0)
-- Dependencies: 225
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_product_id_seq', 10, true);


--
-- TOC entry 5097 (class 0 OID 0)
-- Dependencies: 229
-- Name: sale_items_sale_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sale_items_sale_item_id_seq', 1, true);


--
-- TOC entry 5098 (class 0 OID 0)
-- Dependencies: 227
-- Name: sales_sale_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_sale_id_seq', 2, true);


--
-- TOC entry 5099 (class 0 OID 0)
-- Dependencies: 231
-- Name: stock_movements_movement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_movements_movement_id_seq', 1, true);


--
-- TOC entry 5100 (class 0 OID 0)
-- Dependencies: 219
-- Name: stores_store_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stores_store_id_seq', 1, true);


--
-- TOC entry 5101 (class 0 OID 0)
-- Dependencies: 223
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suppliers_supplier_id_seq', 3, true);


--
-- TOC entry 4902 (class 2606 OID 16411)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- TOC entry 4906 (class 2606 OID 16450)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- TOC entry 4910 (class 2606 OID 16495)
-- Name: sale_items sale_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_pkey PRIMARY KEY (sale_item_id);


--
-- TOC entry 4908 (class 2606 OID 16477)
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (sale_id);


--
-- TOC entry 4912 (class 2606 OID 16519)
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (movement_id);


--
-- TOC entry 4900 (class 2606 OID 16400)
-- Name: stores stores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stores
    ADD CONSTRAINT stores_pkey PRIMARY KEY (store_id);


--
-- TOC entry 4904 (class 2606 OID 16427)
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id);


--
-- TOC entry 4913 (class 2606 OID 16412)
-- Name: categories fk_category_store; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT fk_category_store FOREIGN KEY (store_id) REFERENCES public.stores(store_id);


--
-- TOC entry 4915 (class 2606 OID 16456)
-- Name: products fk_product_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES public.categories(category_id);


--
-- TOC entry 4916 (class 2606 OID 16451)
-- Name: products fk_product_store; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_product_store FOREIGN KEY (store_id) REFERENCES public.stores(store_id);


--
-- TOC entry 4917 (class 2606 OID 16461)
-- Name: products fk_product_supplier; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_product_supplier FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id);


--
-- TOC entry 4919 (class 2606 OID 16501)
-- Name: sale_items fk_sale_item_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT fk_sale_item_product FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- TOC entry 4920 (class 2606 OID 16496)
-- Name: sale_items fk_sale_item_sale; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT fk_sale_item_sale FOREIGN KEY (sale_id) REFERENCES public.sales(sale_id);


--
-- TOC entry 4918 (class 2606 OID 16478)
-- Name: sales fk_sale_store; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT fk_sale_store FOREIGN KEY (store_id) REFERENCES public.stores(store_id);


--
-- TOC entry 4921 (class 2606 OID 16520)
-- Name: stock_movements fk_stock_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT fk_stock_product FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- TOC entry 4914 (class 2606 OID 16428)
-- Name: suppliers fk_supplier_store; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT fk_supplier_store FOREIGN KEY (store_id) REFERENCES public.stores(store_id);


-- Completed on 2026-09-26 20:29:34

--
-- PostgreSQL database dump complete
--

\unrestrict IKehCGCb8jQYrH7iS72LPvZwLuT2WI5VGluaeHqO8KE2L9cE64hrOJDGVmRyMdr

