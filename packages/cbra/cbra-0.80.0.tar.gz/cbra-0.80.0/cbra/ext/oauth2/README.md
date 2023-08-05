# OAuth 2.0 Server

An OAuth 2.0 server based on the `cbra` framework.


# Extensions

The `cbra.ext.oauth2` implementation provides additional extensions to the
OAuth 2.0 standard.

## Client configuration

### `consent_url`

Specifies the URL at which consent may be obtained. The authorization server
redirects to this URL with the followin query parameters:

- `client_id` - The OAuth 2.0 client requesting access.
- `redirect_uri` - The redirection URI specified by an authorization request,
  or the default set by the client if one was not provided. The service is
  expecred to redirect to this URL if the resource owner cancels the flow. It
  must be whitelisted by the client.
- `scope` - The requested scope as specified by the authorization request.
- `authorize` - The original URL that where the authorization request was
  made. If the user consents, then the consent service is expected to
  redirect back to there.
