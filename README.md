# regex.py

У цій лабораторній роботі було імлементовано імітацію роботи недетермінованого скінченного автомата (НСА) для сприймання Regex.

## Стани Автомата

Імлементація програми базується на патерні програмування State, тому було реалізовані окермі стани, які й імітують стани в НСА.


Тобто, коли ми отримуємо стірчку з regex, то ми постійно переходимо в різні стани. Ці стани реалізовані як окремі класи, що відповідає патерну State



Усі класи за принципом ООП поліморфізму успадковуються від абстрактного класу ```State(ABC)```.


Метод ```check_next()``` реалізовано в базовому класі, оскільки логіка пошуку наступного стану однакова для всіх станів

Поле ```next_states``` визначено в базовому класі, оскільки всі стани повинні мати можливість переходу до інших станів


```python

def __init__(self) -> None:

        """Initialize a state with empty next states list."""

        self.next_states: list[State] = []


    @abstractmethod

    def check_self(self, char: str | None) -> bool:

        """

        Check if the given character matches this state.


        Args:

            char: Character to check or None


        Returns:

            True if the character matches this state, False otherwise

        """

        pass


    def check_next(self, next_char: str) -> State | Exception:

        """

        Find the next state that matches the given character.


        Args:

            next_char: Character to check against next states


        Returns:

            The matching next state


        Raises:

            NotImplementedError: If no matching next state is found

        """

        for state in self.next_states:

            if state.check_self(next_char):

                return state

        raise NotImplementedError("rejected string")

```





Клас ```StartState(State)``` представляє імітацію початквого стану автомата.

Метод ```check_self повертає``` ```False```, оскільки початковий стан сам не перевіряє символи

Початковий стан завжди є "віртуальним" і не бере участі в прямому співставленні з символами




```python

class StartState(State):

    """Special state that marks the beginning of the FSM."""


    next_states: list[State] = []


    def __init__(self):

        """Initialize the start state."""

        super().__init__()


    def check_self(self, char: str | None) -> bool:

        """

        Start state is never matched directly.


        Args:

            char: Character to check (ignored)


        Returns:

            Always False

        """

        return False

```


```TerminationState``` — це спеціалізований клас стану, який успадковується від абстрактного класу State і представляє кінцевий (термінальний) стан у скінченному автоматі.

Подібно до ```StartState```, ніколи не співпадає з символами вхідного рядка (```check_self``` завжди повертає ```False```)

Не містить переходів до інших станів (його атрибут next_states залишається порожнім списком)

Використовується як маркер успішного завершення співставлення

```python

class TerminationState(State):

    """Special state that marks the end of the FSM."""


    def __init__(self) -> None:

        """Initialize the termination state."""

        super().__init__()


    def check_self(self, char: str | None) -> bool:

        """

        Termination state is never matched directly.


        Args:

            char: Character to check (ignored)


        Returns:

            Always False

        """

        return False

```


Клас ```DotState``` успідковується від абсратктного класу та імтує повідінку стану, який відповідає за читання крапки. . У контексті регулярних виразів, крапка зазвичай означає "будь-який один символ"



Коли рушій регулярних виразів (```RegexFSM```) обробляє вхідний рядок і поточним активним станом стає екземпляр DotState:


Береться наступний символ з вхідного рядка.

Цей символ передається в метод ```dot_state_instance.check_self(input_char)```.

Якщо ```check_self``` повертає ```True```, це означає, що крапка успішно "спожила" цей символ. Далі рушій спробує перейти до одного зі станів, вказаних у ```dot_state_instance.next_states```, використовуючи вже наступний символ вхідного рядка.

Якщо ```check_self```   повертає ```False``` (наприклад, якщо вхідний рядок закінчився, а ```DotState``` очікував символ), то цей шлях зіставлення вважається невдалим


```python


class DotState(State):

    """State that matches any character (.) in regex."""


    next_states: list[State] = []


    def __init__(self):

        """Initialize a dot state."""

        super().__init__()


    def check_self(self, char: str | None) -> bool:

        """

        Matches any non-None character.


        Args:

            char: Character to check


        Returns:

            True if char is not None, False otherwise

        """

        return char is not None




```


Клас ``` AsciiState(State)```  імітує стан в автоматі, що читатиме один окремий символ з ASCII. Клас успідковієтьсявід абстактоного, то поля теж.


Метод ```check_self(self, curr_char: str | None) -> bool```:


ключовий метод для ```AsciiState```. Він перевіряє, чи відповідає вхідний символ curr_char тому символу, який зберігається в ```self.curr_sym```.

```return curr_char == self.curr_sym```: Якщо ```curr_char``` ідентичний ```self.curr_sym```, метод повертає True (символ розпізнано). В іншому випадку (включаючи, якщо ```curr_char``` є ```None```), він повертає ```False```.


```python


class AsciiState(State):

    """State that matches a specific ASCII character."""


    next_states: list[State] = []

    curr_sym: str = ""


    def __init__(self, symbol: str) -> None:

        """

        Initialize an ASCII state with the specified symbol.


        Args:

            symbol: The specific character this state will match

        """

        super().__init__()

        self.curr_sym = symbol


    def check_self(self, curr_char: str | None) -> bool:

        """

        Check if the current character matches this state's symbol.


        Args:

            curr_char: Character to check


        Returns:

            True if characters match, False otherwise

        """

        return curr_char == self.curr_sym


```




Клас StarState реалізує логіку оператора Кліні (зірочка ```*```) в регулярних виразах. Оператор ```*``` застосовується до попереднього елемента (представленого ```checking_state```) і означає "нуль або більше повторень" цього елемента. Наприклад, ```a*``` означає нуль або більше символів ```a```.

Цей клас такоє успідкоується від абстарктного, проте потрвім виокремити


Метод ```check_self(self, char: str | None) -> bool```:


Цей метод у ```StarState``` делегує перевірку символу char методу ```check_self``` свого внутрішнього стану self.checking_state.

```return self.checking_state.check_self(char):``` Тобто, ```StarState.check_self``` поверне ```True```, якщо символ ```char``` може бути зіставлений патерном, до якого застосована зірочка.

Важливе зауваження: Сам по собі цей метод ```check_self``` не реалізує повну логіку "нуль або більше". Він лише відповідає на питання: "чи може елемент, що повторюється, зіставитися з цим конкретним символом?". Повна логіка оператора ```*``` (включаючи можливість нульового зіставлення, множинні зіставлення та перехід до наступних станів після ```*```) зазвичай реалізується в основному алгоритмі зіставлення рядка в класі ```RegexFSM``` (наприклад, в ```check_string_iterative``` або ```_match_recursive```).


```python

class StarState(State):

    """State that implements the Kleene star (*) operator."""


    next_states: list[State] = []


    def __init__(self, checking_state: State):

        """

        Initialize a star state with the state to check.


        Args:

            checking_state: The state whose matching criteria will be used

        """

        super().__init__()

        self.checking_state = checking_state


    def check_self(self, char: str | None) -> bool:

        """

        Check if character matches the underlying state.


        Args:

            char: Character to check


        Returns:

            Result of the checking state's check_self method

        """

        return self.checking_state.check_self(char)




```



Клас ```PlusState``` реалізує логіку оператора ```+``` (плюс) в регулярних виразах. Оператор ```+``` застосовується до попереднього елемента ```checking_state``` і означає "одне або більше повторень" цього елемента. Наприклад, ```a+```означає один або більше символів ```a```.

Подібно до StarState, цей метод делегує перевірку символу char методу ```check_self``` свого внутрішнього стану ```self.checking_state```.

```return self.checking_state.check_self(char):``` Повертає ```True```, якщо символ char може бути зіставлений патерном, до якого застосовано плюс.

Важливе зауваження: Як і у випадку з StarState, метод ```check_self``` для ```PlusState``` не реалізує повну логіку "одне або більше". Він лише перевіряє, чи може елемент, що повторюється, зіставитися з поточним символом. Повна логіка ```+``` (обов'язкове перше зіставлення, потім можливі наступні, та перехід далі) реалізується в основному алгоритмі зіставлення в ```RegexFSM```.

```python
class PlusState(State):

    """State that implements the plus (+) operator."""


    next_states: list[State] = []


    def __init__(self, checking_state: State):

        """

        Initialize a plus state with the state to check.


        Args:

            checking_state: The state whose matching criteria will be used

        """

        super().__init__()

        self.checking_state = checking_state


    def check_self(self, char: str | None) -> bool:

        """

        Check if character matches the underlying state.


        Args:

            char: Character to check


        Returns:

            Result of the checking state's check_self method

        """

        return self.checking_state.check_self(char)
```



Іншимим словами


StarState та ```PlusState``` є "обгортками" для інших станів ```checking_state```, що дозволяють реалізувати логіку повторень. Їхні методи ```check_self``` лише перевіряють, чи може базовий елемент ```checking_state``` зіставитися з символом. Повна семантика операторів ```*``` (нуль або більше) та ```+``` (один або більше), включаючи управління кількістю повторень та переходи, реалізується на вищому рівні – в алгоритмі обходу скінченного автомата (наприклад, у методі ```check_string``` класу ```RegexFSM```).





Клас ```CharacterClassState(State)``` успідковує функціонал від абостактного класу та роширю цей функціонал. Він імітує стан автомата, який відповідає за сприймання таких наборів ```[abc]```, ```[a-z]```, ```[0-9_]``` тощо, які означають, що на цій позиції в рядку має стояти будь-який один символ з указаного набору або діапазону


```allowed_chars: set[str]:```  атрибут зберігає множину всіх окремих символів, які є дозволеними для цього конкретного класу символів. Використання множини забезпечує дуже ефективну перевірку приналежності символу до класу. Наприклад, для регулярного виразу ```[a-c1]``` цей атрибут буде містити ```{'a', 'b', 'c', '1'}```.


```self.allowed_chars = chars_in_class``` Приймає як аргумент множину символів ```chars_in_class``` і зберігає її в атрибуті екземпляра ```self.allowed_chars```. Таким чином, кожен екземпляр ```CharacterClassState``` "знає", який саме набір символів він має розпізнавати.


```check_self(self, char: str | None) -> bool```: Це основний логічний метод для ```CharacterClassState```. Він визначає, чи може поточний стан "прийняти" або "зіставитися" з наданим символом ```char```.


```if char is None: return False``` Спочатку перевіряється, чи не є переданий символ ```None```. Якщо так (наприклад, досягнуто кінця вхідного рядка, а стан очікує символ), то зіставлення неможливе, і метод повертає ```False```.

```return char in self.allowed_chars``` Якщо char не ```None```, то перевіряється, чи міститься цей символ у множині ```self.allowed_chars```. Якщо символ знайдено в множині, метод повертає True; інакше – ```False```


```python

class CharacterClassState(State):

    """State that implements character class matching (e.g., [a-z])."""


    def __init__(self, chars_in_class: set[str]):

        """

        Initialize a character class state with a set of allowed characters.


        Args:

            chars_in_class: Set of characters this state will match

        """

        super().__init__()

        self.allowed_chars = chars_in_class


    def check_self(self, char: str | None) -> bool:

        """

        Check if character is in the allowed set.


        Args:

            char: Character to check


        Returns:

            True if character is in the allowed set, False otherwise

        """

        if char is None:

            return False

        return char in self.allowed_chars

```


Основне тіло та програми  клас ```RegexFSM```. Допоки всі класи були лише описами станів, а клас RegexFSM є ```Context``` за патерном ```State```.


```self.start_node = StartState()``` Кожен скінченний автомат повинен мати початковий стан. ```self.start_node``` є точкою входу. Сам по собі StartState не відповідає жодному символу, а лише позначає початок.

```current_attach_point: State = self.start_node``` Ця змінна відстежує вузол атомата, до якого буде приєднаний наступний створений стан. Спочатку будь-який новий стан приєднується до списку ```next_states``` об'єкта ```self.start_node```. У міру побудови автомата ця змінна оновлюється, вказуючи на останній "головний" вузол у ланцюжку.

```last_direct_operand_node: State | None = None```  Вона зберігає посилання на останній створений стан, який представляє прямий операнд – тобто, стан, що відповідає конкретному символу ```AsciiState```, будь-якому символу ```DotState``` або класу символів ```CharacterClassState```.  Оператори ```*``` та ```+``` діють саме на такий попередній операнд. На початку ```None```, бо ще жодного операнда не оброблено.

```predecessor_of_last_direct_operand: State = self.start_node``` Ця змінна зберігає стан, який є попередником для ```last_direct_operand_node``` у ланцюжку скінч. автомата. Вона необхідна для коректної обробки операторів ```*``` та ```+```. Коли такий оператор застосовується до ```last_direct_operand_node```, нам потрібно змінити зв'язок: ```predecessor_of_last_direct_operand``` більше не повинен прямо вказувати на ```last_direct_operand_node```, а натомість на новий стан ```StarState (або PlusState)```, який "обгортає" ```last_direct_operand_node```.


```python
if not regex_expr:

            self.start_node.next_states.append(TerminationState())


            return
```

Якщо вхідний рядок ```regex_expr``` порожній, це означає, що такий регулярний вираз має відповідати лише порожньому рядку.
Цей цикл описує основний процес обробки повідомлення та переходів між станами. Оскільки у початковому коді був блок


(первинний код лабии)
```python
for char in regex_expr:
        tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
        prev_state.next_states.append(tmp_next_state)

```

То у цій імплементації також написано ітеративного через цикл While. Тобто ми вайлом пробігаємося по рядку та читаємо його

```char_token = regex_expr[idx]``` отримує поточний символ для аналізу.

```python

while idx < len(regex_expr):

            char_token = regex_expr[idx]

```


Цей блок відповідає за оброку [].

Зчитується весь вміст між [ та ] в class_content_str. Якщо закриваюча дужка ] не знайдена, викликається помилка ValueError.

Основний індекс idx пересувається на позицію після ].


Парситься вміст ```class_content_str```:


Визначаються діапазони (наприклад, a-z, 0-9). Усі символи з валідних діапазонів додаються до множини processed_chars.

Окремі символи (не частини діапазонів) також додаються до processed_chars.

Якщо після парсингу множина processed_chars порожня (наприклад, для [] або некоректного діапазону типу [z-a]), викликається помилка.

Створюється екземпляр ```CharacterClassSta```te з цією множиною



```python

            if char_token == "[":

                idx += 1

                class_content_start_idx = idx


                try:

                    class_content_end_idx = regex_expr.index(

                        "]", class_content_start_idx

                    )

                except ValueError:

                    raise ValueError("Character class '[' was not closed with ']'")


                class_content_str = regex_expr[

                    class_content_start_idx:class_content_end_idx

                ]

                idx = class_content_end_idx + 1


                processed_chars: set[str] = set()

                content_parse_idx = 0

                while content_parse_idx < len(class_content_str):

                    current_class_char = class_content_str[content_parse_idx]

                    if (

                        content_parse_idx + 2 < len(class_content_str)

                        and class_content_str[content_parse_idx + 1] == "-"

                    ):

                        start_range = current_class_char

                        end_range = class_content_str[content_parse_idx + 2]

                        if ord(start_range) <= ord(end_range):

                            for i_ord in range(ord(start_range), ord(end_range) + 1):

                                processed_chars.add(chr(i_ord))

                            content_parse_idx += 3

                            continue

                    processed_chars.add(current_class_char)

                    content_parse_idx += 1


                if not processed_chars:

                    raise ValueError("Empty character class '[]' is not allowed.")

```


```python
                new_node = CharacterClassState(processed_chars)

                current_attach_point.next_states.append(new_node)

                predecessor_of_last_direct_operand = current_attach_point

                last_direct_operand_node = new_node

                current_attach_point = new_node

```

Символ "крапка".

Логіка приєднання та оновлення змінних (```current_attach_point```, ```last_direct_operand_node```, ```predecessor_of_last_direct_operand```) аналогічна до ```CharacterClassState```.

```idx``` збільшується на 1.

```python

            elif char_token == ".":

                new_node = DotState()

                current_attach_point.next_states.append(new_node)

                predecessor_of_last_direct_operand = current_attach_point

                last_direct_operand_node = new_node

                current_attach_point = new_node

                idx += 1

            elif char_token.isascii() and char_token not in ["*", "+", ".", "["]:

                new_node = AsciiState(char_token)

                current_attach_point.next_states.append(new_node)

                predecessor_of_last_direct_operand = current_attach_point

                last_direct_operand_node = new_node

                current_attach_point = new_node

                idx += 1

```


Літеральний ASCII символ


Створюється ```AsciiState``` для поточного символу ```char_token```.

Логіка приєднання та оновлення змінних аналогічна. ```idx``` збільшується на 1.

```elif char_token.isascii() and char_token not in ["*", "+", ".", "[" ]```



Оператор "зірочка"

Перевіряється, чи існував попередній операнд (last_direct_operand_node). Якщо ні, це помилка (наприклад, * на початку виразу).

Створюється StarState, який як checking_state приймає last_direct_operand_node.

Ключовий момент – перебудова зв'язків:


Зі списку next_states стану predecessor_of_last_direct_operand видаляється пряме посилання на last_direct_operand_node.

Замість нього до predecessor_of_last_direct_operand.next_states додається новостворений star_node. Таким чином, StarState вбудовується в ланцюжок FSM, замінюючи прямий зв'язок на операнд.


current_attach_point оновлюється на star_node, оскільки наступні елементи регулярного виразу повинні йти після всієї конструкції з *.

last_direct_operand_node встановлюється в None. Це важливо, бо оператор * вже "спожив" попередній операнд. Якщо наступний символ теж буде оператором (наприклад, a**), це буде помилкою, оскільки * не може застосовуватися до іншого * без проміжного символьного стану. (Примітка: деякі рушії можуть мати іншу поведінку для a**, але для даної реалізації це логічно).

```idx``` збільшується на 1.

```python

            elif char_token == "*":

                if last_direct_operand_node is None:

                    raise ValueError(

                        "'*' operator must follow a character, '.', or class"

                    )

                star_node = StarState(last_direct_operand_node)

                if (

                    last_direct_operand_node

                    in predecessor_of_last_direct_operand.next_states

                ):

                    predecessor_of_last_direct_operand.next_states.remove(

                        last_direct_operand_node

                    )

                else:

                    raise Exception(

                        "FSM construction error: predecessor link lost for *"

                    )

                predecessor_of_last_direct_operand.next_states.append(star_node)

                current_attach_point = star_node

                last_direct_operand_node = None

                idx += 1


```

Оператор "плюс" у регулярних виразах означає "одне або більше повторень" попереднього елемента



```python

            elif char_token == "+":

                if last_direct_operand_node is None:

                    raise ValueError(

                        "'+' operator must follow a character, '.', or class"

                    )

                plus_node = PlusState(last_direct_operand_node)

                if (

                    last_direct_operand_node

                    in predecessor_of_last_direct_operand.next_states

                ):

                    predecessor_of_last_direct_operand.next_states.remove(

                        last_direct_operand_node

                    )

                else:

                    raise Exception(

                        "FSM construction error: predecessor link lost for +"

                    )

                predecessor_of_last_direct_operand.next_states.append(plus_node)

                current_attach_point = plus_node

                last_direct_operand_node = None

                idx += 1

            else:

                raise AttributeError(

                    f"Character '{char_token}' is not supported in FSM construction."

                )

```


після усішного виходу з While циклу відбувається побудова скінченого автомата.

```python

        current_attach_point.next_states.append(TerminationState())

        self.memo: dict[tuple[int, str], bool] = {}

```


У НСА є епсилон/лямбда переходи міє станами. Це переходи між станами, які автомат може здійснити не споживаючи жодного символу з вхідного рядка. Вони є "невидимими" кроками. Ці два стани можуть бути з'єднані, та розривати їх не можна. Оскільки такі переходи можуть поламати саму логіку побудови НСА, то потбіно це хендлети.

Нуль повторень": Найважливіший випадок. Якщо у вас є регулярний вираз типу ```a*b```, він має відповідати рядку ```b```. Це означає, що частина ```a*``` зіставляється з порожнім місцем (тобто, символ a зустрічається нуль разів). В автоматі це реалізується так: зі стану ```StarState```, що відповідає ```a*```, має бути епсилон-перехід до стану, що відповідає ```b```. Тобто, автомат може "перестрибнути" через логіку ```a*```, не читаючи символ.

"Більше повторень": Після того, як ```checking_state``` всередині ```StarState``` зіставився з символом, ```StarState``` концептуально залишається активним, щоб спробувати зіставити ще символи. Але також у цей момент він повинен мати можливість (через лямбда-перехід) перейти до станів, що йдуть після конструкції ```*```, якщо поточне входження було останнім




Метод реалізує алгоритм пошуку (схожий на пошук в ширину або глибину) для знаходження всіх станів, досяжних із початкової множини seed_states виключно через epsilon-переходи.

```closure = set()```: Порожня множина, куди будуть збиратися всі знайдені стани (результат роботи функції).

```states_to_visit = list(seed_states)``` Список станів, які потрібно відвідати та перевірити на наявність вихідних лямбда-переходів.

```visited_in_dfs = set()```: Множина для відстеження станів, які вже були повністю оброблені (тобто, всі їхні вихідні епсилон-переходи були розглянуті) в рамках одного виклику ```_get_epsilon_closure```. Це допомагає уникнути зациклення (якщо б в скінченному автоматі були епмилон-цикли) та зайвої роботи.

idx = 0: Індекс для ітерації по списку states_to_visit, імітуючи роботу черги.


Основний цикл ```while idx < len(states_to_visit)```

Цикл продовжується, доки є невідвідані стани в списку states_to_visit.

```current_s = states_to_visit[idx]``` Береться наступний стан для обробки.

```if current_s in visited_in_dfs: continue``` Якщо цей стан вже був повністю оброблений раніше в цьому ж виклику функції, він пропускається.

```visited_in_dfs.add(current_s)``` Стан позначається як оброблений.

```closure.add(current_s)``` Поточний стан ```current_s``` додається до множини ```closure``` (кожен стан є частиною власного епсилон/лямбда замикання через 0 епсилон-кроків).

Пошук epsilon-переходів з current_s:

```if isinstance(current_s, StartState)``` Якщо поточний стан – це ```StartState```, то всі стани, до яких він веде (```current_s.next_states```), досяжні через epsilon-перехід. Кожен такий ```next_s``` додається до списку ```states_to_visit``` (якщо він ще не був там або не був оброблений).

```elif isinstance(current_s, StarState)``` Якщо поточний стан – це ```StarState```, то всі стани, до яких він веде (```current_s.next_states```), досяжні через лямбда-перехід. Це моделює можливість "пропустити" ```StarState``` (зіставити нуль входжень ```checking_state```). Кожен такий next_s додається до ```states_to_visit```.











```python
def _get_epsilon_closure(self, seed_states: set[State]) -> set[State]:

        """

        Calculate epsilon closure for a set of states.


        Args:

            seed_states: Initial set of states


        Returns:

            Set of all states reachable without consuming any input

        """

        closure = set()

        states_to_visit = list(seed_states)

        visited_in_dfs = set()

        idx = 0

        while idx < len(states_to_visit):

            current_s = states_to_visit[idx]

            idx += 1

            if current_s in visited_in_dfs:

                continue

            visited_in_dfs.add(current_s)

            closure.add(current_s)

            if isinstance(current_s, StartState):

                for next_s in current_s.next_states:

                    if next_s not in visited_in_dfs:

                        states_to_visit.append(next_s)

            elif isinstance(current_s, StarState):

                for next_s in current_s.next_states:

                    if next_s not in visited_in_dfs:

                        states_to_visit.append(next_s)
```


```python
    def check_string(self, text_to_check: str) -> bool:

        """

        Check if a string matches the regex using an iterative approach.


        Args:

            text_to_check: String to check against the regex


        Returns:

            True if the string matches, False otherwise

        """

        if not self.start_node.next_states:

            return not text_to_check

        active_states = self._get_epsilon_closure({self.start_node.next_states[0]})

        for char_token in text_to_check:

            states_reachable_after_char = set()

            for current_s in active_states:

                if isinstance(current_s, (AsciiState, DotState, CharacterClassState)):

                    if current_s.check_self(char_token):

                        states_reachable_after_char.update(current_s.next_states)

                elif isinstance(current_s, StarState):

                    if current_s.checking_state.check_self(char_token):

                        states_reachable_after_char.add(current_s)

                elif isinstance(current_s, PlusState):

                    if current_s.checking_state.check_self(char_token):

                        states_reachable_after_char.add(current_s)

                        states_reachable_after_char.update(current_s.next_states)

            if not states_reachable_after_char:

                return False

            active_states = self._get_epsilon_closure(states_reachable_after_char)

        for final_s in active_states:

            if isinstance(final_s, TerminationState):

                return True

        return False

```



Обробка порожнього регулярного виразу:


```if not self.start_node.next_states:```  Якщо список наступних станів для ```start_node``` порожній, це означає, що регулярний вираз був порожнім при ініціалізації ```RegexFSM```.

```return not text_to_check:``` Порожній регулярний вираз відповідає тільки порожньому рядку. Якщо ```text_to_check``` порожній ```not text_to_check буде True```, повертається True. Інакше ```False```.



Головний цикл обробки символів (```for char_token in text_to_check```):


Цей цикл проходить по кожному символу char_token вхідного рядка text_to_check.

```states_reachable_after_char = set()``` На кожній ітерації створюється нова порожня множина. Вона буде накопичувати всі стани, в які скінченний автомат може перейти з будь-якого з поточних ```active_states``` після споживання поточного ```char_token```.

Внутрішній цикл ```for current_s in active_states:``` Для кожного стану current_s, який наразі є активним:

Випадок A: Прості стани (```AsciiState```, ```DotState```, ```CharacterClassState```):

```if current_s.check_self(char_token):``` Якщо поточний стан ```current_s``` може "прийняти" поточний символ ```char_token```.

```states_reachable_after_char.update(current_s.next_states):``` Якщо зіставлення успішне, то всі стани, які безпосередньо слідують за ```current_s```  додаються до ```states_reachable_after_char``` як можливі наступні стани.

Випадок B: StarState:

```if current_s.checking_state.check_self(char_token):``` Перевіряється, чи може внутрішній стан "зірочки" (```checking_state```) зіставитися з ```char_token```.

```states_reachable_after_char.add(current_s):``` Якщо так, то сам ```StarState (current_s)``` додається до ```states_reachable_after_char```. Це ключовий момент для оператора ```*``` він означає, що після споживання одного символу, що відповідає патерну під зірочкою, ми все ще перебуваємо "всередині" логіки * і можемо або зіставити ще один такий символ, або  перейти до станів, що йдуть після ```*```.

Випадок C: PlusState:

```if current_s.checking_state.check_self(char_token):``` Перевіряється, чи може внутрішній стан "плюса" (```checking_state```) зіставитися з ```char_token```.

```states_reachable_after_char.add(current_s)``` Якщо так, додаємо сам ```PlusState```. Це дозволяє обробити частину "більше" в "один або більше" (тобто, після першого успішного зіставлення, PlusState може поводитися подібно до ```StarState``` для наступних символів).

```states_reachable_after_char.update(current_s.next_states)``` Також додаємо всі стани, що йдуть після ```PlusState```. Це враховує випадок, коли поточний зіставлений символ був останнім необхідним для конструкції ```+``` (тобто, "один" в "один або більше", або останній у серії "більше").

- Випадок D: Перевірка на "мертвий кінець":

```if not states_reachable_after_char: return False``` Якщо після обробки поточного ```char_token``` не знайдено жодного стану, в який міг би перейти автомат, це означає, що рядок не відповідає регулярному виразу. Подальша перевірка не має сенсу.

- Випадок E: Оновлення ```active_states```:

```active_states = self._get_epsilon_closure(states_reachable_after_char)``` Перед переходом до наступного символу вхідного рядка, ми знову обчислюємо епсилон/лямбда замикання для множини ```states_reachable_after_char```. Це гарантує, що ```active_states``` завжди містить повний набір можливих станів, враховуючи всі миттєві (лямбда) переходи.


Кінцева перевірка (після циклу):


```for final_s in active_states:``` Після того, як усі символи з ```text_to_check``` були оброблені, ми переглядаємо всі стани, що залишилися в ```active_states```.

```if isinstance(final_s, TerminationState): return True``` Якщо серед них є хоча б один ```TerminationState```, це означає, що існує шлях через скінченний автомат, який відповідає всьому вхідному рядку. Отже, рядок відповідає регулярному виразу.

```return False``` Якщо жоден з активних станів не є ```TerminationState```, зіставлення не вдалося.


