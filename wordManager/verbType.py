import requests
from bs4 import BeautifulSoup
import re


# Returns the translation of the given verb
def get_translation(site_soup):
    translation = site_soup.find(id="translation").contents
    filtered_text = re.search(r'\"([^)]+)\"', str(translation)).group(1)

    return filtered_text


# Returns all of the conjugations from a specific table
def get_conjugation_from_table(site_soup, table_name, position):
    table_soup = BeautifulSoup(str(site_soup.find_all(class_=str(table_name)+"-cell-"+str(position))), "html.parser")
    all_conjugations = table_soup.find_all(class_="conjugation")

    return all_conjugations


# Converts the list of conjugations into something anki can use
def convert_as_formatted_list(conjugation_result_set):
    conjugation_list = []
    for item in conjugation_result_set:
        filtered_text = re.search(r'\>([^)]+)\<', str(item)).group(1)
        conjugation_list.append(filtered_text)

    output = ";" + ";".join(conjugation_list)
    return output


# Returns the specific "modo" for a given word
def get_modo_indicativo(site_soup):
    tmp_presente = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table1", "left"))
    tmp_pret_imperfeito = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table1", "middle"))
    tmp_pret_perfeito = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table1", "right"))

    tmp_pret_mais_que_perfeito = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table2", "left"))
    tmp_futuro = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table2", "middle"))
    tmp_condicional = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table2", "right"))

    return {
        "presente": tmp_presente,
        "pret_imperfeito": tmp_pret_imperfeito,
        "pret_perfeito": tmp_pret_perfeito,

        "pret_mais_que_perfeito": tmp_pret_mais_que_perfeito,
        "futuro": tmp_futuro,
        "condicional": tmp_condicional
    }


# Returns the specific "modo" for a given word
def get_modo_conjuntivo(site_soup):
    tmp_presente = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table3", "left"))
    tmp_pret_imperfeito = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table3", "middle"))
    tmp_futuro = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table3", "right"))

    return {
        "presente": tmp_presente,
        "pret_imperfeito": tmp_pret_imperfeito,
        "futuro": tmp_futuro
    }


# Returns the specific "modo" for a given word
def get_modo_imperativo(site_soup):
    tmp_afirmativo = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table4", "left"))
    tmp_negativo = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table4", "middle"))

    return {
        "afirmativo": tmp_afirmativo,
        "negativo": tmp_negativo
    }


# Returns the specific "modo" for a given word
def get_modo_infinitivo_pessoal(site_soup):
    tmp_base = convert_as_formatted_list(get_conjugation_from_table(site_soup, "table4", "right"))

    return {
        "base": tmp_base
    }

