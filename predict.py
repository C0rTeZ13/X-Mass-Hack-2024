import pandas as pd
import numpy as np
import os
import argparse
from catboost import CatBoostClassifier


def load_ocved(ocved_path):
    # Загрузка данных
    ocved = pd.read_csv(ocved_path, header=None)  # Загрузка без заголовков

    # Преобразование строк в словарь
    ocved_dict = dict(zip(ocved.iloc[0], ocved.iloc[1].astype(int)))

    return ocved_dict


def getMinMax(normalizePath):
    data = pd.read_csv(normalizePath)

    norm_props = [
        "Нормализованно Доходы (тыс, руб.)",
        "Нормализованно Налоговая нагрузка",
        "Нормализованно Кол-во сотрудников",
        "Нормализованно Возможная сумма при 3%",
    ]

    min_norm = {prop: data[prop].min() for prop in norm_props}
    max_norm = {prop: data[prop].max() for prop in norm_props}

    return {"min": min_norm, "max": max_norm}


def analys(data, model_path="catboost_model.cbm"):
    # Загрузка модели
    model = CatBoostClassifier()
    model.load_model(model_path)

    # Получение предсказаний
    predictions = model.predict(data)
    probabilities = model.predict_proba(data)

    return predictions, probabilities


def proccess(filePath, normalize, ocved):
    # Загрузка данных
    data = pd.read_excel(filePath)
    result_data = data

    # Проверка наличия столбца "Основной ОКВЭД"
    if "Основной ОКВЭД" not in data.columns:
        print("Error: 'Основной ОКВЭД' column is missing in the input data.")
        return None

    # Применение маппинга для ОКВЭД
    data["Основной ОКВЭД"] = data["Основной ОКВЭД"].map(ocved).fillna(-1).astype(int)

    norm_props = ["Доходы (тыс, руб.)", "Налоговая нагрузка", "Кол-во сотрудников", "Возможная сумма при 3%"]

    # Логарифмирование и нормализация
    for prop in norm_props:
        if prop in data.columns:
            data[prop] = np.log1p(data[prop].clip(lower=0))  # Убираем отрицательные значения
            data["Нормализованно " + prop] = (
                data[prop] - normalize["min"]["Нормализованно " + prop]
            ) / (normalize["max"]["Нормализованно " + prop] - normalize["min"]["Нормализованно " + prop])
        else:
            print(f"Warning: Column '{prop}' is missing in the input data.")

    # Преобразование категориальных переменных
    data["Система налогообложения"] = data["Система налогообложения"].astype("category").cat.codes + 1
    data["Система налогообложения"] = data["Система налогообложения"].apply(lambda x: 1 if x != 0 else 0)

    data["Негативная информация"] = data["Негативная информация"].astype("category").cat.codes + 1
    data["Негативная информация"] = data["Негативная информация"].apply(lambda x: 1 if x != 0 else 0)

    # Вычисление отношения оборотов
    data["Отношение оборотов"] = np.where(
        (data["Планируемый оборот по анкете (руб)"] == 0) & (data["Планируемый оборот по снятию д/с (руб)"] == 0), 1,
        np.where((data["Планируемый оборот по анкете (руб)"] == 0) & (data["Планируемый оборот по снятию д/с (руб)"] != 0), 1,
                 np.where((data["Планируемый оборот по анкете (руб)"] != 0) & (data["Планируемый оборот по снятию д/с (руб)"] == 0), 0,
                          data["Планируемый оборот по снятию д/с (руб)"] / data["Планируемый оборот по анкете (руб)"])))
    data = data.drop(columns=["Планируемый оборот по анкете (руб)", "Планируемый оборот по снятию д/с (руб)"])

    # Объединение негативной информации
    data["Вся негативная информация"] = data["Негативная информация"].combine_first(data["Негатив относительно ГД"])
    data = data.drop(columns=["Негативная информация", "Негатив относительно ГД"])

    # Удаление лишних столбцов
    data = data.drop(columns=['ИНН'])
    data = data.drop(columns=norm_props)

    data = data.iloc[:, [0, 1, 8, 2, 10, 6, 3, 4, 11, 7, 5, 9]]

    # Получение предсказаний
    predictions, probabilities = analys(data)

    # Добавление предсказаний в данные
    result_data["Решение"] = predictions
    result_data["Вероятность выдачи кредита"] = probabilities[:, 1]  # Вероятность для класса 1

    return result_data


def main():
    parser = argparse.ArgumentParser(description="Usage: python script.py /path/to/input.xlsx /path/to/output.xlsx")
    parser.add_argument("input_path", type=str, help="Path to the input file")
    parser.add_argument("output_path", type=str, help="Path to save the output file")
    args = parser.parse_args()

    filePath = args.input_path
    outputPath = args.output_path

    minMaxPath = "min_max.csv"
    ocvedPath = "ocved.csv"

    # Проверка наличия файлов
    if not os.path.exists(filePath):
        print(f"Error: The file '{filePath}' does not exist.")
        return

    if not os.path.exists(minMaxPath):
        print(f"Error: The file '{minMaxPath}' does not exist.")
        return
    
    if not os.path.exists(ocvedPath):
        print(f"Error: The file '{ocvedPath}' does not exist.")
        return

    # Получение данных для нормализации
    normalize = getMinMax(minMaxPath)

    # Получение данных ОКВЭДа
    ocved = load_ocved(ocvedPath)

    # Обработка файла
    result_data = proccess(filePath, normalize, ocved)

    if result_data is not None:
        # Сохранение результата
        result_data.to_excel(outputPath, index=False)
        print(f"Results saved to {outputPath}")


if __name__ == "__main__":
    main()
