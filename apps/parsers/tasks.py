from __future__ import absolute_import, unicode_literals

from celery import shared_task

from .olx.parser import OLXInner, OLXUpdater, update_olx_util

from apps.parsers.auto_ria.parser import AutoRiaUpdateParse, AutoRiaInnerParse


@shared_task
def inner_ria():
    AutoRiaInnerParse()
    return None


@shared_task
def upd_ria(hours):
    AutoRiaUpdateParse(hours)
    return None


@shared_task
def inner_olx():
    OLXInner()
    return None


@shared_task
def updater_olx():
    update_olx_util()
    return None
