from django import template

register = template.Library()

@register.simple_tag(takes_context=False)
def ordinal(num):
    return "%d%s" % (num,"tsnrhtdd"[(num//10%10!=1)*(num%10<4)*num%10::4])