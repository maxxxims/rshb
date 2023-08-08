from parser_model import Parser
import os


groups = {'svoe_rodnoe': 'svoerodnoe.rshb', 'esh_derevenskoe': 'eshderevenskoe', 'agromp': 'agromp'}


def GET_TOKEN() -> str:
    return os.getenv('VK_TOKEN')


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
        # print(len(parser.get_users()))
        # print(len(parser.get_users_groups()))
    parser.parse_user_info(n_users='all')

        
def parse_all(parser: Parser):
    parser.parse_all_groups(groups)


def find_common_groups(parser: Parser, path_to_file: str):
    parser.load_users(path_to_file)
    parser.parse_common_groups()
    parser.save_counter(path_to_file='output_data/counter_2.csv')


def get_top_common_groups(parser: Parser):
    parser.merge_common_groups(groups = ['output_data/counter_2.csv', 'output_data/counter_23.csv'])
    parser.get_most_common_groups(limit=20, save_file=True)


def get_top_groups_types(parser: Parser):
    #parser.merge_common_groups(groups = ['output_data/counter_2.csv', 'output_data/counter_23.csv'])
    parser.load_counter('output_data/counter_all.csv')
    parser.get_groups_types()


def load_counter(parser: Parser, path_to_file: str):
    parser.load_counter(path_to_file)
    cnt = parser.get_counter()


if __name__ == '__main__':
    token = GET_TOKEN()
    parser = Parser(token)
    #parse_list_of_groups(parser, group_list=[groups['svoe_rodnoe'], groups['agromp'], groups['esh_derevenskoe']])

    #find_common_groups(parser, path_to_file='data_analysis/users_all2.csv') #
    
    
    get_top_common_groups(parser)
    #get_top_groups_types(parser)

    #load_counter(parser, path_to_file='output_data/counter.csv')
    #parser.save_df(path='data_analysis/users_all2.csv')