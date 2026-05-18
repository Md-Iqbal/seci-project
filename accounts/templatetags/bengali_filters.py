"""
Bengali Template Filters
Custom template filters for Bengali formatting
"""

from django import template
from accounts.utils.bengali_utils import (
    to_bengali_number,
    format_bengali_currency,
    format_bengali_date,
    format_bengali_datetime,
    get_status_bengali,
    get_account_type_bengali,
    get_gender_bengali
)

register = template.Library()

@register.filter
def bengali_number(value):
    """Convert number to Bengali"""
    return to_bengali_number(value)

@register.filter
def bengali_currency(value):
    """Format currency in Bengali"""
    return format_bengali_currency(value)

@register.filter
def bengali_date(value):
    """Format date in Bengali"""
    return format_bengali_date(value)

@register.filter
def bengali_datetime(value):
    """Format datetime in Bengali"""
    return format_bengali_datetime(value)

@register.filter
def status_bengali(value):
    """Get status in Bengali"""
    return get_status_bengali(value)

@register.filter
def account_type_bengali(value):
    """Get account type in Bengali"""
    return get_account_type_bengali(value)

@register.filter
def gender_bengali(value):
    """Get gender in Bengali"""
    return get_gender_bengali(value)