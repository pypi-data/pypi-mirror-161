from askdata import Askdata
from askdata.human2query import smartner
import time

if __name__ == "__main__":

    username = "g.vaccaro@askdata.com"
    password = ""

    # Login
    user = Askdata(username=username, password=password, domainlogin="askdata", env="dev")
    token = user.get_token()

    # Get datasets
    workspace = "20220104_mysql_test"
    agent = user.agent(slug=workspace)
    df_datasets = agent.list_datasets()
    datasets = df_datasets['id'].values.tolist()

    # Usage
    nl = "revenue per restaurants"

    start = time.time()
    smartquery_list = smartner(nl, token=token, workspace=workspace, datasets=datasets, language="en-US")
    end = time.time()
    for sq in smartquery_list:
        print(sq)
        print()

    print("Time: ", end-start, "s")
