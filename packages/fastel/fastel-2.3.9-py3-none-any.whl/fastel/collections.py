from typing import Any, Dict, Optional, Union

from pymongo.collection import Collection

product_collection: Collection = None
coupon_collection: Collection = None
discount_collection: Collection = None
user_collection: Collection = None
user_profile_collection: Collection = None
private_profile_collection: Collection = None
cart_collection: Collection = None
site_collection: Collection = None
checkout_collection: Collection = None
order_collection: Collection = None
counter_collection: Collection = None


def set_collections(
    product: Collection,
    coupon: Collection,
    discount: Collection,
    user: Collection,
    user_profile: Collection,
    private_profile: Collection,
    cart: Collection,
    site: Collection,
    checkout: Collection,
    order: Optional[Collection] = None,
    counter: Optional[Collection] = None,
) -> None:
    global product_collection
    global coupon_collection
    global discount_collection
    global user_collection
    global user_profile_collection
    global private_profile_collection
    global cart_collection
    global site_collection
    global checkout_collection
    global order_collection
    global counter_collection
    product_collection = product
    coupon_collection = coupon
    discount_collection = discount
    user_collection = user
    user_profile_collection = user_profile
    private_profile_collection = private_profile
    cart_collection = cart
    site_collection = site
    checkout_collection = checkout
    order_collection = order
    counter_collection = counter


def get_collection(name: str) -> Collection:
    if name == "product":
        return product_collection
    if name == "coupon":
        return coupon_collection
    if name == "discount":
        return discount_collection
    if name == "user":
        return user_collection
    if name == "cart":
        return cart_collection
    if name == "user_profile":
        return user_profile_collection
    if name == "private_profile":
        return private_profile_collection
    if name == "site":
        return site_collection
    if name == "checkout":
        return checkout_collection
    if name == "order":
        return order_collection
    if name == "counter":
        return counter_collection


def get_site_config_doc() -> Union[Dict[str, Any], None]:
    if site_collection is None:
        return None
    return site_collection.find_one({"name": "config"})  # type: ignore


def get_site_config(key: str, default: Any = None) -> Any:
    config_doc = get_site_config_doc()
    if config_doc is None:
        return default
    return config_doc.get(key, default)
