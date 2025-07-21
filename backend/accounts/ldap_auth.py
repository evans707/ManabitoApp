from ldap3 import Server, Connection, ALL, Tls
import ssl
import os
import dotenv
import logging

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


def authenticate_with_ldap(university_id, password):
    LDAP_SERVER = os.getenv('LDAP_SERVER')
    LDAP_BASE_DN = 'ou=People,dc=dendai,dc=ac,dc=jp'

    server = Server(LDAP_SERVER, get_info=ALL)

    try:
        with Connection(server) as conn:
            search_filter = f'(uid={university_id})'

            found = conn.search(search_base=LDAP_BASE_DN,
                                search_filter=search_filter,
                                attributes=['uid'])

            if not found or not conn.entries:
                logger.warning(f"LDAP search failed: User '{university_id}' not found.")
                return False

            user_dn = conn.entries[0].entry_dn
            logger.info(f"Found user DN: {user_dn}")

        with Connection(server, user=user_dn, password=password) as auth_conn:
            if auth_conn.bound:
                logger.info('LDAP Authentication successful.')
                return True
            else:
                logger.warning(f"LDAP bind failed for user '{user_dn}'. Result: {auth_conn.result}")
                return False

    except Exception as e:
        logger.error(f"An unexpected LDAP error occurred: {e}")
        return False