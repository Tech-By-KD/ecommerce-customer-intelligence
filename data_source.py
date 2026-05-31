"""
data_source.py — Simulates FakeStoreAPI with realistic e-commerce data.
In production, swap fetch_* functions with real HTTP calls to:
  https://fakestoreapi.com/products
  https://fakestoreapi.com/users
  https://fakestoreapi.com/carts
Same JSON schema is maintained exactly.
"""

import random
from datetime import datetime, timedelta

random.seed(42)

CATEGORIES = ["electronics", "jewelery", "men's clothing", "women's clothing"]

PRODUCTS_RAW = [
    {"id":1,"title":"Fjallraven - Foldsack No. 1 Backpack","price":109.95,"description":"Your perfect pack for everyday use and walks in the forest.","category":"men's clothing","rating":{"rate":3.9,"count":120}},
    {"id":2,"title":"Mens Casual Premium Slim Fit T-Shirts","price":22.3,"description":"Slim-fitting style, contrast raglan long sleeve, three-button henley placket.","category":"men's clothing","rating":{"rate":4.1,"count":259}},
    {"id":3,"title":"Mens Cotton Jacket","price":55.99,"description":"Great outerwear jackets for Spring/Autumn/Winter, suitable for many occasions.","category":"men's clothing","rating":{"rate":4.7,"count":500}},
    {"id":4,"title":"Mens Casual Slim Fit","price":15.99,"description":"The color could be slightly different between on the screen and in practice.","category":"men's clothing","rating":{"rate":2.1,"count":430}},
    {"id":5,"title":"John Hardy Women's Legends Naga Gold & Silver Dragon Bracelet","price":695.0,"description":"From our Legends Collection, the Naga was inspired by the mythical water dragon.","category":"jewelery","rating":{"rate":4.6,"count":400}},
    {"id":6,"title":"Solid Gold Petite Micropave","price":168.0,"description":"Satisfaction Guaranteed. Return or exchange any order within 30 days.","category":"jewelery","rating":{"rate":3.9,"count":70}},
    {"id":7,"title":"White Gold Plated Princess","price":9.99,"description":"Classic Created Wedding Engagement Solitaire Diamond Promise Ring.","category":"jewelery","rating":{"rate":3.0,"count":400}},
    {"id":8,"title":"Pierced Owl Rose Gold Plated Stainless Steel Double","price":10.99,"description":"Rose Gold Plated Double Flared Tunnel Plug Earrings.","category":"jewelery","rating":{"rate":1.9,"count":100}},
    {"id":9,"title":"WD 2TB Elements Portable External Hard Drive","price":64.0,"description":"USB 3.0 and USB 2.0 Compatibility Fast data transfers.","category":"electronics","rating":{"rate":3.3,"count":203}},
    {"id":10,"title":"SanDisk SSD PLUS 1TB Internal SSD","price":109.0,"description":"Easy upgrade for faster boot up, shutdown, load times.","category":"electronics","rating":{"rate":2.9,"count":470}},
    {"id":11,"title":"Silicon Power 256GB SSD","price":109.0,"description":"3D NAND flash are applied to deliver high transfer speeds.","category":"electronics","rating":{"rate":4.8,"count":319}},
    {"id":12,"title":"WD 4TB Gaming Drive","price":114.0,"description":"Expand your PS4 gaming experience, Play anywhere.","category":"electronics","rating":{"rate":4.8,"count":400}},
    {"id":13,"title":"Acer SB220Q bi 21.5 inches Full HD (1920 x 1080) IPS Ultra-Thin","price":599.0,"description":"21. 5 inches Full HD (1920 x 1080) widescreen IPS display.","category":"electronics","rating":{"rate":2.9,"count":250}},
    {"id":14,"title":"Samsung 49-Inch CHG90 144Hz Curved Gaming Monitor","price":999.99,"description":"49 INCH SUPER ULTRAWIDE: 32:9 ratio screen.","category":"electronics","rating":{"rate":2.2,"count":140}},
    {"id":15,"title":"BIYLACLESEN Women's 3-in-1 Snowboard Jacket","price":56.99,"description":"Note: The Jackets is US standard size, Please choose size as your usual wear.","category":"women's clothing","rating":{"rate":2.6,"count":235}},
    {"id":16,"title":"Lock and Love Women's Removable Hooded Faux Leather Moto Biker Jacket","price":29.95,"description":"100% POLYURETHANE(shell) 100% POLYESTER(lining).","category":"women's clothing","rating":{"rate":2.9,"count":340}},
    {"id":17,"title":"Rain Jacket Women Windbreaker Striped Climbing Raincoats","price":39.99,"description":"Lightweight perfect for trip or casual wear.","category":"women's clothing","rating":{"rate":3.8,"count":679}},
    {"id":18,"title":"MBJ Women's Solid Short Sleeve Boat Neck V","price":9.85,"description":"95% RAYON 5% SPANDEX, Made in USA or Imported.","category":"women's clothing","rating":{"rate":4.7,"count":130}},
    {"id":19,"title":"Opna Women's Short Sleeve Moisture Tunic","price":7.95,"description":"100% Polyester, Machine wash, 100% Polyester.","category":"women's clothing","rating":{"rate":4.5,"count":146}},
    {"id":20,"title":"DANVOUY Womens T Shirt Casual Cotton Short","price":12.99,"description":"95% COTTON, 5% SPANDEX. If you like loose, you can choose one size larger.","category":"women's clothing","rating":{"rate":3.6,"count":145}},
]

def _random_date(start_days_ago=365):
    start = datetime.now() - timedelta(days=start_days_ago)
    delta = timedelta(days=random.randint(0, start_days_ago))
    return (start + delta).strftime("%Y-%m-%dT%H:%M:%S")

USERS_RAW = [
    {"id":1,"email":"john.doe@gmail.com","username":"johnd","password":"m38rmF$","name":{"firstname":"john","lastname":"doe"},"address":{"city":"kilsyth","street":"7835 new road","number":3,"zipcode":"12926-3874","geolocation":{"lat":"-37.3159","long":"81.1496"}},"phone":"1-570-236-7033"},
    {"id":2,"email":"morrison@gmail.com","username":"mor_2314","password":"83r5^_","name":{"firstname":"david","lastname":"morrison"},"address":{"city":"killsyth","street":"7267 cather permit","number":7,"zipcode":"12915-1619","geolocation":{"lat":"-37.3159","long":"81.1496"}},"phone":"1-570-236-7033"},
    {"id":3,"email":"kate@gmail.com","username":"kevinryan","password":"kfejgklfa","name":{"firstname":"kate","lastname":"hale"},"address":{"city":"Cullman","street":"76 main st","number":86,"zipcode":"29567-1452","geolocation":{"lat":"40.3467","long":"-30.1310"}},"phone":"1-567-094-1345"},
    {"id":4,"email":"derek@gmail.com","username":"derekhaven","password":"asdfc109$","name":{"firstname":"derek","lastname":"haven"},"address":{"city":"San Antonio","street":"42 park road","number":5,"zipcode":"12924-3867","geolocation":{"lat":"34.3516","long":"-86.2757"}},"phone":"1-699-370-4989"},
    {"id":5,"email":"miriam@gmail.com","username":"miriam_27","password":"bajkfm&&","name":{"firstname":"miriam","lastname":"telloli"},"address":{"city":"El Paso","street":"835 dolores st","number":5,"zipcode":"98234-1734","geolocation":{"lat":"38.0980","long":"22.2990"}},"phone":"1-858-452-5634"},
    {"id":6,"email":"david_42@gmail.com","username":"david42","password":"FSmk2#k","name":{"firstname":"david","lastname":"cummings"},"address":{"city":"New York","street":"1709 mulberry ln","number":8,"zipcode":"10280","geolocation":{"lat":"40.7128","long":"-74.0060"}},"phone":"1-234-516-9381"},
    {"id":7,"email":"madison@gmail.com","username":"madison","password":"9ajfm&&","name":{"firstname":"madison","lastname":"dolan"},"address":{"city":"Los Angeles","street":"456 sunset blvd","number":12,"zipcode":"90028","geolocation":{"lat":"34.0522","long":"-118.2437"}},"phone":"1-213-998-4321"},
    {"id":8,"email":"william@gmail.com","username":"williamLee","password":"W1lk##m","name":{"firstname":"william","lastname":"lee"},"address":{"city":"Chicago","street":"222 n clark st","number":1,"zipcode":"60601","geolocation":{"lat":"41.8781","long":"-87.6298"}},"phone":"1-312-888-9374"},
    {"id":9,"email":"emily_rose@gmail.com","username":"em_rose","password":"Em1234!","name":{"firstname":"emily","lastname":"rose"},"address":{"city":"Houston","street":"100 main st","number":3,"zipcode":"77002","geolocation":{"lat":"29.7604","long":"-95.3698"}},"phone":"1-713-445-2231"},
    {"id":10,"email":"carlos_v@gmail.com","username":"carlosv","password":"C@rlos1!","name":{"firstname":"carlos","lastname":"vega"},"address":{"city":"Phoenix","street":"300 e washington","number":10,"zipcode":"85004","geolocation":{"lat":"33.4484","long":"-112.0740"}},"phone":"1-602-774-3312"},
]

CARTS_RAW = [
    {"id":1,"userId":1,"date":_random_date(),"products":[{"productId":1,"quantity":4},{"productId":2,"quantity":1},{"productId":3,"quantity":6}]},
    {"id":2,"userId":1,"date":_random_date(),"products":[{"productId":2,"quantity":2},{"productId":9,"quantity":1}]},
    {"id":3,"userId":2,"date":_random_date(),"products":[{"productId":1,"quantity":1},{"productId":5,"quantity":2}]},
    {"id":4,"userId":3,"date":_random_date(),"products":[{"productId":7,"quantity":1},{"productId":8,"quantity":1},{"productId":14,"quantity":2}]},
    {"id":5,"userId":4,"date":_random_date(),"products":[{"productId":3,"quantity":1},{"productId":13,"quantity":3}]},
    {"id":6,"userId":5,"date":_random_date(),"products":[{"productId":5,"quantity":1},{"productId":6,"quantity":2}]},
    {"id":7,"userId":6,"date":_random_date(),"products":[{"productId":10,"quantity":2},{"productId":11,"quantity":1},{"productId":12,"quantity":1}]},
    {"id":8,"userId":7,"date":_random_date(),"products":[{"productId":15,"quantity":1},{"productId":17,"quantity":3}]},
    {"id":9,"userId":8,"date":_random_date(),"products":[{"productId":18,"quantity":5},{"productId":19,"quantity":2},{"productId":20,"quantity":4}]},
    {"id":10,"userId":9,"date":_random_date(),"products":[{"productId":4,"quantity":2},{"productId":2,"quantity":3}]},
    {"id":11,"userId":10,"date":_random_date(),"products":[{"productId":13,"quantity":1},{"productId":14,"quantity":1}]},
    {"id":12,"userId":3,"date":_random_date(),"products":[{"productId":1,"quantity":2},{"productId":9,"quantity":1},{"productId":10,"quantity":1}]},
    {"id":13,"userId":5,"date":_random_date(),"products":[{"productId":6,"quantity":1},{"productId":7,"quantity":2},{"productId":8,"quantity":1}]},
    {"id":14,"userId":2,"date":_random_date(),"products":[{"productId":16,"quantity":2},{"productId":17,"quantity":1}]},
    {"id":15,"userId":6,"date":_random_date(),"products":[{"productId":11,"quantity":3},{"productId":12,"quantity":2}]},
]


def get_products():
    """Returns data identical to GET https://fakestoreapi.com/products"""
    return PRODUCTS_RAW

def get_users():
    """Returns data identical to GET https://fakestoreapi.com/users"""
    return USERS_RAW

def get_carts():
    """Returns data identical to GET https://fakestoreapi.com/carts"""
    return CARTS_RAW
