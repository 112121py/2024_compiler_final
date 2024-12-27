from lark import Lark, Transformer, v_args, Tree
# 讀取語法文件
with open("grammar.lark", "r") as file:
    grammar_file = file.read()

# 定義 Lark 分析器
try:
    parser = Lark(grammar_file, start="start", parser="lalr", debug=True)
except Exception as e:
    # print("lark error")
    print("syntax error")
    exit(0)

# 定義 AST 節點類別
class NumberNode:
    def __init__(self, value):
        self.value = value

class VariableNode:
    def __init__(self, name):
        self.name = name

class BinaryOpNode:
    def __init__(self, op, left, *args):
        # print("def BinaryOpNode")
        self.op = op
        self.left = left
        self.args = args
        # print(op, left, args)

class LogicalOpNode:
    def __init__(self, op, *args):
        self.op = op
        self.args = args

class DefNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class FunDefNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FunCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class IfNode:
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class PrintNode:
    def __init__(self, value):
        self.value = value

# 上下文管理
class Context:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def def_variable(self, name, value):
        if name in self.variables:
            raise ValueError(f"Variable '{name}' already defined.")
        self.variables[name] = value

    def get_variable(self, name):
        if name not in self.variables:
            raise ValueError(f"Variable '{name}' is not defined.")
        return self.variables[name]

    def define_function(self, name, func):
        self.functions[name.name] = func
        # print("define_function success")
        # print(name.name, func)
        # print(self.functions)

    def get_function(self, name):
        if name.name not in self.functions:
            raise ValueError(f"Function '{name.name}' is not defined.")
        return self.functions[name.name]

# 定義 Transformer
@v_args(inline=True)
class MiniLispTransformer(Transformer):
    def __init__(self):
        self.context = Context()

    def start(self, *stmts):
        return list(stmts)

    def stmt(self, stmt):
        return stmt

    def exp(self, exp):
        return exp
    
    def params(self, *args):
        # 假設 args 是 ID 列表，直接返回名稱
        return [arg for arg in args]

    # 基本類型
    def BOOL(self, value):
        return value == "#t"

    def NUMBER(self, value):
        try:
            num = int(value)
            if num < -2147483648 or num > 2147483647:
                raise ValueError(f"Value '{value}' is out of range for a signed 32-bit integer.")
            return NumberNode(num)
        except ValueError:
            raise ValueError(f"Value '{value}' is out of range for a signed 32-bit integer.")

    def ID(self, value):
        return VariableNode(value)

    # 運算操作生成 AST 節點
    def plus(self, left, *args):
        # print("def plus")
        return BinaryOpNode("+", left, *args)

    def minus(self, left, right):
        return BinaryOpNode("-", left, right)

    def multiply(self, left, *args):
        return BinaryOpNode("*", left, *args)

    def divide(self, left, right):
        return BinaryOpNode("/", left, right)

    def module(self, left, right):
        return BinaryOpNode("%", left, right)

    def greater(self, left, right):
        return BinaryOpNode(">", left, right)

    def smaller(self, left, right):
        return BinaryOpNode("<", left, right)

    def equal(self, left, *args):
        return BinaryOpNode("=", left, *args)

    # bool操作
    def and_op(self, *args):
        return LogicalOpNode("and", *args)

    def or_op(self, *args):
        return LogicalOpNode("or", *args)

    def not_op(self, arg):
        return LogicalOpNode("not", arg)

    # 函數定義
    def fun_def(self, params, body):
        # print("fun_def")
        return FunDefNode("anonymous", params, body)
    
    def fun_call(self, fun_name, *args):
        #  print("fun_call")
         return FunCallNode(fun_name, list(args))

    def named_fun_def(self, name, params, body):
        # print("named_fun_def")
        # print(name.name)
        return FunDefNode(name, params, body)

    # 條件判斷
    def if_exp(self, condition, true_stmt, false_stmt):
        return IfNode(condition, true_stmt, false_stmt)

    # 定義變數
    def def_stmt(self, name, value):
        return DefNode(name.name, value)

    # 輸出指令
    def print_num(self, value):
        return PrintNode(value)

    def print_bool(self, value):
        return PrintNode(value)

# 解釋器
class Interpreter:
    def __init__(self):
        self.context = Context()

    def evaluate(self, node):
        # 處理節點列表的情況
        if isinstance(node, list):
            results = []
            for stmt in node:
                results.append(self.evaluate(stmt))
            return results
        
        # 處理bool值
        if isinstance(node, bool):  # 新增處理bool值的條件
            return node

        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, VariableNode):
            return self.context.get_variable(node.name)
        elif isinstance(node, BinaryOpNode):
            # print("interpreter BinaryOpNode")
            # 將運算結果返回，而不是打印
            # 
            # Ensure all operands are integers
            
            
            left = self.evaluate(node.left)
            
            # Ensure all operands are integers before evaluation

            results = [self.evaluate(arg) for arg in node.args]
            # print("results:", results)
            # print("type:", type(results[0]).__name__)
            # check all the results are int
            for result in results:
                if type(result).__name__ != "int":
                    print("Type Error")
                    exit(0)

            # print("left:", left)
            if node.op == "+":
                return left + sum(results)
            elif node.op == "-":
                return left - results[0]
            elif node.op == "*":
                result = left
                for r in results:
                    result *= r
                return result
            elif node.op == "/":
                return left // results[0]
            elif node.op == "%":
                return left % results[0]
            elif node.op == ">":
                return left > results[0]
            elif node.op == "<":
                return left < results[0]
            elif node.op == "=":
                return all(left == r for r in results)
        elif isinstance(node, LogicalOpNode):
            results = [self.evaluate(arg) for arg in node.args]
            # Ensure all operands are booleans
            # print("results:", results)
            # print("type:", type(results[0]).__name__)
            # check all the results are bool
            for result in results:
                if type(result).__name__ != "bool":
                    print("Type Error")
                    exit(0)

            if node.op == "and":
                return all(results)
            elif node.op == "or":
                return any(results)
            elif node.op == "not":
                return not results[0]
        elif isinstance(node, DefNode):
            # print("DefNode")
            self.context.def_variable(node.name, self.evaluate(node.value))
        elif isinstance(node, FunDefNode):
            # print("FunDef Node")
            self.context.define_function(node.name, node)
        elif isinstance(node, FunCallNode):
            # print("FunCallNode")
            if isinstance(node.name, FunDefNode):
                func = node.name
            else:
                func = self.context.get_function(node.name)
            
            if not isinstance(func, FunDefNode):
                raise ValueError(f"{node.name} is not a function.")

            # 設定局部上下文，覆蓋參數
            local_context = Context()
            for param, arg in zip(func.params, node.args):
                local_context.def_variable(param.name, self.evaluate(arg))

            # 執行函數內容
            previous_context = self.context
            self.context = local_context
            result = self.evaluate(func.body)
            self.context = previous_context
            # print(type(result).__name__)
            return result

        elif isinstance(node, IfNode):

            condition = self.evaluate(node.condition)
            return self.evaluate(node.true_branch if condition else node.false_branch)
        elif isinstance(node, PrintNode):
            value = self.evaluate(node.value)
            # 如果是bool值，返回 #t 或 #f
            if isinstance(value, bool):
                print("#t" if value else "#f")
            else:
                print(value)
            return None
        else:
            print(f"Unknown node: {node}")

# 主程式
def run_code(code):
    try:
        tree = parser.parse(code)
        # print(tree.pretty())  # 印語法樹結構
        transformer = MiniLispTransformer()
        # print("transformer")
        ast = transformer.transform(tree)
        # print("transformer end")
        interpreter = Interpreter()
        results = interpreter.evaluate(ast)
        # 如果結果是列表，逐一輸出
        # print("here")
        # if isinstance(results, list):
        #     for result in results:
        #         if result is not None:  # 避免輸出 None 結果
        #             print(result)
        # else:
        #     if results is not None:
        #         print(results)
    except Exception as e:
        # print("run_code error")
        print("syntax error")
        exit(0)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mini_lisp.py <file.lsp>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, "r") as file:
        code = file.read()

    run_code(code)
