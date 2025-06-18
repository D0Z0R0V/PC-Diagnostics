import pandas as pd
from sklearn.naive_bayes import GaussianNB
import joblib
from pathlib import Path

class DiagnosticModel:
    def __init__(self, data_path='system_data.csv'):
        self.model = GaussianNB()
        self.data_path = data_path
        self.state_mapping = {'Normal': 0, 'Warning': 1, 'Critical': 2}
        self.load_or_train_model()

    def load_or_train_model(self):
        model_file = Path("data/model/diagnostic_model.pkl")
        if model_file.exists():
            self.model = joblib.load(model_file)
        else:
            self.train_model()
            joblib.dump(self.model, model_file)

    def train_model(self):

        # Чтение данных с обработкой возможных ошибок
        try:
            data = pd.read_csv(self.data_path)
            
            # Проверка и очистка данных
            if data.empty:
                raise ValueError("Файл данных пуст")
                
            # Заполнение пропущенных значений
            data.fillna({
                'cpu_usage': 0,
                'cpu_temp': 0,
                'gpu_usage': 0,
                'gpu_temp': 0,
                'disk_usage': 0,
                'ram_usage': 0,
                'system_state': 'Normal'
            }, inplace=True)
            
            # Преобразование меток классов
            data['system_state'] = data['system_state'].map(self.state_mapping)
            
            features = ['cpu_usage', 'cpu_temp', 'gpu_usage', 'gpu_temp', 'disk_usage', 'ram_usage']
            X = data[features]
            y = data['system_state']
            
            # Удаление строк с оставшимися NaN (если есть)
            X = X.dropna()
            y = y[X.index]
            
            if len(X) == 0:
                raise ValueError("Нет допустимых данных для обучения")
                
            self.model.fit(X, y)
            
        except Exception as e:
            print(f"Ошибка при обучении модели: {str(e)}")
            # Создаем модель с дефолтными параметрами
            self.model = GaussianNB()
            # Создаем искусственные данные для обучения
            import numpy as np
            X = np.array([[0]*6])
            y = np.array([0])
            self.model.fit(X, y)

    def predict(self, cpu_usage, cpu_temp, gpu_usage, gpu_temp, disk_usage, ram_usage):
        try:
            # Обработка входных данных
            input_data = pd.DataFrame([{
                'cpu_usage': max(0, float(cpu_usage)),
                'cpu_temp': max(0, float(cpu_temp)),
                'gpu_usage': max(0, float(gpu_usage)),
                'gpu_temp': max(0, float(gpu_temp)),
                'disk_usage': max(0, float(disk_usage)),
                'ram_usage': max(0, float(ram_usage))
            }])
            
            prediction = self.model.predict(input_data)[0]
            # Обратное преобразование к текстовому статусу
            state_mapping = {v: k for k, v in self.state_mapping.items()}
            return state_mapping.get(prediction, "Unknown")
            
        except Exception as e:
            print(f"Ошибка при предсказании: {str(e)}")
            return "Error"