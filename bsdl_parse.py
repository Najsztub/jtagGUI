# MN: 29/10/20
# Parse a simple BSDL file

import pprint
import json
import tatsu


if __name__ == "__main__":
    
    grammar = open('bsdl.ebnf').read()
    # tatsu.to_python_sourcecode(grammar)
    bsdl_model = tatsu.compile(grammar)

    bsdl_file = None
    with open('1k50f256.bsd') as f:
        bsdl_file = f.read()

    class BsdlSemantics:
        def map_string(self, ast):
            ast = bsdl_model.parse(''.join(ast), "port_map")
            return ast

        def grouped_port_identification(self, ast):
            ast = bsdl_model.parse(''.join(ast), "group_table")
            return ast
        
    ast = bsdl_model.parse(bsdl_file, "bsdl_description", semantics=BsdlSemantics(), parseinfo=False)

    print('# JSON')
    open('a1k.out', 'w').write(json.dumps(tatsu.util.asjson(ast), indent=2))
    print(ast)
    print()