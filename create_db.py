import uuid

import sqlalchemy

# CREATE DATABASE
engine = sqlalchemy.create_engine("mysql://root:123@localhost")
engine.execute("DROP DATABASE IF EXISTS shop")
engine.execute("CREATE DATABASE shop")
engine.execute("USE shop")

# CREATE PRODUCTS
engine.execute("create table product("
               "id varchar(255) primary key, "
               "name varchar(80) not null,"
               "stock int not null default 0,"
               "price decimal(10, 2) not null) "
               "engine=InnoDB default charset=utf8mb4;")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO A',"
               "5,"
               "10.99)")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO B',"
               "1,"
               "5.00)")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO C',"
               "4,"
               "3.80)")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO D',"
               "2,"
               "7.95)")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO E',"
               "3,"
               "20.00)")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO F',"
               "1,"
               "12.98)")
engine.execute("insert into product values("
               f"'{uuid.uuid4()}',"
               "'PRODUTO G',"
               "5,"
               "17.50)")

# CREATE COUPON

engine.execute("create table coupon("
               "id bigint primary key auto_increment, "
               "code varchar(80) not null unique, "
               "discount_percentage decimal(10, 2) not null, "
               "is_valid tinyint(1) not null default 0)"
               " engine=InnoDB default charset=utf8mb4;")

engine.execute("insert into coupon(code, discount_percentage, is_valid) values("
               "'VALE10',"
               "10,"
               "1)")

engine.execute("insert into coupon(code, discount_percentage, is_valid) values("
               "'VALE12',"
               "12,"
               "1)")

engine.execute("insert into coupon(code, discount_percentage, is_valid) values("
               "'VALE20',"
               "20,"
               "1)")

engine.execute("insert into coupon(code, discount_percentage, is_valid) values("
               "'VALE7',"
               "7,"
               "1)")

engine.execute("insert into coupon(code, discount_percentage, is_valid) values("
               "'VALE50',"
               "50,"
               "0)")

# CREATE SHOPPING_CART
engine.execute("create table shopping_cart("
               "id varchar(255) primary key,"
               "coupon_id bigint,"
               "constraint fk_shopping_cart_coupon foreign key (coupon_id) references coupon (id))"
               "engine=InnoDB default charset=utf8mb4;")

engine.execute("create table products_in_shopping_cart("
               "id bigint primary key auto_increment, "
               "quantity int not null, "
               "product_id varchar(255) not null, "
               "shopping_cart_id varchar(255) not null, "
               "constraint fk_product_shopping_cart_product foreign key (product_id) references product (id), "
               "constraint fk_product_shopping_cart_cart foreign key (shopping_cart_id) references shopping_cart (id))"
               " engine=InnoDB default charset=utf8mb4;")

