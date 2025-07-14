from ldap3 import Server, Connection, ALL
from ldap3.core.tls import Tls
import ssl
import os
import dotenv
import logging

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

def authenticate_with_ldap(university_id, password):
    LDAP_SERVER = os.getenv('LDAP_SERVER')
    LDAP_BASE_DN = 'ou=People,dc=dendai,dc=ac,dc=jp'

    # USER_DN_TEMPLATE = f'uid={university_id},{LDAP_BASE_DN}'

    logger.info('LDAP Authentication Started.')

    # tls_config = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)

    server = Server(LDAP_SERVER, use_ssl=False, tls=None, get_info=ALL)

    try:
        conn = Connection(server, auto_bind=True)

        search_filter = f'(uid={university_id})'

        conn.search(search_base=LDAP_BASE_DN,
                   search_filter=search_filter,
                   attributes=['dn'])

        if conn.entries:
            user_dn = conn.entries[0].dn
            auth_conn = Connection(server, user=user_dn, password=password)
        if auth_conn.bind():
            logger.info('LDAP Authentication successful.')
            return True
    except Exception as e:
        logger.error(f"LDAP error: {e}")

    return False
