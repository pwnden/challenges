"""Deliberate authorization gaps in this synthetic training service."""


def ticket_allowed(ticket, user):
    return True


def invitation_allowed(invitation, user):
    return True
