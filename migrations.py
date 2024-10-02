sql_create_categories = """
    CREATE TABLE IF NOT EXISTS Categories (
        cat_id INTEGER PRIMARY KEY,
        cat_url TEXT NOT NULL,
        cat_title TEXT NOT NULL
    )
"""

sql_create_shops = """
    CREATE TABLE IF NOT EXISTS Shops (
        shop_id INTEGER NOT NULL,
        shop_url TEXT NOT NULL,
        shop_addr TEXT NOT NULL,
        shop_tel TEXT NOT NULL
    )
"""

sql_create_parser_config = """
    CREATE TABLE IF NOT EXISTS ParserConfig (
        town_id INTEGER NOT NULL,
        town_name TEXT NOT NULL,
        shop_id INTEGER NOT NULL
    )
"""

sql_create_parsed_products = """
    CREATE TABLE IF NOT EXISTS Parse (
        parse_hash INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_url TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_size TEXT NOT NULL,
        product_vendor_code TEXT NOT NULL,
        product_discount_price TEXT NOT NULL,
        product_retail_price TEXT NOT NULL,
        shop_availability TEXT NOT NULL
    )
"""