# Что вообще происходит?

Мы сделали вывод решений, получаемых с помощью _sympy_. Для этого были написаны специальные методы, которые собирают промежуточные значения и затем позволяют вывести весь ход решения.

Эти методы расположены в файле _sympy/utilities/solution.py_. 

#### Методы сборки решения

- `add_comment(cm, *args)` 

Этот метод вставляет текстовый комментарий, в который можно внедрять значения переменных через дополнительные аргументы. Например `add_comment("I've found the root!")` или `add_comment("Let X equals to {}", str(x))`.

- `add_step(variable)`

Этот метод используется с какой либо переменной. В ход решения добавляется конструкция вида _x = val_, где _x_ это имя переменной, а _val_ это её текущее значение.

- `add_eq(leftPart, rightPart)`

Этот метод используется для записи равенств. В функцию передаются соответственно левая и правая часть равенства.

- `add_exp(expression)`

Этот метод используется для записи произвольных выражений.

#### Методы управления блоками (в текущей реализации ещё не поддерживаются)

Для управление выводом сложного решения, которое состоит из нескольких более простых подзадач, можно использовать эти функции.

- `start_subroutine(name)`

Эта функция начинает именованный блок решения.

- `cancel_subroutine()`

Эта функция удаляет из хода решения всё, что было добавлено после последнего вызова `start_subroutine`. Она полезна, когда в ходе решения блока оказалось, что весь текущий блок для решения не нужен и решение пойдет по другой ветке.

- `commit_subroutine()`

Эта функция окончательно сохраняет блок решения от последнего вызова `start_subroutine` до текущего момента. Сохранённый блок уже нельзя будет отменить.

#### Методы получения решения

- `reset_solution()`

Эта функция очищает ход решения. Она обычно используется перед вызовом любой решающей функции, например `solve`.

- `last_solution()`

Эта функция возвращает массив с текущим решением. Обычно используется после работы решающих функций, таких как `solve`. По этим данным для пользователя может быть построено красиво выглядящее решение примера.

#### Управление выводом

- `set_comment_table(ct)`

Эта функция позволяет подключить таблицу трансляции комментариев. В настоящий момент доступны две таблицы трансляции: `solution_comment_table_ru` и `solution_comment_table_en`.

- `setMathMLOutput()`

Устанавливает формат вывода формул MathML.

- `setLatexOutput()`

Устанавливает формат вывода формул Latex. По умолчанию включён именно он.

# Что ещё нужно сделать?

Но это ещё не всё. Чтобы собрать ход решения нужно внедрить в код решателя вызовы функций, сохраняющих промежуточные значения. 
Например в файле integrals.py находится код решающий интегралы. Для получения хода решения в функцию `doit` добавляются вызовы `add_comment` и другие.

Аналогично собираются решения для других типов уравнений.

Иногда вновь добавленная сборка промежуточных решений может повлиять на решение уже сделанных ранее уравнений. Для контроля таких случаев используется автоматическое тестирование (этот модуль в процессе разработки).
