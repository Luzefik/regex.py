from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    _id_c = 0

    def __init__(self) -> None:
        self.id = State._id_c
        State._id_c += 1
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str | None) -> bool:
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        return self.id == other.id


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str | None) -> bool:
        return False


class TerminationState(State):
    def __init__(self) -> None:
        super().__init__()

    def check_self(self, char: str | None) -> bool:
        return False


class DotState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str | None) -> bool:
        return char is not None


class AsciiState(State):
    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str | None) -> bool:
        return curr_char == self.curr_sym


class StarState(State):
    next_states: list[State] = []
    checking_state: State

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char: str | None) -> bool:
        return self.checking_state.check_self(char)


class PlusState(State):
    next_states: list[State] = []
    checking_state: State

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char: str | None) -> bool:
        return self.checking_state.check_self(char)


class RegexFSM:
    curr_state: State

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()

        prev_linking_state = self.curr_state
        current_operand_state = self.curr_state

        if not regex_expr:
            self.curr_state.next_states.append(TerminationState())
            self.memo: dict[tuple[int, str], bool] = {}
            return

        for token in regex_expr:
            newly_created_state = self.__init_next_state(
                token, prev_linking_state, current_operand_state
            )
            prev_linking_state.next_states.append(newly_created_state)

            if token not in ["*", "+"]:
                prev_linking_state = newly_created_state

            current_operand_state = newly_created_state
        current_operand_state.next_states.append(TerminationState())
        self.memo = {}

    def __init_next_state(
        self, next_token: str, prev_state_arg: State, operand_state_arg: State
    ) -> State:
        new_state_obj = None

        match next_token:
            case t if t == ".":
                new_state_obj = DotState()
            case t if t == "*":
                if (
                    operand_state_arg is self.curr_state
                    and not self.curr_state.next_states
                ):
                    raise ValueError("'*' operator must follow a character or '.'")
                new_state_obj = StarState(operand_state_arg)
            case t if t == "+":
                if (
                    operand_state_arg is self.curr_state
                    and not self.curr_state.next_states
                ):
                    raise ValueError("'+' operator must follow a character or '.'")
                new_state_obj = PlusState(operand_state_arg)
            case t if t.isascii() and t not in ["*", "+", "."]:
                new_state_obj = AsciiState(t)
            case _:
                raise AttributeError(f"Character '{next_token}' is not supported")

        if new_state_obj is None:
            return f"Failed to create state for token '{next_token}'"

        return new_state_obj

    def _match_recursive(self, current_processing_node: State, text_slice: str) -> bool:
        memo_key = (current_processing_node.id, text_slice)
        if memo_key in self.memo:
            return self.memo[memo_key]

        if isinstance(current_processing_node, TerminationState):
            result = text_slice == ""
            self.memo[memo_key] = result
            return result
        if isinstance(current_processing_node, StarState):
            for next_node_candidate in current_processing_node.next_states:
                if self._match_recursive(next_node_candidate, text_slice):
                    self.memo[memo_key] = True
                    return True

        if not text_slice:
            self.memo[memo_key] = False
            return False

        current_char_from_text = text_slice[0]
        remaining_text_slice = text_slice[1:]

        if isinstance(current_processing_node, (AsciiState, DotState)):
            if current_processing_node.check_self(current_char_from_text):
                for next_node_candidate in current_processing_node.next_states:
                    if self._match_recursive(next_node_candidate, remaining_text_slice):
                        self.memo[memo_key] = True
                        return True
        elif isinstance(current_processing_node, StarState):
            if current_processing_node.checking_state.check_self(
                current_char_from_text
            ):
                if self._match_recursive(current_processing_node, remaining_text_slice):
                    self.memo[memo_key] = True
                    return True

        elif isinstance(current_processing_node, PlusState):
            if current_processing_node.checking_state.check_self(
                current_char_from_text
            ):

                if self._match_recursive(current_processing_node, remaining_text_slice):
                    self.memo[memo_key] = True
                    return True

                for next_node_candidate in current_processing_node.next_states:
                    if self._match_recursive(next_node_candidate, remaining_text_slice):
                        self.memo[memo_key] = True
                        return True

        self.memo[memo_key] = False
        return False

    def check_string(self, text_to_check: str) -> bool:
        self.memo.clear()
        if not self.curr_state.next_states:
            return not text_to_check
        return self._match_recursive(self.curr_state.next_states[0], text_to_check)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))
    print(regex_compiled.check_string("4uhi"))
    print(regex_compiled.check_string("a4uhi"))  # Для a*4... це має бути True
    print(regex_compiled.check_string("meow"))

    print("--- Pattern: 'a+' ---")
    regex_plus = RegexFSM("a+")
    print(f"'a': {regex_plus.check_string('a')}")  # True
    print(f"'aaa': {regex_plus.check_string('aaa')}")  # True
    print(f"Empty: {regex_plus.check_string('')}")  # False
    print(f"'b': {regex_plus.check_string('b')}")  # False

    print("--- Pattern: '.*c' ---")
    regex_dot_star_c = RegexFSM(".*c")
    print(f"'abc': {regex_dot_star_c.check_string('abc')}")  # True
    print(f"'c': {regex_dot_star_c.check_string('c')}")  # True
    print(f"'abb': {regex_dot_star_c.check_string('abb')}")  # False

    print("--- Pattern: '' ---")
    regex_empty_str = RegexFSM("")
    print(f"Empty: {regex_empty_str.check_string('')}")  # True
    print(f"'a': {regex_empty_str.check_string('a')}")  # False
