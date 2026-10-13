"""Bind each read and staff invitation to the authenticated user."""


def ticket_allowed(ticket, user):
    return ticket['owner'] == user


def invitation_allowed(invitation, user):
    return invitation['recipient'] == user
