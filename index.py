import re

TOKEN_TYPES = [
    ('NUMBER', r'\d+'),
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    ('ASSIGN', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MULTIPLY', r'\*'),
    ('DIVIDE', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'), 
]

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.tokens = []

    def tokenize(self):
        while self.pos < len(self.code):
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    if token_type != 'SKIP':
                        self.tokens.append(Token(token_type, value))
                    self.pos = match.end()
                    break
            else:
                raise SyntaxError(f'Unexpected character: {self.code[self.pos]}')
        return self.tokens

class ASTNode:
    pass

class Number(ASTNode):
    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return f'Number({self.value})'

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Identifier({self.name})'

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'BinOp({self.left}, {self.op}, {self.right})'

class Assign(ASTNode):
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    def __repr__(self):
        return f'Assign({self.identifier}, {self.expr})'

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        statements = []
        while self.current_token().type != 'EOF':
            if self.current_token().type == 'NEWLINE':
                self.consume('NEWLINE')  # Skip newlines
            else:
                statements.append(self.assignment())
        return statements

    def assignment(self):
        identifier = self.identifier()
        self.consume('ASSIGN')
        expr = self.expr()
        return Assign(identifier, expr)

    def expr(self):
        node = self.term()
        while self.current_token().type in ('PLUS', 'MINUS'):
            op = self.current_token().value
            self.consume(self.current_token().type)
            node = BinOp(node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token().type in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token().value
            self.consume(self.current_token().type)
            node = BinOp(node, op, self.factor())
        return node

    def factor(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return Number(token.value)
        elif token.type == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            return Identifier(token.value)
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.expr()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(f'Unexpected token: {token}')

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '')

    def consume(self, expected_type):
        if self.current_token().type == expected_type:
            self.pos += 1
        else:
            raise SyntaxError(f'Expected {expected_type}, got {self.current_token().type}')

    def identifier(self):
        token = self.current_token()
        if token.type == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            return Identifier(token.value)
        else:
            raise SyntaxError(f'Expected identifier, got {token.type}')

class Interpreter:
    def __init__(self):
        self.variables = {}

    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, Identifier):
            if node.name in self.variables:
                return self.variables[node.name]
            else:
                raise NameError(f'Variable {node.name} not defined')
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                return left / right
        elif isinstance(node, Assign):
            value = self.evaluate(node.expr)
            self.variables[node.identifier.name] = value
            return value
        else:
            raise ValueError(f'Unsupported node type: {type(node)}')

if __name__ == '__main__':
    code = """
    x = 10 + 5 * (3 - 2)
    y = x / 2
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print("Tokens:")
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAST:")
    for node in ast:
        print(node)

    interpreter = Interpreter()
    print("\nExecution:")
    for node in ast:
        result = interpreter.evaluate(node)
        print(f"Result: {result}")
    print("Variables:", interpreter.variables)