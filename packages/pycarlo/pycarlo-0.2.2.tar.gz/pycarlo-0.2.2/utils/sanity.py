from utils.vars import ensure_token_env_vars, ensure_endpoint_env_var
from pycarlo.core import Session, Client, Query, Mutation

CONFIRMATION_ICON = '✔️'
CONFIRMATION_SEPARATOR = '='


def test_with_query(client: Client):
    query = Query()
    query.get_user.__fields__('email')
    print(client(query).get_user.email)


def test_with_mutation(client: Client):
    mutation = Mutation()
    mutation.generate_collector_template(region='us-east-1')
    print(client(mutation))


def test_with_string(client: Client):
    get_table_query = """
    query getTables{
      getTables(first: 10) {
        edges {
          node {
            fullTableId
          }
        }
      }
    }
    """
    response = client(get_table_query)
    for edge in response.get_tables.edges:
        print(edge.node.full_table_id)
    print(response['get_tables']['edges'][0]['node']['full_table_id'])


def print_confirmation(text: str):
    separator = CONFIRMATION_SEPARATOR * (len(text) + 2)
    print()
    print(separator)
    print(text, CONFIRMATION_ICON)
    print(separator)
    print()


def sanity_check(mcd_url: str = None, mcd_id: str = None, mcd_token: str = None):
    session = Session(endpoint=mcd_url, mcd_id=mcd_id, mcd_token=mcd_token)
    client = Client(session=session)

    test_with_query(client=client)
    print_confirmation("running queries with Query object")

    test_with_mutation(client=client)
    print_confirmation("running queries with Mutation object")

    test_with_string(client=client)
    print_confirmation("running queries with string")


if __name__ == '__main__':
    api_id, api_token = ensure_token_env_vars()
    api_url = ensure_endpoint_env_var()
    sanity_check(mcd_url=api_url, mcd_id=api_id, mcd_token=api_token)
