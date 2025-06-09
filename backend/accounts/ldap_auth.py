from ldap3 import Server, Connection, ALL, NTLM

# ldap認証(仮)
def authenticate_with_ldap(university_id, password):
    LDAP_SERVER = 'ldap://your.ldap.server'
    LDAP_BASE_DN = 'dc=example,dc=edu'
    USER_DN_TEMPLATE = f"uid={university_id},{LDAP_BASE_DN}"

    server = Server(LDAP_SERVER, get_info=ALL)
    try:
        conn = Connection(server, user=USER_DN_TEMPLATE, password=password)
        if conn.bind():
            return True
    except Exception as e:
        print(f"LDAP error: {e}")
    return False
