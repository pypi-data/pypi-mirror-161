**OAuth** (**O**pen **Auth**orization) is an internet standard that is used to grant websites and applications access to protected resources, on the authorization of the *resource owner*. It is extended by the **OpenID Connect** standards, which provide means to identify a user (*subject*) using the OAuth 2.x protocol. This server implements both the OAuth 2.x and OpenID Connect standards. The OAuth endpoints may be used to obtain a digitally signed access token to resource servers, or an identity token that holds claims about the identity of a subject.

**Error codes**

In addition to the error codes defined by the OAuth 2.x standards,
this server may respond with the following error codes:

- `invalid_origin` - The client did not accept the `Origin` header and
  refuses to respond.