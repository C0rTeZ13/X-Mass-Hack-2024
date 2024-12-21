import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import shap
import matplotlib.pyplot as plt

# Загрузка данных
data = pd.read_csv('output.csv')
data = data.drop(columns=['ЗСК'])
data = data.drop(columns=['score'])

# Разделение признаков и целевой переменной
X = data.drop(columns=['result'])  # Исключаем целевую переменную
y = data['result']

# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание пула данных для CatBoost
train_pool = Pool(X_train, y_train)
test_pool = Pool(X_test, y_test)

# Инициализация и обучение модели

model = CatBoostClassifier(iterations=1000,
                          learning_rate=0.01,
                          depth=5,
                          loss_function='Logloss',
                          random_seed=np.random.randint(10**5),
                          logging_level='Silent')
model.fit(train_pool, eval_set=test_pool)

# Сохранение модели
model.save_model("catboost_model.cbm", format="cbm")
print("Модель успешно сохранена в файле catboost_model.cbm")

# Оценка качества
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

print(f"Accuracy: {accuracy:.2f}")
print(f"ROC-AUC: {roc_auc:.2f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Оценка производительности модели
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy}")

# SHAP-анализ важности признаков
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Визуализация важности признаков
shap.summary_plot(shap_values, X_test, plot_type="bar")
shap.summary_plot(shap_values, X_test)

# Индивидуальный вклад признаков (пример для одного объекта)
shap.force_plot(explainer.expected_value, shap_values[0, :], X_test.iloc[0, :], matplotlib=True)
