Introduction
============

collective.inviting is an add-on for Plone that manages event invitations, 
confirmations, and attendance as stored, indexed relationships between
users (members or guests) and event content items in a Plone site.

This package provides the following features:

 * Allow event content owners to manage invitations and retrospectively
   track attendance and confirmations (RSVPs).

 * Email invitations including iCal, vCal attachments and links to
   return to the event to confirm/RSVP.

 * Support both site members and guests (identifying with email) as 
   parties who can be invited.

 * Builds upon collective.subscribe, a general purpose set of components
   for managing user relationships ("subscriptions") with content.

 * Users can change their confirmation status by re-visiting the
   confirmation link.

 * A simple hash/token is included in emailed URLs to prevent abuse.

 * Provides utility and adapter registrations for components in
   collective.subscribe for use in a Plone site.

Depends on collective.subscribe.

--

Author: Sean Upton <sean.upton@hsc.utah.edu>

Copyright 2011, The University of Utah.

Released as free software under the GNU GPL version 2 license.
See doc/COPYING.txt

