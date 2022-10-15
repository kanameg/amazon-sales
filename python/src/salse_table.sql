CREATE TABLE IF NOT EXISTS book (
    id integer primary key autoincrement,    
    title text not null,
    url text not null,
    image_url text,
    price integer,
    return_price integer,
    sale_id integer,
    foreign key (sale_id) references sale(id)
);

CREATE TABLE IF NOT EXISTS sale (
    id integer primary key autoincrement,
    name text,
    url text,
    available integer
);


CREATE TABLE IF NOT EXISTS test (
    id integer primary key autoincrement,
    name text
);
