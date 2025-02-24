import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report


data = pd.read_csv('system_data.csv')

# Преобразование столбца 'system_state' в числовой формат
# Замена текстовых значений на числовые метки
data['system_state'] = data['system_state'].map({'Normal': 0, 'Warning': 1, 'Critical': 2})


features = ['cpu_usage', 'cpu_temp', 'gpu_usage', 'gpu_temp', 'disk_usage', 'ram_usage']


X = data[features]
y = data['system_state']

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = GaussianNB()

# Обучение модели на обучающей выборке
model.fit(X_train, y_train)

# Прогнозирование на тестовой выборке
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Точность модели: {accuracy}")

print("Отчет о классификации:")
print(classification_report(y_test, y_pred))

new_data = pd.DataFrame({
    'cpu_usage': [10.0],
    'cpu_temp': [85.0],
    'gpu_usage': [60.0],
    'gpu_temp': [85.0],
    'disk_usage': [20.0],
    'ram_usage': [45.0]
})

prediction = model.predict(new_data)[0]

state_mapping = {0: 'Normal', 1: 'Warning', 2: 'Critical'}
predicted_state = state_mapping[prediction]

print(f"Прогнозируемое состояние системы: {predicted_state}")
