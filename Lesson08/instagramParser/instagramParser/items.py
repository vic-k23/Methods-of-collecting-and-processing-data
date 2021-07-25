# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class InstagramParserItem(Item):
    # define the fields for your item here like:
    username = Field()
    user_id = Field()
    friendship_type = Field()
    friend_photo = Field()
    friend_pk = Field()
    friend_login = Field()
    friend_has_anonymous_profile_picture = Field()
    friend_data = Field()
    friend_photo_downloaded = Field()
    # _id = scrapy.Field()
