Измненения:

1. При добавленнии дисциплины создаеться Permissons Name: Can view Математика Codename: view_математика 
2. Преподавватель может видись те дисциплины к которым у него есть Permissons
3. При добавлении топика создаеться Permissons Name: Can view Сложение Codename: view_сложение
4. Преподавватель видит те топики на которые у него есть Permissons
5. При добавлении топика в выподающем списке дисциплин появляються те дисциплины на которые есть Permissons
6. При создании теста в выподающем списке топиков выподают те которые может видеть пользователь
7. В списке тестов при нажатии на название теста перекидывает на страницу этого теста с результатами студентов прошедших этот тест
8. На странцие с результатами есть динамичным поиском и фильтрацией по имени фамилии баллам и оценкам  
9. Полностью изменена страница arter_login
10. Студнты могут проходить только те тесты которые отсносяться к их факультету 
11. Студент может видить свои результаты за прошедшие тесты
12. Стили страниц перенесены в отдельные css файлы
13. Скрипты перенесены в отделные файлы js 
14. Добавлены оценки в зависимости от того сколько бллов набрал пользователь 

Исправленные оошибки:
1. В моделе Quizresult вместе связи с Topik связь к Preset
2. Функция generate_test. Раньше  если генерации теста сгенерировать больше вопросов то некоторые вопросы оставались без не верных ответо это происходло из того что вопросы выбирали не из полного списка не верных ответов а из того что осталось. То есть если вопросов 2 (1 + 1, 2 + 2) а не верные ответы 1 2 3 4 5 то у не первого вопорса не верные ответы 1 2 3 а у второго 4 5  
