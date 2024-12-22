import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

data = pd.read_csv("data.csv")

ocved_dop = pd.DataFrame()
ocved_dop["Основной ОКВЭД"] = data["Основной ОКВЭД"].unique()
ocved_dop = ocved_dop.sort_values(by="Основной ОКВЭД")
ocved = pd.DataFrame(columns=ocved_dop["Основной ОКВЭД"])
ocved.loc[0] = range(1, len(ocved_dop["Основной ОКВЭД"]) + 1)

data = data.head(20000)
parse = pd.read_csv("parsing.csv")

parse["Rating"] = parse["Rating"] / 100
parse["Revenue"] = parse["Revenue"] / 1000

data = pd.merge(data, parse, on="ИНН", how="left")
data["Rating"].fillna(0.2, inplace=True)
data["RecommendedDealLimit"].fillna(80000, inplace=True)

data["Доходы (тыс, руб.)"] = data.apply(lambda r: r["Revenue"] if pd.isna(r["Доходы (тыс, руб.)"]) else r["Доходы (тыс, руб.)"], axis=1)
data["Основной ОКВЭД"] = data.apply(lambda r: r["ActivityCode"] if pd.isna(r["Основной ОКВЭД"]) else r["Основной ОКВЭД"], axis=1)
data["Кол-во сотрудников"] = data.apply(lambda r: r["EmemployeeCount"] if pd.isna(r["Кол-во сотрудников"]) else r["Кол-во сотрудников"], axis=1)

del_props = ["ИНН", "Дата регистрации", "Адрес", "ФИО Генерального директора", "Дата рождения Генерального директора",
             "ФИО Бенефициара", "Сайт", "Номер телефона", "Провайдер", "Деятельность клиента", "Деятельность клиента со слов клиента",
             "Кол-во сотрудников со слов клиента", "Срок жизни SIM-карты/номера (от даты замены e/SIM-карты)",
             "Срок жизни SIM в текущем пользовательском устройстве",
             "Срок жизни SIM-карты/номера (количество дней/часов/минут, которое прошло от даты заключения договора)", "Revenue", "ActivityCode", "EmemployeeCount"]

data = data.drop(columns=del_props)
data["Вся негативная информация"] = data["Негативная информация"].combine_first(data["Негатив относительно ГД"])
data = data.drop(columns=["Негативная информация", "Негатив относительно ГД"])

for column in data.columns:
    if data[column].dtype == "object":
        data[column] = data[column].astype("category").cat.codes + 1

data.fillna(0, inplace=True)

bins = [0, 10, 30, 100, float('inf')]
labels = [0.5, 0, 0.5, 1]
data["Кол-во дополнительных ОКВЭДОВ"] = pd.cut(data["Кол-во дополнительных ОКВЭДОВ"], bins=bins, labels=labels, right=False, ordered=False)

data["Система налогообложения"] = data["Система налогообложения"].apply(lambda x: 1 if x != 0 else 0)
data["Вся негативная информация"] = data["Вся негативная информация"].apply(lambda x: 1 if x != 0 else 0)

data["Отношение оборотов"] = np.where((data["Планируемый оборот по анкете (руб)"] == 0) & (data["Планируемый оборот по снятию д/с (руб)"] == 0), 1,
                                      np.where((data["Планируемый оборот по анкете (руб)"] == 0) & (data["Планируемый оборот по снятию д/с (руб)"] != 0), 1,
                                               np.where((data["Планируемый оборот по анкете (руб)"] != 0) & (data["Планируемый оборот по снятию д/с (руб)"] == 0), 0,
                                                        data["Планируемый оборот по снятию д/с (руб)"] / data["Планируемый оборот по анкете (руб)"])))
data = data.drop(columns=["Планируемый оборот по анкете (руб)", "Планируемый оборот по снятию д/с (руб)"])

data.rename(columns={"Rating": "Оценка надежности"}, inplace=True)
data.rename(columns={"RecommendedDealLimit": "Возможная сумма при 3%"}, inplace=True)

min_max = pd.DataFrame()
norm_props = ["Доходы (тыс, руб.)", "Налоговая нагрузка", "Кол-во сотрудников", "Уставной капитал (руб)", "Возможная сумма при 3%"]
for prop in norm_props:
    data[prop] = np.log1p(data[prop])
    data["Нормализованно " + prop] = (data[prop] - data[prop].min()) / (data[prop].max() - data[prop].min())
    min_max["Нормализованно " + prop] = [data[prop].min(), data[prop].max()]
data = data.drop(columns=norm_props)

data["Нормализованно Уставной капитал (руб)"] = data["Нормализованно Уставной капитал (руб)"].apply(lambda x: 0 if x < 0.2 else x)

data = data.iloc[:, [0, 1, 11, 2, 8, 9, 3, 4, 5, 7, 10, 12, 6, 13]]

weights = [0, 0.2, -0.2, -0.3, 0.3, -0.4, 2, 0.8, 0.6, 0.2, -0.5, -0.1, -2, -0.5]
weights_categories = pd.DataFrame([weights], columns=data.columns.tolist())

data["score"] = 0.0
for index, row in data.iterrows():
    w = 0.0
    score = 0.0
    for column in data.columns:
        if column != "score":
            w += weights_categories[column].item()
            score += weights_categories[column].item() * row[column].item()

    data.loc[index, "score"] = score / w

    if index % 10000 == 0:
        print(index)

line = data["score"].min() + abs(data["score"].max() - data["score"].min()) * 0.4
data["result"] = data["score"].apply(lambda x: 0 if x > line else 1)

data.to_csv('output.csv', index=False)
min_max.to_csv('min_max.csv', index=False)
ocved.to_csv('ocved.csv', index=False)

print(data["score"].min())
print(data["score"].max())
