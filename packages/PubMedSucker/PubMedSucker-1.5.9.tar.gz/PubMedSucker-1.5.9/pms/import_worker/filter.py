# ToDo: Rewrite with https://boolean-parser.readthedocs.io/en/latest/intro.html#id1 or https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html

import re
from Configs import getConfig
import logging
from dict2graph import Dict2graph
import operator
from typing import Any, Callable, Union, Dict, List

config = getConfig()
log = logging.getLogger("FilterLOgger")

# sequence of the operators in this dict is important, as we first parse multi char operators
COMPARISON_OPERATOR_DICT: Dict[str, Callable[[Any, Any], bool]] = {
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    "=": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
    " in ": lambda left, right: left in right,
    " not in ": lambda left, right: left not in right,
}

LOGICAL_OPERATOR_DICT: Dict[str, Callable[[Any, Any], bool]] = {
    " and ": lambda left, right: left and right,
    " or ": lambda left, right: left or right,
}


class Filter(object):
    def __init__(
        self,
        filter_rules: Union["Filter.FilterRuleGroup", "Filter.FilterRule", str] = None,
    ):
        if isinstance(filter_rules, str):
            self.Deserializer.from_string(filter_rules, filter=self)
        else:
            self.filter_rules = filter_rules

    def pass_filter(self, article_parser: Dict2graph):
        self.data = article_parser._current_nodes
        return bool(self.filter_rules)

    class FilterRule(object):
        filter = None

        def __init__(
            self,
            filter: "Filter",
            node_label: str,
            prop_name: Union[str, List[str]],
            op: Callable[[Any, Any], bool],
            prop_value: Union[str, int, List[str], List[int]],
        ):
            self.filter = filter
            if isinstance(op, str):
                operator = COMPARISON_OPERATOR_DICT[op]
            else:
                operator = op
            if operator not in list(COMPARISON_OPERATOR_DICT.values()):
                raise ValueError(
                    f"Can not create FilterRule. Unknown operator. Expected {list(COMPARISON_OPERATOR_DICT.keys())} got '{op}'"
                )
            self.op_func: Callable[[Any, Any], Any] = operator
            self.node_label = node_label

            self.prop_name = [prop_name] if isinstance(prop_name, str) else prop_name
            self.prop_value = (
                [prop_value] if isinstance(prop_value, str) else prop_value
            )

            if len(self.prop_name) != len(self.prop_value):
                raise ValueError(
                    f"'{self}' is corrupt. Expected same amount of properties and values."
                )

        def __repr__(self) -> str:
            op_str = list(COMPARISON_OPERATOR_DICT.keys())[
                list(COMPARISON_OPERATOR_DICT.values()).index(self.op_func)
            ]
            if len(self.prop_name) == 1:
                prop = self.prop_name[0]
                val = (
                    self.prop_value[0]
                    if isinstance(self.prop_value[0], (float, int))
                    else f"'{self.prop_value[0]}'"
                )
            else:
                prop = self.prop_name
                val = [
                    v if isinstance(v, (float, int)) else f"'{v}'"
                    for v in self.prop_value
                ]
            return f"{self.node_label}.{prop} {op_str} {val}"

        def __str__(self) -> str:
            return self.__repr__()

        def __bool__(self):
            # actual evaluation of rule applied to data

            # get all nodes matching the label configured in the FilterRule
            nodes = self.filter.data.get(frozenset([self.node_label]), [])
            log.debug(frozenset([self.node_label]))
            log.debug(nodes)

            # Throw these nodes in the filter one by one
            log.debug(f"Check {len(nodes)}")
            for node in nodes:
                # Atm we only apply an "or" logic to a filter. if one of the nodes is true the filter returns true
                if self._resolve_filter(node):
                    return True
            return False

        def _resolve_filter(self, node):
            for index, prop in enumerate(self.prop_name):
                log.debug(f"Check prop {prop}")
                # Check if one of the nodes with a certain label has the expected props and values
                if prop in node:
                    log.debug(
                        f"  {node[prop]} to {self.prop_value[index]} results in {self.op_func(node[prop], self.prop_value[index])}"
                    )
                    if not self.op_func(node[prop], self.prop_value[index]):
                        return False
                else:
                    return False
            return True

    class FilterRuleGroup(object):
        def __init__(
            self,
            filter_rules: List[
                Union["Filter.FilterRule", "Filter.FilterRuleGroup"]
            ] = None,
            operator: str = None,
            parenthesis_group: bool = False,
        ):
            self.op_func = None
            if operator:
                self.operator(operator)
            if filter_rules is None:
                filter_rules = []
            elif not isinstance(filter_rules, list):
                filter_rules = [filter_rules]
            self.rules = filter_rules
            self.parenthesis_group = parenthesis_group

        def operator(self, op: str):
            oper = None
            if op in [" and ", "and", "&", "&&"]:
                oper = LOGICAL_OPERATOR_DICT[" and "]
            if op in [" or ", "or", "|", "||"]:
                oper = LOGICAL_OPERATOR_DICT[" or "]
            if oper is None:
                raise ValueError(
                    f"Unknown rule chain operator. Expected 'and','or' got '{op}'"
                )
            self.op_func = oper

        def get_operator_str(self):
            if self.op_func:
                return list(LOGICAL_OPERATOR_DICT.keys())[
                    list(LOGICAL_OPERATOR_DICT.values()).index(self.op_func)
                ]
            else:
                return None

        def add_rule(self, rule: "Filter.FilterRule"):
            self.rules.append(rule)

        def __repr__(self) -> str:
            op_func = str(self.get_operator_str())
            s = ""
            if self.parenthesis_group:
                s += "("
            s += f"{op_func.join([str(rule) for rule in self.rules])}"
            if self.parenthesis_group:
                s += ")"
            return s

        def __str__(self) -> str:
            return self.__repr__()

        def __bool__(self):
            # Check for sanity. If error occures here, there is possible a bug in the Filter.Deserializer
            if not self.op_func and len(self.rules) > 1:
                raise ValueError(f"Rule group {self} has no logical operator.")
            if not self.rules:
                raise ValueError("Rule group has no rules.")
            # run filter rule group

            operator = self.get_operator_str()
            log.debug(f'Run {str(operator).upper()}-rules "{self.rules}"')
            if operator == " or ":
                return any(self.rules)
            elif operator == " and ":
                return all(self.rules)
            elif len(self.rules) == 1:
                return bool(self.rules[0])
            else:
                raise ValueError(f"Something is wrong with rule group '{self}'")

    class Deserializer(object):
        def __init__(self, filter: "Filter" = None):
            if filter is None:
                self.filter = Filter()
            elif isinstance(filter, Filter):
                self.filter = filter
            else:
                raise ValueError(f"Expected None or Filter type got {type(filter)}")

        def eat(self, data):
            self.filter_serialized = data

        def run(self):
            paranthesis_groups = self._seperate_parenthesis_groups(
                self.filter_serialized
            )
            logical_groups = self._split_logical_groups(paranthesis_groups)
            implicit_logical_groups = self._resolve_implicit_brackets(logical_groups)
            return self._parse_logical_groups(implicit_logical_groups)

        @classmethod
        def from_string(
            cls, filter_rules_string: str, filter: "Filter" = None
        ) -> "Filter":
            des = cls(filter)
            des.eat(filter_rules_string)
            filter.filter_rules = des.run()
            return filter

        def _seperate_parenthesis_groups(self, filter_rules_string) -> List[str]:
            def _concatenate_list(lst):
                conc_sub_list = []
                conc_str = ""
                for item in lst:
                    if isinstance(item, list):
                        conc_sub_list.append(conc_str)
                        conc_str = ""
                        conc_sub_list.append(_concatenate_list(item))
                    else:
                        conc_str += item
                if conc_str:
                    conc_sub_list.append(conc_str)
                return conc_sub_list

            # Parse and group parenthesis
            rule_groups = []
            current_group = rule_groups
            parent_group = None
            grandparent_group = None
            for c in filter_rules_string:
                if c == "(":
                    new_group = []
                    current_group.append(new_group)
                    grandparent_group = parent_group
                    parent_group = current_group
                    current_group = new_group
                elif c == ")":
                    current_group = parent_group
                    parent_group = grandparent_group
                else:
                    current_group += c
            return _concatenate_list(rule_groups)

        def _split_logical_groups(self, parenthesis_groups: List):
            new_list = []
            # print("parenthesis_groups", parenthesis_groups)
            for group in parenthesis_groups:
                if isinstance(group, list):
                    new_list.append(self._split_logical_groups(group))
                elif any(log_op in group for log_op in LOGICAL_OPERATOR_DICT.keys()):
                    # split group with one or more logical operators (and, or) into multiple groups
                    # "foo==2 and bar==1" -> ["foo==2","and", "bar==1"]
                    new_list.extend(
                        re.split(f"({'|'.join(LOGICAL_OPERATOR_DICT.keys())})", group)
                    )
                else:
                    new_list.append(group)
            new_list.reverse()
            return [x for x in new_list if x]  # hack to remove empty entries

        def _parse_logical_groups(
            self, parenthesis_groups: List, implicit_parenthesis=False
        ):
            current_group = Filter.FilterRuleGroup(
                parenthesis_group=not implicit_parenthesis
            )
            for token in parenthesis_groups:
                if token in list(LOGICAL_OPERATOR_DICT.keys()):
                    if current_group.get_operator_str() is None:
                        current_group.operator(token)
                    elif current_group.get_operator_str() != token:
                        raise ValueError(
                            f"Mixed operators in group '{parenthesis_groups}'. Possible a bug in Filter.Deserializer._resolve_implicit_brackets() or syntax error in the filter."
                        )
                elif isinstance(token, list):
                    # step recoursive into child groups and add to current group
                    current_group.add_rule(
                        self._parse_logical_groups(token, implicit_parenthesis=False)
                    )
                    # child_groups.append(self._parse_logical_groups(group))
                elif isinstance(token, tuple):
                    current_group.add_rule(
                        self._parse_logical_groups(token, implicit_parenthesis=True)
                    )
                else:
                    current_group.add_rule(self._parse_rule(token))
            return current_group

        def _resolve_implicit_brackets(self, parenthesis_groups):
            last_operator = None
            current_group = []
            current_sub_group = None
            for token in parenthesis_groups:
                if token == " and " and last_operator == " or ":
                    # we have a operator change to "and". we need to build a subgroup
                    current_sub_group = [current_group.pop()]
                    current_sub_group.append(token)
                    last_operator = token
                elif token == " or " and last_operator == " and ":
                    # we have a operator change to "or". we need to put past tokens in a subgroup or a close an opened subgroup
                    if current_sub_group is None:
                        current_group = [current_group, token]
                    elif current_sub_group:
                        current_group.append(tuple(current_sub_group))
                        current_group.append(token)
                        current_sub_group = None
                    last_operator = token
                elif token in [" and ", " or "]:
                    if current_sub_group:
                        current_sub_group.append(token)
                    else:
                        current_group.append(token)
                    last_operator = token
                else:
                    if isinstance(token, list):
                        statement = self._resolve_implicit_brackets(token)
                    else:
                        statement = token
                    if current_sub_group is None:
                        current_group.append(statement)
                    else:
                        current_sub_group.append(statement)
            # close/append leftover open subgroups
            if current_sub_group is not None:
                current_group.append(tuple(current_sub_group))
            return current_group

        def _parse_rule(self, rule_str: str) -> "Filter.FilterRule":
            operator_str = None
            left = None
            right = None

            for op in COMPARISON_OPERATOR_DICT.keys():
                if op in rule_str:
                    operator_str = op
                    left, right = rule_str.split(op)
                    break
            if None in (operator_str, left, right):
                raise ValueError(
                    f"Can not parse filter rule expected '<left> <operator> <right>' pattern. Got '{rule_str}'"
                )
            label, prop = left.replace('"', "").replace("'", "").split(".")
            operator = COMPARISON_OPERATOR_DICT[operator_str]
            prop = prop.strip().strip('"')
            label = label.strip()
            right = right.strip().strip('"')

            if prop.startswith("[") and prop.endswith("]"):
                prop = prop.strip("[").strip("]")
                prop = prop.split(",")
                prop = [p.strip().strip('"') for p in prop]
                right = right.strip("[").right("]")
                right = re.split(r',(?=")', right)
                right = [r.strip().strip('"') for r in right]
            return Filter.FilterRule(
                filter=self.filter,
                node_label=label,
                prop_name=prop,
                op=operator,
                prop_value=right,
            )


# "MyNode"."MyProp"=="12" or "MyNode"."MyProp"=="13"
# ("MyNode"."MyProp"=="12" or "MyNode"."MyProp"=="13") and "MyNode2"."MyProp2"=="Hello"


#
# rule = 'A1.B=="1Hello" or (MyNode.MyProp==12 or (MyNode.MyProp==13 and MyOtherNode.prop99="waaaass")) and MyNode2.MyProp2=="Hello"'
# res =  [['MyNode2.MyProp2=="Hello"', ' and ', [['MyOtherNode.prop99="waaaass"', ' and ', 'MyNode.MyProp==13'], ' or ', 'MyNode.MyProp==12']], ' or ', 'A1.B=="1Hello"']
# rule = 'a==23 and (b=="sd" and f==True) or c=="d" and (a==23 and (d>3 or f=="sd"))'
# rule = "True and False or True"  # any([all([True,False]),True])
# rule = "True and False and True"  # all([True,False,True])
# print(json.dumps(Filter.from_string(rule), indent=5,))
# rule = "Keyword in ['Laptop']"
# rule = '"Author".[Forename,LastName]==["Fred","Miller"] and Article.id in [12,34,56]'
# rule = '["Fred","Miller"] in Author.[Forename,LastName]'
# rule = '"Fred" in Author.Forename and "Miller" in Author.LastName'
# rule = '"Fred" in Author.Forename and "Miller" in Author.LastName'

# from boolean_parser import parse


# rule = '(Z0.Y0 == "whateva" and A1.B1 == "1Hello") and C2.A2 <= "2wtf" or D3.F3 > 23'
# print(rule)
# print(Filter.Deserializer.from_string(rule))
# print("")

# res = parse(rule)
# print(rule)
# print(res)
# print("")
# rule = 'A1.B1 == "1Hello" and C2.A2 <= "2wtf" or D3.F3 > 23'
# res = parse(rule)
# print(rule)
# print(res)
# print(rule)
# print(Filter.Deserializer.from_string(rule))
# print(rule)

# rule = '(A1.B=="1Hello" or MyNode.MyProp==12) or (MyNode.MyProp==13 and MyOtherNode.prop99="waaaass") and MyNode2.MyProp2=="Hello"'
# print(rule)
# print(Filter.Deserializer.from_string(rule))
# print("")
