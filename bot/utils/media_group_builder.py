from aiogram.types import InputMediaPhoto, InputMediaDocument
from aiogram.utils.media_group import MediaGroupBuilder


def get_media_group_builders(
    media_elements: list[str], media_type: str
) -> list[list[InputMediaPhoto | InputMediaDocument]]:
    lists_media_elements = []
    for index in range(0, len(media_elements), 10):
        sublist = media_elements[index : index + 10]
        lists_media_elements.append(sublist)

    media_groups = []

    for elements in lists_media_elements:
        media_group = MediaGroupBuilder()
        for element in elements:
            if media_type == "photo":
                media_group.add_photo(element)
            elif media_group == "file":
                media_group.add_document(element)
        media_groups.append(media_group.build())
    return media_groups
