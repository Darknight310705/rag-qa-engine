# JWT Authentication

JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties. A JWT consists of three parts separated by dots: a header, a payload, and a signature. The header typically specifies the signing algorithm, such as HS256 or RS256.

The payload contains claims, statements about an entity (typically the user), plus additional metadata. Common claims include "sub" for subject, "exp" for expiration time, and "iat" for issued-at time. The signature is created by encoding the header and payload and signing them with a secret or private key, ensuring the token has not been tampered with.

Unlike session-based authentication, JWTs are stateless: the server does not need to store session data, since all necessary information is encoded in the token itself. This makes JWTs well-suited for distributed systems and microservices, but it also means revoking a JWT before its expiration requires additional mechanisms like a token blacklist.

Refresh tokens are commonly used alongside short-lived access tokens: the access token is used for API requests and expires quickly, while the longer-lived refresh token is used to obtain new access tokens without requiring the user to log in again.
