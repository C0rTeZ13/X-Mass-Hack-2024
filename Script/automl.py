import pandas as pd
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
from sklearn.model_selection import train_test_split

# Загружаем данные
data = pd.read_csv('output.csv')

# Разделение данных
X = data.drop(columns=['score'])  # Признаки
y = data['score']  # Целевая переменная
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание AutoML модели
automl = TabularAutoML(task = Task(name = 'binary', metric = 'auc'))  # Настраиваем задачу (reg для регрессии)
model = automl.fit_predict(X_train, roles={'target': y_train})

# Оценка модели на тестовых данных
y_pred = automl.predict(X_test).data
print(f"RMSE: {(y_test - y_pred).pow(2).mean() ** 0.5}")

# Сохранение модели
import pickle
with open('automl_model.pkl', 'wb') as f:
    pickle.dump(automl, f)

# Загрузка модели
with open('automl_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# Использование загруженной модели для предсказаний
y_loaded_pred = loaded_model.predict(X_test).data

import matplotlib.pyplot as plt

# Получение важности признаков
feature_importance = automl.get_feature_scores('importance')

# Визуализация
feature_importance.plot(kind='barh', figsize=(10, 6))
plt.title('Важность признаков')
plt.show()
