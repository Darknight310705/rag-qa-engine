# OAuth 2.0 Authorization Framework

OAuth 2.0 is an authorization framework that enables a third-party application to obtain limited access to a user's resources on another service, without exposing the user's credentials to that third-party application. It is fundamentally about authorization -- granting access to resources -- not authentication, which is a common point of confusion; OpenID Connect is built on top of OAuth 2.0 specifically to add an authentication layer.

The authorization code flow is the most common grant type for server-side web applications: the user is redirected to the authorization server to log in and consent, the authorization server redirects back with a short-lived authorization code, and the application's backend exchanges that code for an access token via a direct server-to-server request, keeping the token out of the browser.

The client credentials grant is used for machine-to-machine authentication where no user is involved, such as a backend service calling another backend service. Access tokens are typically short-lived and scoped to specific permissions, while refresh tokens allow obtaining new access tokens without repeating the full authorization flow.

PKCE (Proof Key for Code Exchange) was added to protect the authorization code flow for public clients like mobile and single-page apps, which cannot securely store a client secret, by having the client generate a temporary secret verified at token exchange time.
