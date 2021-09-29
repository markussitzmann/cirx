from django import template

register = template.Library()

@register.filter(name='beautify2')
def beautify2(value):
	return 'blu'



#beautify = register.filter('beautify', beautify)