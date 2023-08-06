from typing import Any, List

from eevend_libs.client.base_client import BaseClient

service_name = "eev-catalogue-service"


class CatalogueClient(BaseClient):

    def __init__(self) -> None:
        super().__init__(service_name)

    def get_categories(self) -> Any:
        return self.get('categories')

    def get_product(self, product_id: int) -> Any:
        return self.get('product/%s' % product_id)

    def add_product(self,
                    product_title: str,
                    product_description: str,
                    product_quantity: int,
                    product_price: float,
                    product_price_currency_id: int,
                    seller_id: int,
                    sub_category_id: int,
                    product_link_or_hash: str,
                    product_is_downloadable: bool,
                    product_is_viewable: bool,
                    product_format_id: int) -> Any:
        return self.post('product',
                         product_title=product_title,
                         product_description=product_description,
                         product_quantity=product_quantity,
                         product_price=product_price,
                         product_price_currency_id=product_price_currency_id,
                         seller_id=seller_id,
                         sub_category_id=sub_category_id,
                         product_link_or_hash=product_link_or_hash,
                         product_is_downloadable=product_is_downloadable,
                         product_is_viewable=product_is_viewable,
                         product_format_id=product_format_id)

    def edit_product(self,
                     product_id: int,
                     product_title: str,
                     product_description: str,
                     product_quantity: int,
                     product_is_pre_order: bool,
                     product_is_active: bool,
                     product_price: float,
                     product_price_currency_id: int,
                     seller_id: int,
                     sub_category_id: int,
                     product_link_or_hash: str,
                     product_is_downloadable: bool,
                     product_is_viewable: bool, ) -> Any:
        return self.put('product',
                        product_id=product_id,
                        product_title=product_title,
                        product_description=product_description,
                        product_quantity=product_quantity,
                        product_is_pre_order=product_is_pre_order,
                        product_is_active=product_is_active,
                        product_price=product_price,
                        product_price_currency_id=product_price_currency_id,
                        seller_id=seller_id,
                        sub_category_id=sub_category_id,
                        product_link_or_hash=product_link_or_hash,
                        product_is_downloadable=product_is_downloadable,
                        product_is_viewable=product_is_viewable, )

    def add_product_discount(self,
                             product_id: int,
                             product_discount_name: str,
                             product_discount_description: str,
                             product_discount_percentage: int,
                             product_discount_quantity: int,
                             product_discount_user_modified_email: str, ) -> Any:
        return self.post('product/discount',
                         product_id=product_id,
                         product_discount_name=product_discount_name,
                         product_discount_description=product_discount_description,
                         product_discount_percentage=product_discount_percentage,
                         product_discount_quantity=product_discount_quantity,
                         product_discount_user_modified_email=product_discount_user_modified_email, )

    def get_tags(self) -> Any:
        return self.get('tags')

    def edit_product_tags(self,
                          product_id: int,
                          product_tags: List[int], ) -> Any:
        return self.put('product/tags',
                        product_id=product_id,
                        product_tags=product_tags, )

    def get_formats(self) -> Any:
        return self.get('formats')

    def get_products(self,
                     categories: [int] = None,
                     on_sale: bool = None,
                     page_size: int = None,
                     page_number: int = None,
                     order_by: str = None,
                     sort_direction: str = None,) -> Any:
        return self.post('products',
                         categories=categories,
                         on_sale=on_sale,
                         page_size=page_size,
                         page_number=page_number,
                         order_by=order_by,
                         sort_direction=sort_direction,)


class CartWishlistClient(BaseClient):

    def __init__(self) -> None:
        super().__init__(service_name)

    def get_user_cart(self, user_id: int) -> Any:
        return self.get('cart/%s' % user_id)

    def get_user_wishlist(self, user_id: int) -> Any:
        return self.get('wishlist/%s' % user_id)

    def add_user_cart_item(self,
                           user_id: int,
                           product_id: int,
                           cart_item_quantity: int, ) -> Any:
        return self.post('cart/%s' % user_id,
                         user_id=user_id,
                         product_id=product_id,
                         cart_item_quantity=cart_item_quantity, )

    def add_user_wishlist_item(self,
                               user_id: int,
                               product_id: int, ) -> Any:
        return self.post('wishlist/%s' % user_id,
                         user_id=user_id,
                         product_id=product_id, )

    def delete_user_cart_item(self, user_id: int, product_id: int) -> Any:
        return self.delete('cart/%s' % user_id, product_id=product_id)

    def delete_user_wishlist_item(self, user_id: int, product_id: int) -> Any:
        return self.delete('wishlist/%s' % user_id, product_id=product_id)

    def edit_user_cart_item(self,
                            user_id: id,
                            product_id: int,
                            cart_item_quantity: int) -> Any:
        return self.put('cart',
                        user_id=user_id,
                        product_id=product_id,
                        cart_item_quantity=cart_item_quantity)
