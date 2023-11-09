# Shibboleth Emulator

A reverse proxy that emulates a Shibboleth Service Provider (SP) during development.

## Usage

### Configuration

Open `config.py`

- Set HOST and PORT to the host and port you want the emulator to listen on. "0.0.0.0" refers to all interfaces. 7777 is
  the default port.
- Set PASSTHROUGH_URL to the URL of your application without a trailing slash. For example, "http://localhost:8080".
- Optionally enable EMULATE_HOST and configure the EMULATE_HOST_VALUE if you want a custom HOST header to be sent to
  your application.
- Optionally enable REPLACE_URLS to replace the body content of responses with the emulator's URL. For example, if your
  application returns a URL like "http://localhost:8080/some/path", the emulator will replace it with
  "http://localhost:7777/some/path".
- Set SHIBBOLETH_PATHS to all the paths where the emulator should emulate Shibboleth. For
  example, `["/portal/api/login/", "/auth/users/auth/shibboleth/callback"]`
- Configure SHIBBOLETH_HEADERS with the default headers you want the emulator to inject into your application. You'll be
  able to override these during runtime, but the keys need to be specified for the front-end to be generated.

### Running

Run `shibboleth-emulator.py` on your host machine. Run your application hosted at PASSTHROUGH_URL. Connect to the host
and port you specified. Most requests will be passed directly to your application. When you request a Shibboleth path,
the emulator will intercept the request and ask you to provide the Shibboleth headers. The emulator will then forward
the request to your application with the Shibboleth headers injected.

## Screenshot

![image](https://github.com/NicholasMy/shibboleth-emulator/assets/32116122/b7aa2650-cbdd-4596-a74f-6a7310326ff2)

When accessing a path specified in SHIBBOLETH_PATHS, you'll see this interception page. The fields are dynamically
generated based on your SHIBBOLETH_HEADERS configuration.

