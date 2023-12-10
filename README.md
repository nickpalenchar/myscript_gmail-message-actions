# myscript_gmail-message-actions
Script that deletes old messages according to time-based labels

This is a `myscript_` repo. See [Special prefixes in my workspace](https://github.com/nickpalenchar/nickpalenchar/tree/main#special-prefixes-in-my-workspace) for more info.

## Secrets
Create a secrets directory.

- `secrets/client_secret.json` - used for google. Auto-generated on first run
- `secrets/twilio.json` - credentials for twilio

```
{
  "account_sid": "",
  "auth_token": "",
  "twilio_phone_number": ""
}
```

get these from https://console.twilio.com/

## Dependencies

Google Cloud Console:
- project:`gmail bot - personal`
- org: my email
