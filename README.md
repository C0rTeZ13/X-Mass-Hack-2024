# Описание

![ ](/_image/sticker.gif)

Проект выполнен командой «Kizil» в рамках хакатона [XMAS_HACK2024](https://xmas-hack.ru/) по треку «**Стартовый (профилактический) комплаенс: предотвращение рисков с помощью AI**».

На хакатоне была поставлена задача создания системы, которая на основе предоставленных данных о текущих клиентах банка, а также дополнительной информации из открытых источников, социальных сетей, сайтов и других параметров о компании, способна прогнозировать уровень риска нового клиента.

Вся первоначальная информация расположена в директории [Документации](/_doc/):

* [Предлагамое решение](/_doc/solution.md)
* [Описание процесса обучения модели](/_doc/algorithm_guide.md)

Ссылка на спецификацию API, которая в проекте выступает как Frontend - [Swagger API](http://83.217.213.75:8080/swagger/index.html)

# Структура репозитория:

    ./_doc/ -- здесь хранится документация и другие материалы
        ./solution.md
        ./setup_guide.md
        ./algorithm_guide.md
    ./_image/ -- папка для хранения изображений документации
    
    ./API/ - проект MS Visual Studio (C#)
    ./DataLayer/
    ./ServiceLayer/

    ./Script/ -- Папка python скриптов
        ./*.csv - различные .csv файлы
        ./preprocess.py - предобработка исходных данных
        ./model.py - процесс обучения
        ./predict.py - получения предсказания для клиента
        ./catboost_model.cbm - файл полученной модели

    ./Dockerfile 
    ./docker-compose.yml