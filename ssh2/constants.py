SSH_CONFIG = "~/.ssh/config"

STRING  = 1
INTEGER = 2
BOOLEAN = 3
SOCKS   = 4

CONFIG_KEY_MAPPING = (
    ("hostname", "hostname", STRING,),
    ("port", "port", INTEGER,),
    ("user", "username", STRING,),
    ("identityfile", "key_filename", STRING,),
    ("connecttimeout", "timeout", INTEGER,),
    ("forwardagent", "allow_agent", BOOLEAN,),
    ("identitiesonly", "look_for_keys", BOOLEAN,),
    ("compression", "compress", BOOLEAN,),
    ("gssapiauthentication", "gss_auth", BOOLEAN,),
    ("gssapikeyexchange", "gss_kex", BOOLEAN,),
    ("gssapidelegatecredentials", "gss_deleg_creds", BOOLEAN),
    ("proxycommand", "sock", SOCKS)
)