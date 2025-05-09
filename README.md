# regex.py
У цій лабораторній роботі було імлементовано імітацію роботи недетермінованого скінченного автомата (НСА) для сприймання Regex.
## Стани Автомата
Імлементація програми базується на патерні програмування State, тому було реалізовані окермі стани, які й імітують стани в НСА.

Тобто, коли ми отримуємо стірчку з regex, то ми постійно переходимо в різні стани. Ці стани реалізовані як окремі класи, що відповідає патерну State


Усі класи за принципом ООП поліморфізму успадковуються від абстрактного класу ```State(ABC)```.

Метод ```check_next()``` реалізовано в базовому класі, оскільки логіка пошуку наступного стану однакова для всіх станів
Поле ```next_states``` визначено в базовому класі, оскільки всі стани повинні мати можливість переходу до інших станів

```
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



```
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
```
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

```

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

    Логіка: Це ключовий метод для AsciiState. Він перевіряє, чи відповідає вхідний символ curr_char тому символу, який зберігається в self.curr_sym.
    return curr_char == self.curr_sym: Якщо curr_char ідентичний self.curr_sym, метод повертає True (символ розпізнано). В іншому випадку (включаючи, якщо curr_char є None), він повертає False.

```

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



Клас StarState реалізує логіку оператора Кліні (зірочка *) в регулярних виразах. Оператор * застосовується до попереднього елемента (представленого checking_state) і означає "нуль або більше повторень" цього елемента. Наприклад, a* означає нуль або більше символів a.
Цей клас такоє успідкоується від абстарктного, проте потрвім виокремити

Метод check_self(self, char: str | None) -> bool:

    Логіка: Цей метод у StarState делегує перевірку символу char методу check_self свого внутрішнього стану self.checking_state.
    return self.checking_state.check_self(char): Тобто, StarState.check_self поверне True, якщо символ char може бути зіставлений патерном, до якого застосована зірочка.
Важливе зауваження: Сам по собі цей метод check_self не реалізує повну логіку "нуль або більше". Він лише відповідає на питання: "чи може елемент, що повторюється, зіставитися з цим конкретним символом?". Повна логіка оператора * (включаючи можливість нульового зіставлення, множинні зіставлення та перехід до наступних станів після *) зазвичай реалізується в основному алгоритмі зіставлення рядка в класі RegexFSM (наприклад, в check_string_iterative або _match_recursive).

```
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


Клас PlusState реалізує логіку оператора + (плюс) в регулярних виразах. Оператор + застосовується до попереднього елемента (checking_state) і означає "одне або більше повторень" цього елемента. Наприклад, a+ означає один або більше символів a.
Логіка: Подібно до StarState, цей метод делегує перевірку символу char методу check_self свого внутрішнього стану self.checking_state.
return self.checking_state.check_self(char): Повертає True, якщо символ char може бути зіставлений патерном, до якого застосовано плюс.



Важливе зауваження: Як і у випадку з StarState, метод check_self для PlusState не реалізує повну логіку "одне або більше". Він лише перевіряє, чи може елемент, що повторюється, зіставитися з поточним символом. Повна логіка + (обов'язкове перше зіставлення, потім можливі наступні, та перехід далі) реалізується в основному алгоритмі зіставлення в RegexFSM.
```

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

StarState та PlusState є "обгортками" для інших станів (checking_state), що дозволяють реалізувати логіку повторень. Їхні методи check_self лише перевіряють, чи може базовий елемент (checking_state) зіставитися з символом. Повна семантика операторів * (нуль або більше) та + (один або більше), включаючи управління кількістю повторень та переходи, реалізується на вищому рівні – в алгоритмі обходу скінченного автомата (наприклад, у методі check_string класу RegexFSM).


```
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