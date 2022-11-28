DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
USE shop;

create table product(
    id varchar(255) primary key,
    name varchar(80) not null,
    stock int not null default 0,
    price decimal(10, 2) not null)
    engine=InnoDB default charset=utf8mb4;

insert into product values(UUID(), 'PRODUTO A', 5, 10.99);
insert into product values(UUID(), 'PRODUTO B', 3, 1.99);
insert into product values(UUID(), 'PRODUTO C', 2, 5.00);
insert into product values(UUID(), 'PRODUTO D', 1, 3.97);
insert into product values(UUID(), 'PRODUTO E', 10, 27.78);
insert into product values(UUID(), 'PRODUTO F', 50, 12.00);
insert into product values(UUID(), 'PRODUTO G', 7, 7.00);
insert into product values(UUID(), 'PRODUTO H', 12, 33.50);

create table coupon(
               id bigint primary key auto_increment,
               code varchar(80) not null unique,
               discount_percentage decimal(10, 2) not null,
               is_valid tinyint(1) not null default 0)
               engine=InnoDB default charset=utf8mb4;

insert into coupon(code, discount_percentage, is_valid) values('VALE10',10,1);
insert into coupon(code, discount_percentage, is_valid) values('VALE7',7,1);
insert into coupon(code, discount_percentage, is_valid) values('VALE15',15,1);
insert into coupon(code, discount_percentage, is_valid) values('VALE25',25,1);
insert into coupon(code, discount_percentage, is_valid) values('VALE50',50,0);

create table shopping_cart(
               id varchar(255) primary key,
               coupon_id bigint,
               constraint fk_shopping_cart_coupon foreign key (coupon_id) references coupon (id))
               engine=InnoDB default charset=utf8mb4;

create table products_in_shopping_cart(
               id bigint primary key auto_increment,
               quantity int not null,
               product_id varchar(255) not null,
               shopping_cart_id varchar(255) not null,
               constraint fk_product_shopping_cart_product foreign key (product_id) references product (id),
               constraint fk_product_shopping_cart_cart foreign key (shopping_cart_id) references shopping_cart (id))
               engine=InnoDB default charset=utf8mb4;