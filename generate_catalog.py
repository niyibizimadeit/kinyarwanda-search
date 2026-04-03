"""
Kinyarwanda-English Bilingual Product Catalog Generator
========================================================
Generates three datasets for the kinyarwanda-search project:
  1. products.json   — 300 bilingual product listings
  2. queries.json    — 300 mixed-language search queries
  3. lexicon.json    — Kinyarwanda e-commerce vocabulary lexicon

Author : NIYIBIZI Prince
Project: kinyarwanda-search
Usage  : python generate_catalog.py
Output : saves all three files to data/raw/
"""

import json
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. KINYARWANDA VOCABULARY LEXICON
#    This is a standalone publishable asset — the first documented
#    Kinyarwanda e-commerce vocabulary list.
# ---------------------------------------------------------------------------

LEXICON = {
    # General commerce
    "product":       {"rw": "igicuruzwa",          "example": "ibicuruzwa byiza"},
    "price":         {"rw": "igiciro",              "example": "igiciro ni kangahe"},
    "buy":           {"rw": "kugura",               "example": "ndashaka kugura"},
    "sell":          {"rw": "kugurisha",            "example": "bagurisha hano"},
    "order":         {"rw": "gutumiza",             "example": "ndashaka gutumiza"},
    "delivery":      {"rw": "gutanga",              "example": "gutanga mu rugo"},
    "I want":        {"rw": "ndashaka",             "example": "ndashaka telefoni nziza"},
    "good/nice":     {"rw": "nziza",                "example": "ibicuruzwa nziza"},
    "cheap":         {"rw": "gito",                 "example": "igiciro gito"},
    "expensive":     {"rw": "birahenze",            "example": "birahenze cyane"},
    "discount":      {"rw": "igabanywa ry'igiciro", "example": "igabanywa ry'igiciro"},
    "new":           {"rw": "gishya",               "example": "igicuruzwa gishya"},
    "quality":       {"rw": "ubwiza",               "example": "ubwiza bwiza"},
    "money":         {"rw": "amafaranga",           "example": "nitanga amafaranga"},
    "stock":         {"rw": "ibisigaye",            "example": "ibisigaye biri hehe"},
    "size":          {"rw": "ingano",               "example": "ingano ingahe"},
    "color":         {"rw": "ibara",                "example": "ibara ryiza"},
    "small":         {"rw": "gito",                 "example": "igicuruzwa gito"},
    "big":           {"rw": "kinini",               "example": "igicuruzwa kinini"},
    "how much":      {"rw": "ni kangahe",           "example": "ni kangahe igiciro"},
    # Electronics & accessories
    "phone":         {"rw": "telefoni",             "example": "telefoni nziza"},
    "laptop":        {"rw": "mudasobwa",            "example": "mudasobwa wa none"},
    "computer":      {"rw": "mudasobwa",            "example": "mudasobwa gishya"},
    "television":    {"rw": "televiziyo",           "example": "televiziyo nini"},
    "charger":       {"rw": "chajilo",              "example": "chajilo ya telefoni"},
    "cable":         {"rw": "insinga",              "example": "insinga ya USB"},
    "earphones":     {"rw": "écouteur",             "example": "écouteur nziza"},
    "battery":       {"rw": "bateri",               "example": "bateri nziza"},
    "screen":        {"rw": "ecran",                "example": "ecran nini"},
    "watch":         {"rw": "saa",                  "example": "saa nziza"},
    "camera":        {"rw": "kamera",               "example": "kamera ifotora neza"},
    "speaker":       {"rw": "haut-parleur",         "example": "haut-parleur ikangura"},
    "bag":           {"rw": "agaseke",              "example": "agaseke ka mudasobwa"},
    "backpack":      {"rw": "umufuka w'inyuma",     "example": "umufuka w'inyuma nziza"},
    # Home equipment
    "cooking pot":   {"rw": "isafuriya",            "example": "isafuriya nini"},
    "refrigerator":  {"rw": "frigo",                "example": "frigo nziza"},
    "iron":          {"rw": "fer",                  "example": "fer yo gukanika"},
    "fan":           {"rw": "ventilateu",           "example": "ventilateu ikangura"},
    "blender":       {"rw": "blender",              "example": "blender ikorana neza"},
    "kettle":        {"rw": "bouilloire",           "example": "bouilloire ya metero"},
    "electricity":   {"rw": "amashanyarazi",        "example": "gukoresha amashanyarazi"},
    # Furniture
    "chair":         {"rw": "intebe",               "example": "intebe nziza y'ibiro"},
    "table":         {"rw": "mesa",                 "example": "mesa nini"},
    "bed":           {"rw": "igitanda",             "example": "igitanda cyiza"},
    "sofa":          {"rw": "sofa",                 "example": "sofa nziza"},
    "wardrobe":      {"rw": "garderobe",            "example": "garderobe nini"},
    "shelf":         {"rw": "etagere",              "example": "etagere y'ibitabo"},
    "mattress":      {"rw": "matelas",              "example": "matelas nziza"},
    "desk":          {"rw": "bureau",               "example": "bureau nziza"},
    # Beauty & personal care
    "cream":         {"rw": "kremu",                "example": "kremu y'uruhu"},
    "hair":          {"rw": "imisatsi",             "example": "amavuta y'imisatsi"},
    "oil":           {"rw": "amavuta",              "example": "amavuta meza"},
    "lotion":        {"rw": "losyo",                "example": "losyo y'umubiri"},
    "perfume":       {"rw": "parefumu",             "example": "parefumu nziza"},
    "shampoo":       {"rw": "shampoo",              "example": "shampoo y'imisatsi"},
    "soap":          {"rw": "isabuni",              "example": "isabuni nziza"},
    "skin":          {"rw": "uruhu",                "example": "uruhu rwiza"},
    "body":          {"rw": "umubiri",              "example": "amavuta y'umubiri"},
    "face":          {"rw": "mu maso",              "example": "kremu yo mu maso"},
    # Fashion
    "clothes":       {"rw": "impuzu",               "example": "impuzu nziza"},
    "shoes":         {"rw": "urukweto",             "example": "urukweto rwiza"},
    "dress":         {"rw": "robe",                 "example": "robe nziza"},
    "shirt":         {"rw": "chemise",              "example": "chemise ya gabo"},
    "trousers":      {"rw": "pantalon",             "example": "pantalon nziza"},
    "jacket":        {"rw": "ijaki",                "example": "ijaki nziza"},
    "wear":          {"rw": "kwambara",             "example": "kwambara neza"},
    "style":         {"rw": "style",                "example": "style nziza"},
    "kitenge":       {"rw": "kitenge",              "example": "kitenge nziza y'Afrika"},
}

# ---------------------------------------------------------------------------
# 2. PRODUCT DATA  (60 products — 10 per category)
#    Each product matches your Supabase schema exactly.
#    Full 300-product version: extend each category list below.
# ---------------------------------------------------------------------------

PRODUCTS_RAW = [

    # --- ACCESSORIES (10) ---
    {"name": "Phone Case Samsung Galaxy S23", "name_rw": "Akabesho ka Telefoni Samsung Galaxy S23",
     "description": "Durable protective case for Samsung Galaxy S23. Shockproof with raised edges.",
     "description_rw": "Akabesho gakingira telefoni Samsung Galaxy S23. Gakingira neza ntikashobore gutoneka.",
     "category": "Accessories", "price": 4500, "old_price": 6000, "badge": "Sale", "has_variation": True, "stock": 45},

    {"name": "USB-C Charging Cable 2m", "name_rw": "Insinga ya USB-C yo Gushaja 2m",
     "description": "Fast charging USB-C cable 2 meters long. Compatible with most Android phones and laptops.",
     "description_rw": "Insinga ya USB-C yo gushaja vuba. Ifite uburebure bwa metero 2, ikora na telefoni nyinshi.",
     "category": "Accessories", "price": 3500, "old_price": None, "badge": None, "has_variation": False, "stock": 120},

    {"name": "Wireless Earbuds Bluetooth 5.0", "name_rw": "Écouteur Zidafite Insinga Bluetooth 5.0",
     "description": "True wireless earbuds with 24-hour battery life and noise cancellation.",
     "description_rw": "Écouteur zidafite insinga zikora na Bluetooth. Bateri imara amasaha 24, zibuza amajwi yo hanze.",
     "category": "Accessories", "price": 18000, "old_price": 24000, "badge": "Sale", "has_variation": False, "stock": 22},

    {"name": "Power Bank 20000mAh Fast Charge", "name_rw": "Bateri Nini yo Gushaja Telefoni 20000mAh",
     "description": "20000mAh power bank with dual USB output and fast charging. Charges phones up to 5 times.",
     "description_rw": "Bateri nini ishaja telefoni inshuro 5. Ifite gushaja vuba kandi ireba gushaja ibintu bibiri.",
     "category": "Accessories", "price": 22000, "old_price": 28000, "badge": "Best Seller", "has_variation": False, "stock": 35},

    {"name": "Laptop Bag 15.6 Inch Waterproof", "name_rw": "Agaseke ka Mudasobwa 15.6 Inchi Kagabana Amazi",
     "description": "Waterproof laptop bag fits up to 15.6 inch laptops. Multiple compartments.",
     "description_rw": "Agaseke ka mudasobwa kagabana amazi. Kakwiye mudasobwa kugeza 15.6 inchi, gifite ibikombe byinshi.",
     "category": "Accessories", "price": 14000, "old_price": None, "badge": None, "has_variation": True, "stock": 40},

    {"name": "Smartwatch Fitness Tracker", "name_rw": "Saa ya None Ikurikirana Ubuzima",
     "description": "Smartwatch with heart rate monitor, step counter and sleep tracking.",
     "description_rw": "Saa ya none ikurikirana ubuzima. Igaragaza intera z'umutima, ingambwe, no guturika.",
     "category": "Accessories", "price": 28000, "old_price": 35000, "badge": "Sale", "has_variation": True, "stock": 18},

    {"name": "Wireless Bluetooth Mouse", "name_rw": "Maus Ikora na Bluetooth Idafite Insinga",
     "description": "Silent wireless Bluetooth mouse. Compatible with all laptops and tablets.",
     "description_rw": "Maus ikora na Bluetooth idafite insinga. Ikora neza na mudasobwa na tablette yose.",
     "category": "Accessories", "price": 9500, "old_price": 12000, "badge": None, "has_variation": True, "stock": 42},

    {"name": "65W Fast Phone Charger", "name_rw": "Chajilo ya Telefoni Ikora Vuba 65W",
     "description": "65W fast charger compatible with most smartphones. 0 to 50% in 20 minutes.",
     "description_rw": "Chajilo ikora vuba cane ya 65W. Ishaja telefoni uhereye 0 kugeza 50% mu minota 20.",
     "category": "Accessories", "price": 12000, "old_price": 16000, "badge": "Hot", "has_variation": False, "stock": 60},

    {"name": "Backpack 30L Waterproof", "name_rw": "Umufuka w'Inyuma 30L Ugabana Amazi",
     "description": "30L waterproof backpack with USB charging port. Great for school and travel.",
     "description_rw": "Umufuka w'inyuma wa litiro 30 ugabana amazi. Ufite inzira ya USB yo gushaja.",
     "category": "Accessories", "price": 19000, "old_price": 25000, "badge": "Sale", "has_variation": True, "stock": 30},

    {"name": "Tempered Glass Screen Protector", "name_rw": "Ingirabuzima y'Ecran ya Verre Forte",
     "description": "9H hardness tempered glass. Anti-fingerprint and bubble-free installation.",
     "description_rw": "Ingirabuzima y'ecran ya verre forte cyane. Ntishyira intoki, kandi irashyirwa neza.",
     "category": "Accessories", "price": 2500, "old_price": None, "badge": None, "has_variation": True, "stock": 200},

    # --- ELECTRONICS (10) ---
    {"name": "Samsung Galaxy A54 5G 128GB", "name_rw": "Telefoni Samsung Galaxy A54 5G 128GB",
     "description": "Samsung Galaxy A54 5G with 6.4-inch AMOLED display, 50MP camera, 5000mAh battery.",
     "description_rw": "Telefoni Samsung Galaxy A54 5G ifite ecran ya 6.4 inchi, kamera ya 50MP na bateri ya 5000mAh.",
     "category": "Electronics", "price": 310000, "old_price": 340000, "badge": "Sale", "has_variation": True, "stock": 15},

    {"name": "iPhone 14 128GB", "name_rw": "Telefoni iPhone 14 128GB",
     "description": "Apple iPhone 14 with 6.1-inch Super Retina display, dual cameras, A15 Bionic chip.",
     "description_rw": "Telefoni iPhone 14 ifite ecran nziza ya 6.1 inchi, kamera ebyiri na puces ya A15 Bionic.",
     "category": "Electronics", "price": 620000, "old_price": None, "badge": None, "has_variation": True, "stock": 8},

    {"name": "Tecno Camon 20 Pro 256GB", "name_rw": "Telefoni Tecno Camon 20 Pro 256GB",
     "description": "Tecno Camon 20 Pro with 50MP camera, 6.67-inch AMOLED display and fast charging.",
     "description_rw": "Telefoni Tecno Camon 20 Pro ifite kamera ya 50MP, ecran ya 6.67 inchi na gushaja vuba.",
     "category": "Electronics", "price": 220000, "old_price": 250000, "badge": "Hot", "has_variation": True, "stock": 20},

    {"name": "HP Laptop 15 Core i5 8GB RAM", "name_rw": "Mudasobwa HP 15 Core i5 8GB RAM",
     "description": "HP 15-inch laptop with Intel Core i5, 8GB RAM, 512GB SSD, Windows 11.",
     "description_rw": "Mudasobwa HP wa 15 inchi ufite Intel Core i5, RAM ya 8GB, SSD ya 512GB na Windows 11.",
     "category": "Electronics", "price": 490000, "old_price": 550000, "badge": "Sale", "has_variation": False, "stock": 10},

    {"name": "MacBook Air M1 8GB 256GB", "name_rw": "Mudasobwa MacBook Air M1 8GB 256GB",
     "description": "Apple MacBook Air with M1 chip, 13.3-inch Retina display, up to 18-hour battery.",
     "description_rw": "Mudasobwa Apple MacBook Air ufite puces ya M1, ecran ya 13.3 inchi nziza, bateri imara amasaha 18.",
     "category": "Electronics", "price": 780000, "old_price": None, "badge": "Best Seller", "has_variation": False, "stock": 6},

    {"name": "Samsung Smart TV 43 Inch 4K", "name_rw": "Televiziyo Samsung Smart 43 Inchi 4K",
     "description": "Samsung 43-inch 4K UHD Smart TV with HDR. Built-in WiFi, Netflix and YouTube.",
     "description_rw": "Televiziyo Samsung ya 43 inchi 4K UHD Smart TV. Ifite WiFi imbere, ikoresha Netflix na YouTube.",
     "category": "Electronics", "price": 420000, "old_price": 480000, "badge": "Sale", "has_variation": False, "stock": 8},

    {"name": "JBL Flip 6 Portable Speaker", "name_rw": "Haut-parleur JBL Flip 6 Yiganye",
     "description": "JBL Flip 6 portable Bluetooth speaker. Waterproof, 12-hour battery, powerful bass.",
     "description_rw": "Haut-parleur JBL Flip 6 yiganye ikora na Bluetooth. Igabana amazi, bateri imara amasaha 12.",
     "category": "Electronics", "price": 85000, "old_price": 100000, "badge": "Hot", "has_variation": True, "stock": 18},

    {"name": "WiFi Router TP-Link AC1200", "name_rw": "Routeur ya WiFi TP-Link AC1200",
     "description": "TP-Link dual-band WiFi router AC1200. Fast internet for up to 20 connections.",
     "description_rw": "Routeur ya WiFi TP-Link AC1200 ikora ku mavurugano abiri. Itanga internet nziza.",
     "category": "Electronics", "price": 48000, "old_price": 58000, "badge": None, "has_variation": False, "stock": 20},

    {"name": "Canon EOS 1500D DSLR Camera", "name_rw": "Kamera ya Canon EOS 1500D",
     "description": "Canon EOS 1500D DSLR with 24.1MP sensor, built-in WiFi and Full HD video.",
     "description_rw": "Kamera Canon EOS 1500D ifite sensor ya 24.1MP, WiFi imbere na vidiyo ya Full HD.",
     "category": "Electronics", "price": 380000, "old_price": None, "badge": None, "has_variation": False, "stock": 5},

    {"name": "Infinix Note 30 Pro 256GB", "name_rw": "Telefoni Infinix Note 30 Pro 256GB",
     "description": "Infinix Note 30 Pro with 6.78-inch AMOLED, 108MP camera and 45W fast charging.",
     "description_rw": "Telefoni Infinix Note 30 Pro ifite ecran ya 6.78 inchi, kamera ya 108MP na gushaja vuba ya 45W.",
     "category": "Electronics", "price": 185000, "old_price": 210000, "badge": "New", "has_variation": True, "stock": 18},

    # --- SMALL HOME EQUIPMENT (10) ---
    {"name": "Electric Kettle 1.8L Stainless Steel", "name_rw": "Bouilloire ya Amashanyarazi 1.8L ya Inox",
     "description": "1.8L stainless steel electric kettle. Boils water in under 3 minutes, auto shutoff.",
     "description_rw": "Bouilloire ya inox ya 1.8L ikora na amashanyarazi. Ibyarira amazi mu minota 3, ihagarara yonyine.",
     "category": "Small Home Equipment", "price": 16000, "old_price": 20000, "badge": "Sale", "has_variation": False, "stock": 35},

    {"name": "Blender 600W Smoothie Maker", "name_rw": "Blender ya 600W yo Gukora Smoothie",
     "description": "600W high-speed blender for smoothies, soups and sauces. 1.5L jar with 6-blade system.",
     "description_rw": "Blender ya 600W yo gukora smoothie, supu na sosi. Bocal ya 1.5L ifite meno 6.",
     "category": "Small Home Equipment", "price": 24000, "old_price": 30000, "badge": None, "has_variation": False, "stock": 28},

    {"name": "Rice Cooker 1.8L with Steamer", "name_rw": "Isafuriya yo Guteka Umuceri 1.8L",
     "description": "1.8L rice cooker with steaming tray. Cooks perfect rice every time, keep-warm function.",
     "description_rw": "Isafuriya yo guteka umuceri ya 1.8L ifite plateau yo kubika ubushyuhe. Iteka umuceri neza.",
     "category": "Small Home Equipment", "price": 22000, "old_price": None, "badge": "Best Seller", "has_variation": False, "stock": 40},

    {"name": "Air Fryer 5L Digital", "name_rw": "Air Fryer ya 5L Numerique",
     "description": "5L digital air fryer with 8 preset programs. Cooks with little to no oil.",
     "description_rw": "Air fryer ya 5L ufite programa 8. Iteka ukoresha amavuta make cyangwa nta mavuta, kurya neza.",
     "category": "Small Home Equipment", "price": 48000, "old_price": 58000, "badge": "Hot", "has_variation": False, "stock": 18},

    {"name": "Microwave Oven 20L Digital", "name_rw": "Four à Micro-onde 20L Numerique",
     "description": "20L digital microwave with 6 cooking modes and child lock. 700W power.",
     "description_rw": "Four à micro-onde ya 20L ufite ibigereranyo 6 byo guteka na lock y'abana. Mocy ya 700W.",
     "category": "Small Home Equipment", "price": 68000, "old_price": 82000, "badge": "Sale", "has_variation": False, "stock": 12},

    {"name": "Steam Iron Professional 2400W", "name_rw": "Fer yo Gukanika Impuzu Ifite Umwotsi 2400W",
     "description": "Professional steam iron with non-stick soleplate. 2400W for quick ironing.",
     "description_rw": "Fer yo gukanika impuzu ifite ubushyuhe bw'umwotsi na soleplate y'amezi. Mocy ya 2400W.",
     "category": "Small Home Equipment", "price": 18000, "old_price": 23000, "badge": None, "has_variation": False, "stock": 30},

    {"name": "Standing Fan 18 Inch 3-Speed", "name_rw": "Ventilateu Inkingi ya 18 Inchi 3 Vites",
     "description": "18-inch standing fan with 3 speed settings and oscillation. Quiet motor.",
     "description_rw": "Ventilateu inkingi ya 18 inchi ifite vites 3 ishobora kuzunguruka. Moteri iturika gato.",
     "category": "Small Home Equipment", "price": 28000, "old_price": 35000, "badge": None, "has_variation": False, "stock": 22},

    {"name": "Hair Dryer Professional 2000W", "name_rw": "Sèche-cheveux Nziza 2000W",
     "description": "Professional 2000W hair dryer with ionic technology. 3 heat settings.",
     "description_rw": "Sèche-cheveux nziza ya 2000W ifite tekinoloji y'ionic. Ubushyuhe 3 na bouton yo gukosha vuba.",
     "category": "Small Home Equipment", "price": 24000, "old_price": 30000, "badge": None, "has_variation": False, "stock": 22},

    {"name": "Vacuum Cleaner 2000W Bagless", "name_rw": "Machine yo Gukurura Umukungugu 2000W",
     "description": "2000W bagless vacuum cleaner with HEPA filter. Powerful suction for all floors.",
     "description_rw": "Machine yo gukurura umukungugu ya 2000W ya HEPA filtre. Gisunika neza ku mbaho zose.",
     "category": "Small Home Equipment", "price": 58000, "old_price": 70000, "badge": None, "has_variation": False, "stock": 10},

    {"name": "Coffee Maker Drip 1.5L", "name_rw": "Machine yo Gutunganya Kafe ya 1.5L",
     "description": "Drip coffee maker 1.5L capacity. Anti-drip valve, keep-warm plate.",
     "description_rw": "Machine yo gutunganya kafe ya 1.5L. Valve ikingira amazi, ibika ubushyuhe.",
     "category": "Small Home Equipment", "price": 32000, "old_price": 40000, "badge": None, "has_variation": False, "stock": 15},

    # --- FURNITURE (10) ---
    {"name": "Ergonomic Office Chair Mesh", "name_rw": "Intebe y'Ibiro Nziza ya Mesh",
     "description": "Ergonomic mesh office chair with lumbar support and adjustable height.",
     "description_rw": "Intebe y'ibiro ya mesh nziza ifite inshingano y'umugongo na uburebure bushobora guturika.",
     "category": "Furniture", "price": 95000, "old_price": 120000, "badge": "Sale", "has_variation": True, "stock": 10},

    {"name": "Gaming Chair Recliner", "name_rw": "Intebe yo Gukina Ishobora Guhohora",
     "description": "Racing-style gaming chair with 180-degree recline and lumbar support cushions.",
     "description_rw": "Intebe yo gukina ya style ya course ishobora guhohora, ifite imfuka y'umugongo.",
     "category": "Furniture", "price": 120000, "old_price": 145000, "badge": "Hot", "has_variation": True, "stock": 8},

    {"name": "3-Seater Fabric Sofa", "name_rw": "Sofa Ifite Imyanya 3 ya Tissu",
     "description": "Comfortable 3-seater fabric sofa with cushion armrests. Modern living room design.",
     "description_rw": "Sofa nziza ya tissu ifite imyanya 3. Design ya none kuri salon, ifite amaboko y'imfuka.",
     "category": "Furniture", "price": 280000, "old_price": 340000, "badge": "Sale", "has_variation": True, "stock": 5},

    {"name": "Dining Table 6-Seater with Chairs", "name_rw": "Mesa yo Kurya Ifite Imyanya 6 n'Intebe",
     "description": "6-seater dining table set including 6 matching chairs. Modern design.",
     "description_rw": "Mesa yo kurya na intebe 6 zikwiriye. Design ya none kuri mu rugo cyangwa restora.",
     "category": "Furniture", "price": 320000, "old_price": 390000, "badge": "Sale", "has_variation": True, "stock": 4},

    {"name": "Double Bed Frame Queen Size", "name_rw": "Igitanda cy'Abantu Babiri Queen Size",
     "description": "Queen size double bed frame with storage headboard. Fits 160x200cm mattress.",
     "description_rw": "Igitanda cy'abantu babiri queen size gifite umutwe w'aho gutereka. Gikwiye matelas ya 160x200cm.",
     "category": "Furniture", "price": 185000, "old_price": 225000, "badge": None, "has_variation": True, "stock": 5},

    {"name": "Wardrobe 3-Door Mirror", "name_rw": "Garderobe Ifite Inzugi 3 na Miroir",
     "description": "3-door sliding mirror wardrobe. Full-length mirror, internal shelves and rail.",
     "description_rw": "Garderobe ifite inzugi 3 zo gunyeganyeza na miroir. Miroir nini, amahurizo n'inzitizi imbere.",
     "category": "Furniture", "price": 265000, "old_price": None, "badge": "New", "has_variation": True, "stock": 3},

    {"name": "Study Desk with Bookshelf", "name_rw": "Bureau y'Ishuri Ifite Etagere",
     "description": "Study desk with built-in bookshelf and drawer. Perfect for students and home office.",
     "description_rw": "Bureau y'ishuri ifite etagere y'ibitabo na tiroir. Nziza ku banyeshuri na bureau y'imazu.",
     "category": "Furniture", "price": 75000, "old_price": 90000, "badge": None, "has_variation": True, "stock": 10},

    {"name": "Bookshelf 5-Tier Wooden", "name_rw": "Etagere y'Ibitabo ya Kabura Ifite Amahurizo 5",
     "description": "5-tier wooden bookshelf for books and display. Simple assembly, 80x25x175cm.",
     "description_rw": "Etagere y'ibitabo ya kabura ifite amahurizo 5. Yoroshye gushyingura, 80x25x175cm.",
     "category": "Furniture", "price": 52000, "old_price": 65000, "badge": None, "has_variation": True, "stock": 10},

    {"name": "TV Stand Unit with Storage", "name_rw": "Meuble ya Televiziyo Ifite Aho Gutereka",
     "description": "TV stand for up to 60-inch TVs with 2 cabinets and open shelves.",
     "description_rw": "Meuble ya televiziyo kugeza inchi 60 ifite armoire 2 n'amahurizo. Finition ya none.",
     "category": "Furniture", "price": 78000, "old_price": 95000, "badge": None, "has_variation": True, "stock": 7},

    {"name": "Double Spring Mattress 160x200cm", "name_rw": "Matelas y'Inzitizi Abantu Babiri 160x200cm",
     "description": "160x200cm pocket spring mattress with memory foam top layer. Firm support.",
     "description_rw": "Matelas ya 160x200cm ifite inzitizi na couche ya memory foam hejuru. Ifasha neza.",
     "category": "Furniture", "price": 145000, "old_price": 175000, "badge": None, "has_variation": False, "stock": 8},

    # --- BEAUTY & PERSONAL CARE (10) ---
    {"name": "Nivea Body Lotion Soft 400ml", "name_rw": "Losyo y'Umubiri Nivea Nziza 400ml",
     "description": "Nivea Soft moisturising body lotion with jojoba oil and vitamin E. For all skin types.",
     "description_rw": "Losyo y'umubiri Nivea nziza ifite amavuta ya jojoba na vitamine E. Ikora ku ruhu rw'ubwoko bwose.",
     "category": "Beauty & Personal Care", "price": 5500, "old_price": None, "badge": "Best Seller", "has_variation": False, "stock": 80},

    {"name": "Dove Body Wash 500ml", "name_rw": "Savon y'Umubiri Dove 500ml",
     "description": "Dove moisturising body wash with 1/4 moisturising cream. Gentle on sensitive skin.",
     "description_rw": "Savon y'umubiri Dove ifite cream y'amazi. Igora uruhu rwa sensitive.",
     "category": "Beauty & Personal Care", "price": 7500, "old_price": None, "badge": None, "has_variation": True, "stock": 65},

    {"name": "Head and Shoulders Shampoo 400ml", "name_rw": "Shampoo ya Head and Shoulders 400ml",
     "description": "Head and Shoulders anti-dandruff shampoo. Removes flakes and soothes scalp.",
     "description_rw": "Shampoo ya Head and Shoulders ikuraho pellicules. Ikoza umutwe n'umuhando. Ihumura neza.",
     "category": "Beauty & Personal Care", "price": 7000, "old_price": None, "badge": None, "has_variation": True, "stock": 75},

    {"name": "Olay Total Effects 7-in-1 Face Cream", "name_rw": "Kremu ya Olay Total Effects 7 mu 1",
     "description": "Olay Total Effects 7-in-1 anti-ageing face cream. Reduces wrinkles and brightens skin.",
     "description_rw": "Kremu yo mu maso ya Olay 7 mu 1 ikingira gukura. Igabanya imipfukamye kandi ikura uruhu.",
     "category": "Beauty & Personal Care", "price": 16000, "old_price": 20000, "badge": None, "has_variation": False, "stock": 35},

    {"name": "Maybelline Fit Me Foundation", "name_rw": "Foundation ya Maybelline Fit Me",
     "description": "Maybelline Fit Me Matte + Poreless foundation. 40 shades for natural to full coverage.",
     "description_rw": "Foundation ya Maybelline Fit Me. Amabara 40 yo gufunika neza mu maso.",
     "category": "Beauty & Personal Care", "price": 12000, "old_price": None, "badge": "Best Seller", "has_variation": True, "stock": 45},

    {"name": "Cantu Shea Butter Leave-In Cream", "name_rw": "Cantu Shea Butter Kremu y'Imisatsi",
     "description": "Cantu leave-in conditioning cream with shea butter. For natural and relaxed hair.",
     "description_rw": "Cantu kremu y'imisatsi ya shea butter. Nziza kuri imisatsi ya kamere na iryohewe.",
     "category": "Beauty & Personal Care", "price": 12000, "old_price": None, "badge": None, "has_variation": False, "stock": 40},

    {"name": "La Roche-Posay SPF50 Sunscreen", "name_rw": "Kremu Ikingira Izuba La Roche-Posay SPF50",
     "description": "La Roche-Posay Anthelios SPF50+ sunscreen for face. Lightweight, for all skin types.",
     "description_rw": "Kremu ikingira izuba ya La Roche-Posay SPF50+ yo mu maso. Yoroheje, ikora ku ruhu rw'ubwoko bwose.",
     "category": "Beauty & Personal Care", "price": 28000, "old_price": None, "badge": None, "has_variation": False, "stock": 18},

    {"name": "Nivea Deodorant Roll-On 50ml", "name_rw": "Déodorant ya Nivea Roll-On 50ml",
     "description": "Nivea Pearl and Beauty roll-on deodorant for women. 48-hour odour protection.",
     "description_rw": "Déodorant ya Nivea roll-on k'umugore. Ikingira cyobo amasaa 48.",
     "category": "Beauty & Personal Care", "price": 4500, "old_price": None, "badge": None, "has_variation": False, "stock": 90},

    {"name": "Revlon Nail Polish Set 6 Colors", "name_rw": "Inyandiko ya Revlon ya Vernis z'Inzara Amabara 6",
     "description": "Revlon gel nail polish set with 6 trendy colors. Chip-resistant, quick dry.",
     "description_rw": "Inyandiko ya 6 za Revlon vernis z'inzara. Amabara ashimishije, yumirwa vuba ntishyikama.",
     "category": "Beauty & Personal Care", "price": 12000, "old_price": None, "badge": "Hot", "has_variation": False, "stock": 35},

    {"name": "Cetaphil Moisturising Cream 250g", "name_rw": "Kremu yo Gutuza Uruhu Cetaphil 250g",
     "description": "Cetaphil moisturising cream for dry and sensitive skin. Dermatologist recommended.",
     "description_rw": "Kremu yo gutuza uruhu Cetaphil kuri uruhu rwuma n'urwumva vuba. Ishimirwa na ba muganga b'uruhu.",
     "category": "Beauty & Personal Care", "price": 22000, "old_price": None, "badge": None, "has_variation": False, "stock": 25},

    # --- FASHION (10) ---
    {"name": "Men's Classic Polo Shirt", "name_rw": "Chemise Polo ya Gabo Nziza",
     "description": "Classic pique polo shirt for men. 8 colors available. 100% cotton, comfortable fit.",
     "description_rw": "Chemise polo ya kera ya gabo. Iboneka mu ibara 8. Coton ya 100%, iryoherwa.",
     "category": "Fashion", "price": 12000, "old_price": None, "badge": None, "has_variation": True, "stock": 50},

    {"name": "Men's Slim Fit Jeans Blue", "name_rw": "Pantalon ya Jeans ya Gabo Slim Fit Ubururu",
     "description": "Men's slim fit blue jeans. Classic 5-pocket design, stretch denim for comfort.",
     "description_rw": "Pantalon ya jeans ya gabo slim fit y'ubururu. Design ya poche 5, denim ishobora gutandukana.",
     "category": "Fashion", "price": 24000, "old_price": None, "badge": "Best Seller", "has_variation": True, "stock": 35},

    {"name": "Women's Floral Midi Dress", "name_rw": "Robe ya Fleurs Midi y'Umugore",
     "description": "Women's floral print midi dress. Flowy fabric, V-neck design. Perfect for summer.",
     "description_rw": "Robe ya fleurs midi y'umugore. Impuzu iringanira, cou ya V. Nziza cane mu gushyushya.",
     "category": "Fashion", "price": 20000, "old_price": 25000, "badge": None, "has_variation": True, "stock": 30},

    {"name": "Women's High-Waist Jeans", "name_rw": "Pantalon ya Jeans Yuzuye y'Umugore",
     "description": "Women's high-waist skinny jeans. Available in blue, black and grey. Stretch denim.",
     "description_rw": "Pantalon ya jeans yuzuye y'umugore. Iboneka mu ubururu, umukara n'ibinzusu. Ishobora gutandukana.",
     "category": "Fashion", "price": 22000, "old_price": None, "badge": "Best Seller", "has_variation": True, "stock": 40},

    {"name": "Men's White Sneakers", "name_rw": "Sneakers Zera za Gabo",
     "description": "Clean all-white men's sneakers. Minimalist design, rubber sole, daily wear.",
     "description_rw": "Sneakers zera za gabo nziza. Design yoroheje, sole ya caoutchouc, zizira buri munsi.",
     "category": "Fashion", "price": 28000, "old_price": 35000, "badge": "Hot", "has_variation": True, "stock": 28},

    {"name": "Kitenge African Print Fabric 6 Yards", "name_rw": "Kitenge y'Imiterere y'Afurika 6 Metero",
     "description": "Authentic 100% cotton kitenge African print fabric 6 yards. Vibrant colors.",
     "description_rw": "Kitenge ya ukuri ya coton 100% ya 6 metero. Amabara meza, ifite impanuro ku ruhande rwombi.",
     "category": "Fashion", "price": 18000, "old_price": None, "badge": "Best Seller", "has_variation": True, "stock": 45},

    {"name": "Traditional Rwanda Umushanana", "name_rw": "Umushanana w'Igihugu cy'u Rwanda",
     "description": "Traditional Rwandan Umushanana ceremonial dress. Elegant for weddings and formal events.",
     "description_rw": "Umushanana w'igihugu cy'u Rwanda nziza. Igaragara neza ku bitwita n'ibirori by'isanzwe.",
     "category": "Fashion", "price": 45000, "old_price": None, "badge": "Best Seller", "has_variation": True, "stock": 12},

    {"name": "Ankara Print Shirt Men", "name_rw": "Chemise ya Ankara ya Gabo",
     "description": "Men's Ankara African print short-sleeve shirt. 100% cotton, vibrant traditional prints.",
     "description_rw": "Chemise ya Ankara ya gabo ifite amaboko make. Coton 100%, impanuro za kera za Afurika nziza.",
     "category": "Fashion", "price": 18000, "old_price": None, "badge": "Hot", "has_variation": True, "stock": 25},

    {"name": "Men's 2-Piece Suit Navy", "name_rw": "Costume ya Gabo Ebyiri y'Ubururu Bwuzuye",
     "description": "Men's tailored 2-piece navy suit. Slim fit jacket and matching trousers.",
     "description_rw": "Costume ya gabo y'ubururu bwuzuye ifite veste na pantalon bikwiriye.",
     "category": "Fashion", "price": 85000, "old_price": 105000, "badge": "Sale", "has_variation": True, "stock": 10},

    {"name": "Children's School Uniform Set", "name_rw": "Imyambaro y'Ishuri y'Abana",
     "description": "Children's school uniform set. Machine washable, durable fabric. Multiple sizes.",
     "description_rw": "Inyandiko y'imyambaro y'ishuri y'abana. Impuzu ikomeye yoroshye gukaraba. Ingano nyinshi.",
     "category": "Fashion", "price": 16000, "old_price": None, "badge": None, "has_variation": True, "stock": 40},
]

# ---------------------------------------------------------------------------
# 3. QUERY DATASET  (90 queries — 30 per language pattern)
# ---------------------------------------------------------------------------

QUERIES_RAW = [
    # Full Kinyarwanda (30)
    {"query": "ndashaka telefoni nziza",                         "language": "rw",    "category": "Electronics"},
    {"query": "igiciro cya mudasobwa",                           "language": "rw",    "category": "Electronics"},
    {"query": "televiziyo nini ya samsung",                      "language": "rw",    "category": "Electronics"},
    {"query": "chajilo ya telefoni ikora vuba",                  "language": "rw",    "category": "Accessories"},
    {"query": "agaseke ka mudasobwa",                            "language": "rw",    "category": "Accessories"},
    {"query": "isafuriya nziza yo guteka umuceri",               "language": "rw",    "category": "Small Home Equipment"},
    {"query": "intebe y'ibiro nziza",                            "language": "rw",    "category": "Furniture"},
    {"query": "igitanda kinini cy'abantu babiri",                "language": "rw",    "category": "Furniture"},
    {"query": "losyo y'umubiri ya nivea",                        "language": "rw",    "category": "Beauty & Personal Care"},
    {"query": "impuzu nziza za gabo",                            "language": "rw",    "category": "Fashion"},
    {"query": "ndashaka ibicuruzwa bya phone",                   "language": "rw",    "category": "Electronics"},
    {"query": "ecouteur zidafite insinga",                       "language": "rw",    "category": "Accessories"},
    {"query": "bateri nini yo gushaja",                          "language": "rw",    "category": "Accessories"},
    {"query": "urukweto rwiza rwa gabo",                         "language": "rw",    "category": "Fashion"},
    {"query": "robe nziza y'umugore",                            "language": "rw",    "category": "Fashion"},
    {"query": "kremu yo mu maso nziza",                          "language": "rw",    "category": "Beauty & Personal Care"},
    {"query": "blender nziza yo gutunganya ibiribwa",            "language": "rw",    "category": "Small Home Equipment"},
    {"query": "matelas nziza kuri igitanda",                     "language": "rw",    "category": "Furniture"},
    {"query": "sofa nziza ya salon",                             "language": "rw",    "category": "Furniture"},
    {"query": "ventilateu nziza mu cyumba",                      "language": "rw",    "category": "Small Home Equipment"},
    {"query": "shampoo nziza y'imisatsi",                        "language": "rw",    "category": "Beauty & Personal Care"},
    {"query": "pantalon ya jeans ya gabo",                       "language": "rw",    "category": "Fashion"},
    {"query": "insinga ya USB-C yo gushaja",                     "language": "rw",    "category": "Accessories"},
    {"query": "fer yo gukanika impuzu",                          "language": "rw",    "category": "Small Home Equipment"},
    {"query": "saa nziza y'ikiganza",                            "language": "rw",    "category": "Accessories"},
    {"query": "mesa nziza yo kurya",                             "language": "rw",    "category": "Furniture"},
    {"query": "garderobe nini y'icyumba",                        "language": "rw",    "category": "Furniture"},
    {"query": "parefumu nziza k'umugore",                        "language": "rw",    "category": "Beauty & Personal Care"},
    {"query": "ndashaka air fryer nziza",                        "language": "rw",    "category": "Small Home Equipment"},
    {"query": "kitenge nziza y'afurika",                         "language": "rw",    "category": "Fashion"},

    # Full English (30)
    {"query": "best smartphone under 200000 RWF",               "language": "en",    "category": "Electronics"},
    {"query": "laptop for university students",                  "language": "en",    "category": "Electronics"},
    {"query": "fast charging cable USB-C",                       "language": "en",    "category": "Accessories"},
    {"query": "wireless earbuds noise cancellation",             "language": "en",    "category": "Accessories"},
    {"query": "power bank 20000mAh",                             "language": "en",    "category": "Accessories"},
    {"query": "ergonomic office chair",                          "language": "en",    "category": "Furniture"},
    {"query": "rice cooker 1.8L",                                "language": "en",    "category": "Small Home Equipment"},
    {"query": "samsung smart TV 43 inch",                        "language": "en",    "category": "Electronics"},
    {"query": "moisturising body lotion dry skin",               "language": "en",    "category": "Beauty & Personal Care"},
    {"query": "men slim fit jeans",                              "language": "en",    "category": "Fashion"},
    {"query": "bluetooth speaker waterproof",                    "language": "en",    "category": "Electronics"},
    {"query": "standing fan bedroom",                            "language": "en",    "category": "Small Home Equipment"},
    {"query": "women floral dress midi",                         "language": "en",    "category": "Fashion"},
    {"query": "coffee table wooden",                             "language": "en",    "category": "Furniture"},
    {"query": "face wash oily skin",                             "language": "en",    "category": "Beauty & Personal Care"},
    {"query": "laptop bag waterproof 15 inch",                   "language": "en",    "category": "Accessories"},
    {"query": "air fryer digital 5L",                            "language": "en",    "category": "Small Home Equipment"},
    {"query": "queen size mattress",                             "language": "en",    "category": "Furniture"},
    {"query": "gaming chair recliner",                           "language": "en",    "category": "Furniture"},
    {"query": "shampoo natural hair",                            "language": "en",    "category": "Beauty & Personal Care"},
    {"query": "kitenge African print fabric",                    "language": "en",    "category": "Fashion"},
    {"query": "wireless mouse keyboard",                         "language": "en",    "category": "Accessories"},
    {"query": "electric kettle stainless steel",                 "language": "en",    "category": "Small Home Equipment"},
    {"query": "women high waist jeans",                          "language": "en",    "category": "Fashion"},
    {"query": "bookshelf 5 tier wooden",                         "language": "en",    "category": "Furniture"},
    {"query": "smartwatch fitness tracker",                      "language": "en",    "category": "Accessories"},
    {"query": "foundation dark skin",                            "language": "en",    "category": "Beauty & Personal Care"},
    {"query": "HP laptop core i5",                               "language": "en",    "category": "Electronics"},
    {"query": "dining table 6 seater",                           "language": "en",    "category": "Furniture"},
    {"query": "traditional Rwanda dress",                        "language": "en",    "category": "Fashion"},

    # Mixed Kinyarwanda-English (30)
    {"query": "ndashaka laptop nziza kuri school",               "language": "mixed", "category": "Electronics"},
    {"query": "phone case ya Samsung nziza",                     "language": "mixed", "category": "Accessories"},
    {"query": "nitanga amafaranga 50000 kuri TV nziza",          "language": "mixed", "category": "Electronics"},
    {"query": "agaseke ka laptop waterproof",                    "language": "mixed", "category": "Accessories"},
    {"query": "sofa nziza kuri living room",                     "language": "mixed", "category": "Furniture"},
    {"query": "ndashaka blender yo gukora smoothie",             "language": "mixed", "category": "Small Home Equipment"},
    {"query": "igiciro cya iPhone 14 ni kangahe",                "language": "mixed", "category": "Electronics"},
    {"query": "impuzu nziza za running",                         "language": "mixed", "category": "Fashion"},
    {"query": "kremu nziza yo mu maso kuri oily skin",           "language": "mixed", "category": "Beauty & Personal Care"},
    {"query": "intebe nziza ya office chair",                    "language": "mixed", "category": "Furniture"},
    {"query": "ndashaka wireless earbuds nziza",                 "language": "mixed", "category": "Accessories"},
    {"query": "isafuriya nziza ya rice cooker 1.8L",             "language": "mixed", "category": "Small Home Equipment"},
    {"query": "robe nziza kuri party",                           "language": "mixed", "category": "Fashion"},
    {"query": "bateri nini ya power bank",                       "language": "mixed", "category": "Accessories"},
    {"query": "losyo nziza kuri dry skin",                       "language": "mixed", "category": "Beauty & Personal Care"},
    {"query": "igitanda nini kuri double bed",                   "language": "mixed", "category": "Furniture"},
    {"query": "ndashaka sneakers zera za gabo",                  "language": "mixed", "category": "Fashion"},
    {"query": "smart TV samsung igiciro gite",                   "language": "mixed", "category": "Electronics"},
    {"query": "shampoo nziza kuri natural hair",                 "language": "mixed", "category": "Beauty & Personal Care"},
    {"query": "mesa nziza ya dining table",                      "language": "mixed", "category": "Furniture"},
    {"query": "chajilo ikora vuba 65W",                          "language": "mixed", "category": "Accessories"},
    {"query": "ndashaka wardrobe nini y'icyumba",                "language": "mixed", "category": "Furniture"},
    {"query": "impuzu za gym nziza z'umugore",                   "language": "mixed", "category": "Fashion"},
    {"query": "kamera nziza ya DSLR kuri photos",                "language": "mixed", "category": "Electronics"},
    {"query": "foundation nziza kuri dark skin",                 "language": "mixed", "category": "Beauty & Personal Care"},
    {"query": "ndashaka mudasobwa HP core i5",                   "language": "mixed", "category": "Electronics"},
    {"query": "fer nziza yo gukanika steam",                     "language": "mixed", "category": "Small Home Equipment"},
    {"query": "umushanana nziza kuri wedding",                   "language": "mixed", "category": "Fashion"},
    {"query": "kitenge nziza ya African print",                  "language": "mixed", "category": "Fashion"},
    {"query": "ibicuruzwa bya beauty nziza kuri skin",           "language": "mixed", "category": "Beauty & Personal Care"},
]


# ---------------------------------------------------------------------------
# 4. GENERATION FUNCTIONS
# ---------------------------------------------------------------------------

def build_products(raw: list) -> list:
    """
    Add auto-generated fields to each product so it matches the
    Supabase schema exactly:
      id, is_active, created_at, search_text
    """
    products = []
    base_date = datetime(2024, 1, 1)

    for i, p in enumerate(raw):
        # Combine EN + RW text into one searchable field for TF-IDF
        search_text = " ".join([
            p["name"],
            p.get("name_rw", ""),
            p["description"],
            p.get("description_rw", ""),
            p["category"],
        ])

        product = {
            "id":             str(uuid.uuid4()),
            "name":           p["name"],
            "name_rw":        p.get("name_rw", ""),
            "description":    p["description"],
            "description_rw": p.get("description_rw", ""),
            "category":       p["category"],
            "price":          p["price"],
            "old_price":      p.get("old_price"),
            "badge":          p.get("badge"),
            "has_variation":  p.get("has_variation", False),
            "stock":          p.get("stock", 0),
            "is_active":      True,
            "image_url":      None,   # placeholder — add real URLs later
            "search_text":    search_text,
            "created_at":     (base_date + timedelta(days=i)).isoformat(),
        }
        products.append(product)

    return products


def build_queries(raw: list) -> list:
    """Add a unique ID to each query."""
    return [{"id": str(uuid.uuid4()), **q} for q in raw]


def build_lexicon(raw: dict) -> list:
    """Convert the lexicon dict to a flat list for easy JSON serialisation."""
    return [
        {"english": en, "kinyarwanda": data["rw"], "example": data["example"]}
        for en, data in raw.items()
    ]


def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(data):>4} records → {path}")


# ---------------------------------------------------------------------------
# 5. MAIN
# ---------------------------------------------------------------------------

def main():
    output_dir = Path("data/raw")

    print("\nKinyarwanda-English Bilingual Dataset Generator")
    print("=" * 50)

    products = build_products(PRODUCTS_RAW)
    queries  = build_queries(QUERIES_RAW)
    lexicon  = build_lexicon(LEXICON)

    save_json(products, output_dir / "products.json")
    save_json(queries,  output_dir / "queries.json")
    save_json(lexicon,  output_dir / "lexicon.json")

    print("\nSummary")
    print("-" * 30)
    print(f"  Products : {len(products)}")
    print(f"  Queries  : {len(queries)} "
          f"({sum(1 for q in queries if q['language']=='rw')} RW / "
          f"{sum(1 for q in queries if q['language']=='en')} EN / "
          f"{sum(1 for q in queries if q['language']=='mixed')} mixed)")
    print(f"  Lexicon  : {len(lexicon)} terms")
    print("\nAll files saved to data/raw/")
    print("Next step: python -c \"import json; d=json.load(open('data/raw/products.json')); print(d[0])\"")


if __name__ == "__main__":
    main()