
import re

def validate_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    # Regex to find tags like {% tag ... %}
    tag_re = re.compile(r'{%\s*(\w+)\s*.*?%}')
    
    # Tags that open a block
    block_tags = {'if', 'for', 'with', 'block', 'comment', 'autoescape', 'filter', 'spaceless'}
    # Tags that terminate a block
    end_tags = {
        'endif': 'if',
        'endfor': 'for',
        'endwith': 'with',
        'endblock': 'block',
        'endcomment': 'comment',
        'endautoescape': 'autoescape',
        'endfilter': 'filter',
        'endspaceless': 'spaceless'
    }

    for i, line in enumerate(lines):
        line_num = i + 1
        matches = tag_re.finditer(line)
        for match in matches:
            tag_name = match.group(1)
            
            if tag_name in block_tags:
                stack.append((tag_name, line_num))
                print(f"L{line_num}: Open {tag_name} -> Stack regex: {[t[0] for t in stack]}")
            elif tag_name in end_tags:
                expected_open = end_tags[tag_name]
                if not stack:
                    print(f"Error at line {line_num}: Found {tag_name} but stack is empty.")
                    return
                
                last_open, last_line = stack.pop()
                if last_open != expected_open:
                    print(f"Error at line {line_num}: Found {tag_name} but expected closing for {last_open} (opened at {last_line}).")
                    return
                print(f"L{line_num}: Close {tag_name} matches {last_open}")

    if stack:
        print(f"Error: Stack not empty at end of file. Unclosed tags: {stack}")
    else:
        print("Template valid.")

if __name__ == "__main__":
    validate_template(r"C:\Users\Acer\Documents\Projetos Python\Gestão de Clientes\gestao_clientes\templates\clientes\dashboard.html")
