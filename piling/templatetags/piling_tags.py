from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Allow dict[key] access in templates: {{ my_dict|get_item:key }}"""
    return dictionary.get(key, "")


@register.filter
def index(lst, item):
    """Return index of item in list: {{ my_list|index:item }}"""
    try:
        return lst.index(item)
    except (ValueError, AttributeError):
        return -1
