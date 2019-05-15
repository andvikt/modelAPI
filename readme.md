# ModelAPI
Библиотека для удобной "упаковки" модели для последующей интеграции в промышленный процесс
## Установка
pip install git+https://github.com/andvikt/sql_builder

Для работы требуется версия python не ниже 3.6

## Принцип работы
Чтобы "упаковать" модель для начала нужно описать процесс скоринга в виде функции, которая на вход принимает сырые данные
, на выходе отдает скор, при этом сама модель или какие-либо дополнительные параметры указываются как аргументы этой функции, например так:
```python
def score(data, model, imputer):
    data_imputed = imputer.transform(data)
    data_imputed['score'] = model.predict_proba(data_imputed)
    return data_imputed['score']
```
Далее эта функция и все необходимые аргументы передаются в контейнер:
```python
from modelAPI import BaseScorer
scorer = BaseScorer.make_scorer(
    score_foo=score #наша функция скоринга
    , model=test_model #какая-то модель, уже натренированная ранее
    , imputer=test_imputer #импютер, так же натренированный заранее
)
```
Теперь у нас есть объект типа BaseScorer, который в себе содержит функцию скоринга и все необходимые параметры для ее работы.

Перед сохранением можно проверить его работоспособность:
```python
test_score = scorer.score(test_data) # test_data - сырые данные
test_score.hist(20)
```
Если нас все устроило, сохраняем модель:
```python
scorer.save('test_scorer')
```
Модель сохранится в файле test_score в текущей рабочей папке. Ее можно загрузить в любое другое время.

Проверим работоспособность загруженной модели (после перезагрузки ядра или в другом проекте):
```python
from modelAPI import BaseScorer
scorer = BaseScorer.load('test_scorer')
test_score = scorer.score(test_data) # test_data - сырые данные
test_score.hist(20)
```
Если графики совпали, значит все ок, модель успешно сохранилась и загрузилась обратно

## Валидация данных
Часто мы вручную проверям все ли хорошо с нашими данными как на этапе их загрузки из бд, так и на этапе после скоринга. 
Этот процесс можно автоматизировать: мы можем запомнить основные статистики по нашим данным во время скоринга и проверить, 
сохраняются ли они на реальных боевых данных, для этого в ModelAPI есть класс DataValidator

Попробуем запомнить статистики по нашим данным
```python
from modelAPI import DataValidator
from modelAPI import val_schemas

data_validator = DataValidator(test_data, val_schemas.VAL_DATA_SCHEMA, 'data_validator')
score_validator = DataValidator(test_score, val_schemas.VAL_DATA_SCHEMA, 'score_validator')
score_validator.save('score_validator')
data_validator.save('data_validator')
```
Теперь чтобы проверить новые данные можно использовать:
```python
data_validator.validate(new_data, raise_on_error=False)
score_validator.validate(new_data, raise_on_error=False)

```
Если в новых данных ошибок нет, то вернется пустой датафрейм, если есть, то вернется dataframe с описанием найденных 
ошибок
## Валидационная схема
DataValidator использует так называему валидационную схему для запоминания статистик, схема по умолчанию выглядит так:
```python
VAL_DATA_SCHEMA = [
    _PrepValidator('dtypes', stats.dtypes, (WARNING, tr.not_match))
    , _PrepValidator('has_text', stats.has_text, (ERROR, tr.ne))
    , _PrepValidator('has_dates', stats.has_dates, (ERROR, tr.ne))
    , _PrepValidator('nans', stats.nans, (ERROR, tr.high_diff), (WARNING, tr.low_diff))
    , _PrepValidator('mean', stats.mean, (ERROR, tr.high_diff), (WARNING, tr.low_diff))
    , _PrepValidator('uniques', stats.uniques, (ERROR, tr.high_diff), (WARNING, tr.low_diff))
    , _PrepValidator('quant', stats.quantiles, (WARNING, tr.low_diff))
]
```
Валидационная схема - это список так называемых валидаторов, валидатор формируется из функции, которая на вход принимает 
данные размера [n, n_cols], а на выходе отдает рассчитанные статистики как правило размера [n_cols, 1], некоторые функции 
статистики уже содержатся в `modelAPI.data_validation.statistics`

Так же валидатор 
должен иметь в качестве позиционного параметра хотя бы один кортеж с описанием проверки, которую валидатор должен совершить
при вызове функции validate, этот кортеж состоит из двух объектов: 1-ый - уровень (WARNING, INFO, DEBUG, ERROR )
, на котором показывается сообщение об ошибке в логе (уровни берутся из стандартной библиотеки logging), 2-ой - функция 
сравнения статистик. Некоторые функции сравнения содержатся в modelAPI.data_validation.treatments:
```python
from modelAPI.data_validation.treatments import treatment_foo

@treatment_foo # обязательный декоратор для работы функции как функции сравнения
def ne(x, y):
    return not_equal(x, y)


@treatment_foo
def not_match(x, y):
    return x != y


@treatment_foo
def low_diff(y, x):
    diff = x/y
    return (diff < 0.5) | (diff > 2)


@treatment_foo
def high_diff(y, x):
    diff = x/y
    return (diff < 0.1) | (diff > 10)
```
