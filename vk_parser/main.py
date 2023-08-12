from parser_model import Parser
from utils import GET_TOKEN


groups = {'svoe_rodnoe': 'svoerodnoe.rshb', 'esh_derevenskoe': 'eshderevenskoe', 
          'agromp': 'agromp', 'tvoy_product': 'tvoyproduct', 'm2-organic': 'organicferma',
          'eco_lakomka': 'eco_lakomka', 'fermermag': 'fermermag', 'ecomarket': 'ecomarket_russia',
          'apeti': 'apeti_moscow', }


def parse_one_group(parser: Parser, group_name: str):
    parser.set_group(groups[group_name])
    parser.parse_users_from_group(test=False)
    print(len(parser.get_users()))
    print(len(parser.get_users_groups()))
    parser.parse_user_info(n_users=1)


def parse_list_of_groups(parser: Parser, group_list: list):
    for group in group_list:
        parser.set_group(group)
        parser.parse_users_from_group(test=False)
    parser.parse_user_info(n_users='all')
    parser.save_df('all_users.csv')
        

def parse_all(parser: Parser):
    parser.parse_all_groups(groups)


def find_common_groups(parser: Parser, path_to_file: str):
    parser.load_users(path_to_file)
    parser.parse_common_groups()
    parser.save_counter(path_to_file='output_data/counter.csv')


def get_top_common_groups(parser: Parser, save_file: bool = True):
    #parser.merge_common_groups(groups = ['output_data/counter_2.csv', 'output_data/counter_23.csv'])
    parser.get_most_common_groups(limit=20, save_file=save_file)


def get_top_groups_types(parser: Parser):
    #parser.merge_common_groups(groups = ['output_data/counter_2.csv', 'output_data/counter_23.csv'])
    parser.load_counter('output_data/counter.csv')
    parser.get_groups_types()


def load_counter(parser: Parser, path_to_file: str):
    parser.load_counter(path_to_file)
    cnt = parser.get_counter()


if __name__ == '__main__':
    token = GET_TOKEN()
    parser = Parser(token)
    #parse_list_of_groups(parser, [groups['m2-organic'], groups['eco_lakomka'], groups['fermermag'], groups['ecomarket'], groups['apeti']])
    #get_top_groups_types(parser)
    #parser.save_df(path='data_analysis/all_users.csv')
    
    find_common_groups(parser, path_to_file='data_analysis/all_users_end.csv') #
    get_top_common_groups(parser, save_file=True)


    #load_counter(parser, path_to_file='output_data/counter.csv')
    