import pandas as pd
import recordlinkage
import difflib
import re

def diffseeker(a, b):
    an = a.lower()
    bn = b.lower()
    matcher = difflib.SequenceMatcher(None, an, bn)
    return matcher.ratio()


def clean_FIO(name):
    
    if isinstance(name, str):
        return "".join(c for c in name if c.isalpha())
    elif isinstance(name, float):
        return ""
    else:
        return name

def clean_number(number):
    return re.sub('\D', "", number)

def clean_date(date):
    return date.split("-")




def main():

    storage_dir='D:\ML DATA\input_data'

    # Читаем датасеты
    first = pd.read_csv(f"{storage_dir}\main1.csv")
    second = pd.read_csv(f"{storage_dir}\main2.csv")
    third = pd.read_csv(f"{storage_dir}\main3.csv")

    # РЕФАКТОРИНГ ДБ 1
    first['full_name'] =  first["full_name"].apply(clean_FIO)
    first['phone'] = first['phone'].apply(clean_number)
    first['year'] = first['birthdate'].apply(lambda x: int(x.split('-')[0]) if len(x.split('-')) == 3 else None)
    first['month'] = first['birthdate'].apply(lambda x: int(x.split('-')[1]) if len(x.split('-')) == 3 else None)
    first['day'] = first['birthdate'].apply(lambda x: int(x.split('-')[2]) if len(x.split('-')) == 3 else None)
    first = first.drop("birthdate", axis=1)

    # РЕФАКТОРИНГ ДБ 2
    second['full name'] =  second["last_name"].apply(clean_FIO) + " " + second["first_name"].apply(clean_FIO) + " " + second["middle_name"].apply(clean_FIO)
    second = second.drop(['first_name', 'last_name', 'middle_name'], axis=1)
    second['phone'] = second['phone'].apply(clean_number)
    second['year'] = second['birthdate'].apply(lambda x: int(x.split('-')[0]) if len(x.split('-')) == 3 else None)
    second['month'] = second['birthdate'].apply(lambda x: int(x.split('-')[1]) if len(x.split('-')) == 3 else None)
    second['day'] = second['birthdate'].apply(lambda x: int(x.split('-')[2]) if len(x.split('-')) == 3 else None)
    second = second.drop("birthdate", axis=1)

    # РЕФАКТОРИНГ ДБ 3
    third['full_name'] =  third["name"].apply(clean_FIO)
    third = third.drop("name", axis=1)

    third['year'] = third['birthdate'].apply(lambda x: int(x.split('-')[0]) if len(x.split('-')) == 3 else None)
    third['month'] = third['birthdate'].apply(lambda x: int(x.split('-')[1]) if len(x.split('-')) == 3 else None)
    third['day'] = third['birthdate'].apply(lambda x: int(x.split('-')[2]) if len(x.split('-')) == 3 else None)
    third = third.drop("birthdate", axis=1)

    # Compare 1 and 3
    print("Совпадения между 1 и 3 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name')
    candidate_links = indexer.index(first, third)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.8)
    compare.string("email", "email", method='jarowinkler', label='email', threshold=0.8)
    compare.exact("sex", "sex", label='sex')
    compare.exact("year", 'year', label='year')
    compare.exact("month", 'month', label='month')
    compare.exact("day", 'day', label='day')
    compare_vectors = compare.compute(candidate_links, first, third)
    matches = compare_vectors[compare_vectors.sum(axis=1) >= 4]
    print("Предсказания всухую: ",len(matches))
    print(matches)
    ecm = recordlinkage.ECMClassifier()
    ml_matches = ecm.fit_predict(compare_vectors)
    print("Предсказания моделью: ",len(ml_matches))
    print(ml_matches)

    # Compare 1 and 2
    print("Совпадения между 1 и 2 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name')
    candidate_links = indexer.index(first, second)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.8)
    compare.string("phone", "phone", method='jarowinkler', label='phone', threshold=0.9)
    compare.string("address", "address", method='jarowinkler', label='address', threshold=0.9)
    compare.exact("year", 'year', label='year')
    compare.exact("month", 'month', label='month')
    compare.exact("day", 'day', label='day')
    compare_vectors = compare.compute(candidate_links, first, third)
    matches = compare_vectors[compare_vectors.sum(axis=1) >= 4]
    print("Предсказания всухую: ",len(matches))
    print(matches)
    ecm = recordlinkage.ECMClassifier()
    ml_matches = ecm.fit_predict(compare_vectors)
    print("Предсказания моделью: ",len(ml_matches))
    print(ml_matches)