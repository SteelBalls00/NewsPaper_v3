from django import template


register = template.Library()


@register.filter()
def censor(content, censor_list):
    censor_list = ['редиска', 'Редиска', 'сортировки', 'богатые', 'метод', 'Для'] # Пример списка запрещенных слов который
    lower_censor_list = [words.lower() for words in censor_list]           # мы приводим в нижний регистр дабы исключить заглавные буквы.
    split_content = content.split()                                        # Создаем из контента список.

    for i in range(len(split_content)):
        if isinstance(split_content[i], str):                               # Проверка переменной на строковый тип
            if split_content[i].lower() in lower_censor_list:               # Каждое слово из текста приводится в нижний регистр
                first_letter = split_content[i][0]                          # и сравнивается с цензор-списком.
                other_letter = split_content[i][1:]
                replaced_word = first_letter + '*' * len(other_letter)      # Ну тут понятно, собираем слово после цензуры
                split_content[i] = replaced_word                            # и собираем обратно в текст контента.
        else:
            continue
    return ' '.join(split_content)