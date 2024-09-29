import pandas as pd
import recordlinkage
import difflib
import re
from progress.bar import IncrementalBar

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


def add_to_dataset(dataset, multiindex, ind1, ind2):
    for x in range(len(multiindex)):
        try:
            location = [multiindex[x][0] in z for z in dataset[f'id_is{ind1}']].index(True)
        except ValueError:
            location = -1
        try:
            location1 = [multiindex[x][1] in z for z in dataset[f'id_is{ind2}']].index(True)
        except ValueError:
            location1 = -1
        if location >=0:
            dataset[f'id_is{ind2}'].loc[location].append(multiindex[x][1])
        elif location1 >= 0:
            dataset[f'id_is{ind1}'].loc[location1].append(multiindex[x][0])
        else:
            new_row = [[], [], []]
            new_row[ind1-1].append(multiindex[x][0])
            new_row[ind2-1].append(multiindex[x][1])
            dataset.loc[len(dataset)] = new_row



def main():
    mylist = [1,2,3,4,5,6,7,8]
    bar = IncrementalBar('Countdown', max = len(mylist))

    new_dataset = pd.DataFrame(columns=["id_is1", "id_is2", "id_is3"])
    storage_dir='input_data'

    # Читаем датасеты bar =1
    print("Чтение датасетов")
    first = pd.read_csv(f"{storage_dir}\main1.csv")
    second = pd.read_csv(f"{storage_dir}\main2.csv")
    third = pd.read_csv(f"{storage_dir}\main3.csv")
    bar.next()
    # ------------------------------------- Refactoring -----------------------------------------------------------

    # РЕФАКТОРИНГ ДБ 1 bar = 2
    print("Предобработка БД")
    first['full_name'] =  first["full_name"].apply(clean_FIO)
    first['phone'] = first['phone'].apply(clean_number)
    first['year'] = first['birthdate'].apply(lambda x: int(x.split('-')[0]) if len(x.split('-')) == 3 else None)
    first['month'] = first['birthdate'].apply(lambda x: int(x.split('-')[1]) if len(x.split('-')) == 3 else None)
    first['day'] = first['birthdate'].apply(lambda x: int(x.split('-')[2]) if len(x.split('-')) == 3 else None)
    first = first.drop("birthdate", axis=1)

    # РЕФАКТОРИНГ ДБ 2
    second['full_name'] =  second["last_name"].apply(clean_FIO) + " " + second["first_name"].apply(clean_FIO) + " " + second["middle_name"].apply(clean_FIO)
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
    bar.next()
    # ------------------------------------- Compairing -----------------------------------------------------------


    # Compare 1 and 3 bar = 3
    print("Совпадения между 1 и 3 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name')
    candidate_links = indexer.index(first, third)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.85)
    compare.string("email", "email", method='jarowinkler', label='email', threshold=0.9)
    compare_vectors = compare.compute(candidate_links, first, third)
    matches = compare_vectors[compare_vectors.sum(axis=1) >= 3]
    ecm = recordlinkage.ECMClassifier()
    connections_first_third = ecm.fit_predict(compare_vectors)

    add_to_dataset(new_dataset, connections_first_third, 1, 3)
    del connections_first_third
    bar.next()

    # Compare 1 and 2 bar = 4
    print("Совпадения между 1 и 2 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name')
    candidate_links = indexer.index(first, second)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.9)
    compare.string("phone", "phone", method='jarowinkler', label='phone', threshold=0.9)
    compare.string("address", "address", method='jarowinkler', label='address', threshold=0.9)
    compare_vectors = compare.compute(candidate_links, first, second)
    matches = compare_vectors[compare_vectors.sum(axis=1) >= 3]
    ecm = recordlinkage.ECMClassifier()
    connections_first_second = ecm.fit_predict(compare_vectors)

    add_to_dataset(new_dataset, connections_first_second, 1, 2)
    del connections_first_second
    bar.next()

    # Compare 1 and 1 bar = 5
    print("Совпадения между 1 и 1 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name')
    candidate_links = indexer.index(first, first)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.9)
    compare.string("email", "email", method='jarowinkler', label='email', threshold=0.9)
    compare.string("phone", "phone", method='jarowinkler', label='phone', threshold=0.9)
    compare.string("address", "address", method='jarowinkler', label='address', threshold=0.9)
    compare_vectors = compare.compute(candidate_links, first, first)
    matches = compare_vectors[compare_vectors.sum(axis=1) >= 4]
    ecm = recordlinkage.ECMClassifier()
    connections_first_first = ecm.fit_predict(compare_vectors)

    add_to_dataset(new_dataset, connections_first_first, 1, 1)
    del connections_first_first
    bar.next()

    # Compare 2 and 2 bar = 6
    print("Совпадения между 2 и 2 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name', window=7)
    candidate_links = indexer.index(second, second)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.9)
    compare.string("phone", "phone", method='jarowinkler', label='phone', threshold=0.9)
    compare.string("address", "address", method='jarowinkler', label='address', threshold=0.9)
    compare_vectors = compare.compute(candidate_links, second, second)
    ecm = recordlinkage.ECMClassifier()
    connections_second_second = ecm.fit_predict(compare_vectors)

    add_to_dataset(new_dataset, connections_second_second, 2, 2)
    del connections_second_second
    bar.next()

    # Compare 3 and 3 bar = 7
    print("Совпадения между 3 и 3 БД")
    indexer = recordlinkage.Index()
    indexer.sortedneighbourhood(left_on='full_name', right_on='full_name')
    candidate_links = indexer.index(third, third)   
    print("Количество претендентов на совпадение: ", len(candidate_links))
    compare = recordlinkage.Compare()
    compare.string("full_name", "full_name", method='jarowinkler', label='full_name', threshold=0.9)
    compare.string("email", "email", method='jarowinkler', label='email', threshold=0.9)
    compare.exact("sex", "sex", label='sex')
    compare_vectors = compare.compute(candidate_links, third, third)
    ecm = recordlinkage.ECMClassifier()
    connections_third_third = ecm.fit_predict(compare_vectors)

    add_to_dataset(new_dataset, connections_third_third, 3, 3)
    del connections_third_third
    bar.next()

    bar.finish()