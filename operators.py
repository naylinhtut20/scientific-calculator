import operator
import ast
import os
import json
import math

_Operator = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv
}

_ALLOWED_FUNC = {
    "sqrt": lambda  x: math.sqrt(float(x)),
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "fact": math.factorial
}

_ALLOWED_CONSTS = {
    "pi": math.pi,
    "e": math.e
}

file_path = "history.json"

def load_histories():
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as r:
                data = json.load(r)
                if isinstance(data, list):
                    return data
                else:
                    return []
        except json.JSONDecodeError:
            return []
    return []

def add_history(histories):
    with open(file_path, "w") as w:
        json.dump(histories, w, indent=4)

def eval_node(node):
    if isinstance(node, ast.BinOp):
        left = eval_node(node.left)
        right = eval_node(node.right)
        op_type = type(node.op)
        if op_type in _Operator:
            return _Operator[op_type](left, right)
        else:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")

    if isinstance(node, ast.UnaryOp):
        operand = eval_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op,  ast.USub):
            return -operand
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTS:
            return _ALLOWED_CONSTS[node.id]
        raise ValueError("Unknown constant")

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            name = node.func.id

            if name in _ALLOWED_FUNC:
                args = [eval_node(a) for a in node.args]
                return _ALLOWED_FUNC[name](*args)

        raise ValueError("Unsupported function")

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        else:
            raise ValueError("Only numeric constants are allowed")


    if hasattr(ast, 'Num') and isinstance(node, ast.Num):
        return node.n

    raise ValueError(f"Unsupported expression: {type(node).__name__}")

def eval_expr(expr):
    parsed = ast.parse(expr, mode='eval')
    return eval_node(parsed.body)

def main():
    print("Calculator (type 'q' to quit) or (type 'history' to see history)")
    histories = load_histories()
    if len(histories) > 20:
        histories.pop(0)
        add_history(histories)

    while True:
        s = input("Enter expression: ").strip()
        if s.lower() in ('q', 'quit', 'exit'):
            print("Bye")
            break
        if s.lower() in ('h', 'history', 'histories'):
            print("\nHistory: ")
            for i, t in enumerate(histories, start=-1):
                print(f"{t['expression']} = {t['answer']}")
            continue

        if not s:
            continue
        try:
            value = eval_expr(s)
            print("Result:", value)
            histories.append({
                "expression": s, "answer": value
            })

            add_history(histories)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()






