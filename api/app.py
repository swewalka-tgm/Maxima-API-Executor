from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import re

app = Flask(__name__)

def validate_input(input):
    if not input.strip():
        return jsonify({"error": "Maxima code cannot be empty"}), 400
    
    if input.count('(') != input.count(')'):
        return jsonify({"error": "Mismatched parentheses"}), 400
    
    if input.count('[') != input.count(']'):
        return jsonify({"error": "Mismatched brackets"}), 400
    
    if input.count('{') != input.count('}'):
        return jsonify({"error": "Mismatched braces"}), 400
    
    if input[-1] != ';':
        return jsonify({"error": "Maxima code must end with a semicolon"}), 400
    
    return None

def remove_whitespace(s):
    return re.sub(r'(\(%[io]\d+\))\s*', r'\1 ', s)

def process_output(output):

    output = output.strip()

    if '(%i2)' in output:
        output = "(%i2)" + output.split('(%i2)')[1]

    else:
        output = output.split('(%i1)')[1]


    output = remove_whitespace(output)

    return output.rsplit('\n', 1)[0]

@app.route('/execute-maxima', methods=['POST'])
def execute_maxima():
    maxima_code = request.json.get('code', '')
    
    # Step 1: Validate the input
    if validate_input(maxima_code) is not None:
        return validate_input(maxima_code)

    # Step 2 & 3: Create a temporary file and write the Maxima code to it
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(maxima_code)
            temp_file_name = temp.name
    except Exception as e:
        return jsonify({"error": "Failed to create temporary file"}), 500

    # Step 4: Execute Maxima with the temporary file as the input
    try:
        result = subprocess.run(['maxima', '-b', temp_file_name], capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Maxima execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Step 5: Clean up by deleting the temporary file
        os.remove(temp_file_name)

    return jsonify({"output": process_output(result.stdout)})

@app.route('/execute-maxima', methods=['GET'])
def execute_maxima_get():
    maxima_code = request.args.get('code', '')
    
    # Step 1: Validate the input
    if validate_input(maxima_code) is not None:
        return validate_input(maxima_code)

    # Step 2 & 3: Create a temporary file and write the Maxima code to it
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(maxima_code)
            temp_file_name = temp.name
    except Exception as e:
        return jsonify({"error": "Failed to create temporary file"}), 500

    # Step 4: Execute Maxima with the temporary file as the input
    try:
        result = subprocess.run(['maxima', '-b', temp_file_name], capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Maxima execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Step 5: Clean up by deleting the temporary file
        os.remove(temp_file_name)

    return jsonify({"output": process_output(result.stdout)})

if __name__ == '__main__':
    app.run(debug=True)
