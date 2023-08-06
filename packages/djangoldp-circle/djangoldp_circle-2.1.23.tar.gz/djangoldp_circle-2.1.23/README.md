# Synopsis

Circles represent groups of people, and can optionally support a chat mechanic in co-operation with XMPP

# Permissions on Circles

Standard Circles can be **Public**, **Private** or **Archived**

Anonymous users can view public circles

Authenticated users can view public circles and add to them. You can change this in the settings :
```
# default value :
USER_AUTHENTICATED_CIRCLE_PERMISSIONS=['view', 'add']
# use this to prevent user to create new circles (except if they are superusers):
USER_AUTHENTICATED_CIRCLE_PERMISSIONS=['view']
```

If a user is a **member** of a private circle (they have been added by another member, or the circle's creator), then they can view the circle, and add to it

If a member is an **admin** of a circle then they can change information about the circle and delete it. They can add other users as administrators, or delete members, but they can't delete other administrators, or delete themselves if they are the last administrator

Circles can also be **Restricted**, which makes them Private circles which a user can request access to. When an administrator accepts their request, they will be added to the circle membership

As with all DjangoLDP models, individual users may also be given permissions individually on circles

## Allow XMPP server to access private datas

By default, our Prosody server is allowed to access any Circle information, for membership purpose. You can set it to your own server by adding `XMPP_SERVER_IP` to your packages.yml.
