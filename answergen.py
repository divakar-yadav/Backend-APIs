import pandas as pd
import numbers
from cachier import cachier
from termcolor import colored, cprint


def print_title(title='Title'):
    print('\n\n')
    #line = colored('▓'*78+'\n', 'magenta', attrs=['reverse'])
    line = colored('■'*78+'\n', 'magenta')
    #line = colored('*'*78+'\n', 'magenta')
    text = colored(' '*20 + title+'\n', 'yellow')
    print(line)
    print(text)
    print(line)


def get_language_with_multi_value(responses):
    nl_response = ''

    if len(responses) == 0:
        pass
    elif len(responses) == 1:
        nl_response = responses[0]
    else:
        for index, response in enumerate(responses):
            #print(response, index)
            if index == 0:
                nl_response = str(response)
            elif index == len(responses) - 1:
                nl_response = nl_response + ' and ' + str(response)
            else:
                nl_response = nl_response + ', ' + str(response)
            
    return nl_response

def get_language_with_multi_value_and_number(responses, answer_prefix, answer_suffix):
    nl_response = ''

    if len(responses) == 0:
        pass
    elif len(responses) == 1:
        nl_response = responses[0]
    else:
        for index, response in enumerate(responses):
            #print(response, index)
            if index == 0:
                nl_response = str(response[0]) + answer_prefix + str(response[1]) + answer_suffix
            elif index == len(responses) - 1:
                nl_response = nl_response + ' and '  + str(response[0]) + answer_prefix + str(response[1]) + answer_suffix
            else:
                nl_response = nl_response + ', ' +  str(response[0]) + answer_prefix + str(response[1]) + answer_suffix
            
    return nl_response

def get_language_with_multi_value_with_highlight(responses):
    nl_response = ''

    if len(responses) == 0:
        pass
    elif len(responses) == 1:
        nl_response = '<span class="answer_highlight">' + responses[0] + '</span>'
    else:
        for index, response in enumerate(responses):
            #print(response, index)
            if index == 0:
                nl_response = '<span class="answer_highlight">' + response + '</span>'
            elif index == len(responses) - 1:
                nl_response = nl_response + ' and ' + '<span class="answer_highlight">' + response + '</span>'
            else:
                nl_response = nl_response + ', ' + '<span class="answer_highlight">' + response + '</span>'
            
    return nl_response

def get_language_with_multi_value_and_number_with_highlight(responses, answer_prefix, answer_suffix):
    nl_response = ''

    highlight_tag = '<span class="answer_highlight">' 
    highlight_tag_end = '</span>'

    if len(responses) == 0:
        pass
    else:
        for index, response in enumerate(responses):
            #print(response, index)
            if index == 0:
                nl_response = highlight_tag + str(response[0]) + highlight_tag_end + answer_prefix + highlight_tag + str(response[1]) + highlight_tag_end + answer_suffix
            elif index == len(responses) - 1:
                nl_response = nl_response + ' and '  + highlight_tag + str(response[0]) + highlight_tag_end + answer_prefix + highlight_tag + str(response[1]) + highlight_tag_end + answer_suffix
            else:
                nl_response = nl_response + ', ' +  highlight_tag + str(response[0]) + highlight_tag_end + answer_prefix + highlight_tag + str(response[1]) + highlight_tag_end + answer_suffix
            
    return nl_response

def get_highlight_response(response):
    nl_response = ''
    response = str(response)
    highlight_tag = '<span class="answer_highlight">' 
    highlight_tag_end = '</span>'

    nl_response = highlight_tag + response + highlight_tag_end
    return nl_response

def create_single_column_response(df, column_name, prefix='', suffix ='.', n_answer = 3, sort_by=None, sort_asc=True, is_highlight = True):
    if sort_by:
        df = df.sort_values(by=[sort_by], ascending=sort_asc)
    df = df.head(n_answer)
    responses = df[column_name].tolist()
    nl_reponses = ''
    if is_highlight:
        nl_reponses = get_language_with_multi_value_with_highlight(responses)
    else:
        nl_reponses = get_language_with_multi_value(responses)

    final_nl_answer = prefix + nl_reponses + suffix

    print(final_nl_answer)
    return final_nl_answer

def create_multi_column_response(df, column_name_1, column_name_2, prefix='', suffix ='.', answer_suffix = '', answer_prefix = '',
    n_answer = 3, sort_by=None, sort_asc=True, is_highlight = True):
    if sort_by:
        df = df.sort_values(by=[sort_by], ascending=sort_asc)
    df = df.head(n_answer)
    responses_1 = df[column_name_1].tolist()
    responses_2 = df[column_name_2].tolist()

    responses = list(zip(responses_1, responses_2))

    nl_reponses = ''
    if is_highlight:
        nl_reponses = get_language_with_multi_value_and_number_with_highlight(responses, answer_prefix, answer_suffix)
    else:
        nl_reponses = get_language_with_multi_value_and_number(responses, answer_prefix, answer_suffix)


    final_nl_answer = prefix + nl_reponses + suffix

    print(final_nl_answer)
    return final_nl_answer


if __name__== "__main__":

    df_answer_data = pd.read_csv('answer-data.csv')
    print_title('Input Data')
    print(df_answer_data)
    # resp = get_language_with_multi_value(['a', 'b', 'c'])
    # resp = get_language_with_multi_value(['a', 'c'])
    # print(resp)

    print_title('Generated Simple Answers')
    create_single_column_response(df_answer_data, 'city', 'Cities with highest screens are ', n_answer=4, sort_by='screens', sort_asc=False)
    create_single_column_response(df_answer_data, 'city', 'Cities with minimum screens are ', n_answer=2, sort_by='screens')
    create_single_column_response(df_answer_data, 'city', 'Cities with the most screens is ', n_answer=1, sort_by='screens', sort_asc=False)
    create_single_column_response(df_answer_data, 'city', 'Our algorithms suggest that we increase our budgets in ', n_answer=3, sort_by='impact', sort_asc=False)
    create_single_column_response(df_answer_data, 'city', 'Our algorithms suggest that we decrease our budgets in ', n_answer=3, sort_by='impact')

    print_title('Generated Complex Answers')
    create_multi_column_response(df_answer_data, 'city', 'screens', 'Among top cities there are ', 
                answer_suffix=' screens', answer_prefix=' with ',  n_answer=3, sort_by='screens', sort_asc=False)
    create_multi_column_response(df_answer_data, 'city', 'screens', 'Among cities with least screens are ', 
                answer_suffix=' screens', answer_prefix=' which has ',  n_answer=2, sort_by='screens', sort_asc=True)
    create_multi_column_response(df_answer_data, 'city', 'impact', 'Please increase the bid prices in ', 
                answer_suffix='', answer_prefix=' by ',  n_answer=4, sort_by='impact', sort_asc=False, is_highlight=False)
