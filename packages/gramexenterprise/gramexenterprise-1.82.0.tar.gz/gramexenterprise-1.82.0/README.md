# Gramex Enterprise Edition

Install the [enterprise edition of Gramex](https://learn.gramener.com/guide/):

```bash
pip install gramexenterprise
```

[Read the documentation for details](https://learn.gramener.com/guide/)


## Changelog

### 1.82.0

- BUG: Allow OTP to use databases
- BUG: Save redirect information for SAMLAuth2
- ENH: Add recaptcha to SMS template

### 1.76.0

- FIX: EmailAuth supports recaptcha: and delay
- FIX: Remove HTTP reason, add ldap dependency

### 1.74.0

- ENH: EmailAuth support html emails and bypasses Outlook safelinks
- ENH: EmailAuth supports direct entry of OTP
- BUG: EmailAuth: if user refreshes OTP page, preserve next page
- ENH: DBAuth forgot-email accepts text/html content/files
- BUG: DBAuth uses 'email' as default email column
- ENH: SAMLAuth2 handler supporting SAML2 @vinay.ranjan
- ENH: Support password policy
- SEC: Slow down username enumeration

### 1.65.0

- DBAuth: remove `table` as an explicit kwarg. It is not required for files, and will fail for
  non-Excel files from Gramex CE 1.65.0 onwards.
- Auth: When Gramex is behind a proxy, use `handler.xredirect_uri` to redirect to the end-user URL,
  not the proxied URL (which would be `localhost:port`).

### 1.56.1

- DBAuth: `reset_url` should be ?forgot key

### 1.56.0

- DBAuth: extend signup to configure email like forgot configuration
