# coding: utf-8
from __future__ import unicode_literals


def generate_permissions(data):
    """
    Insert here code to generate group specific permissions
    """

    user_groups_permissions = []
    for entity in data:
        user_groups_permissions.append(
            {'group': entity[u'country'], 'reports': {'$or': [{'entityName': entity[u'country']}]}}
        )

    return user_groups_permissions
