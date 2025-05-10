from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """Base abstract class for all states in the Finite State Machine."""

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


class RegexFSM:
    """
    Finite State Machine implementation for regular expressions.

    Supports basic regex features: literal characters, dot (.), star (*),
    plus (+), and character classes [].
    """

    def __init__(self, regex_expr: str) -> None:
        """
        Initialize the FSM by parsing the regex expression.

        Args:
            regex_expr: Regular expression to parse

        Raises:
            ValueError: For invalid regex syntax
            AttributeError: For unsupported characters
            Exception: For internal FSM construction errors
        """
        self.start_node = StartState()
        current_attach_point: State = self.start_node
        last_direct_operand_node: State | None = None
        predecessor_of_last_direct_operand: State = self.start_node

        if not regex_expr:
            self.start_node.next_states.append(TerminationState())

            return

        idx = 0
        while idx < len(regex_expr):
            char_token = regex_expr[idx]

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

                new_node = CharacterClassState(processed_chars)
                current_attach_point.next_states.append(new_node)
                predecessor_of_last_direct_operand = current_attach_point
                last_direct_operand_node = new_node
                current_attach_point = new_node

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

        current_attach_point.next_states.append(TerminationState())
        self.memo: dict[tuple[int, str], bool] = {}

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
        return closure


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


if __name__ == "__main__":
    test_suite = {
        "": {"": True, "a": False},
        "a*": {"": True, "a": True, "aa": True, "aaaaa": True, "b": False, "ba": False},
        "a*b": {"b": True, "ab": True, "aaab": True, "bb": False, "a": False},
        ".*": {"": True, "abc": True, "123": True, " ": True},
        ".*c": {
            "c": True,
            "abc": True,
            "cccc": True,
            "ac": True,
            "ca": False,
            "ab": False,
        },
        "a+": {"a": True, "aa": True, "aaaaa": True, "": False, "b": False},
        ".+c": {"ac": True, "absc": True, "c": False, "cc": True},
        "[abc]": {"a": True, "b": True, "c": True, "d": False, "": False},
        "[a-c]": {"a": True, "b": True, "c": True, "d": False},
        "h[aeiou]llo": {
            "hallo": True,
            "hello": True,
            "hillo": True,
            "hollo": True,
            "hullo": True,
            "h llo": False,
        },
        "a*4.+hi": {
            "aaaaaa4uhi": True,
            "4uhi": True,
            "a4uhi": True,
            "meow": False,
            "4ahia": False,
            "a*4bhi": False,
            "a4b": False,
        },
        "ab*c+d": {
            "acd": True,
            "abcd": True,
            "abbcd": True,
            "acccd": True,
            "abbcccd": True,
            "ad": False,
            "abd": False,
            "ac": False,
        },
        "[a-c-e]": {
            "a": True,
            "b": True,
            "c": True,
            "-": True,
            "e": True,
            "d": False,
            "f": False,
        },
    }

    overall_passed = 0
    overall_failed = 0
    overall_total = 0

    for pattern, tests in test_suite.items():
        print(f"\n--- Regex: '{pattern}' ---")
        passed_count = 0
        failed_count = 0

        regex_fsm_instance = RegexFSM(pattern)
        for test_string, expected_result in tests.items():
            overall_total += 1
            actual_result = regex_fsm_instance.check_string(test_string)
            status_char = "✅" if actual_result == expected_result else "❌"
            if actual_result == expected_result:
                passed_count += 1
                overall_passed += 1
            else:
                failed_count += 1
                overall_failed += 1
            print(
                f"String: '{test_string}', Expected: {expected_result}, Got: {actual_result} {status_char}"
            )
        print(f"Pattern summary: Passed: {passed_count}, Failed: {failed_count}")