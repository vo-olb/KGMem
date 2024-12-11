from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
import os
import time
import json
from utils import *
from setup import *

app = Flask(__name__, static_folder='build', static_url_path='/')
# CORS(app, resources={r"/process_request": {"origins": "http://localhost:3000"}})

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# region Memory Management
@app.route('/memory', methods=['GET'])
def get_memory_files():
    user_id = request.args.get('user_id')
    if not check_filename_validity(user_id):
        return jsonify({"error": "Invalid user ID."}), 400
    user_dir = os.path.join(MEMORY_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    files = [fn for fn in os.listdir(user_dir)]
    return jsonify({"files": files})

@app.route('/memory', methods=['POST'])
def create_memory_file():
    user_id = request.args.get('user_id')
    if not check_filename_validity(user_id):
        return jsonify({"error": "Invalid user ID."}), 400
    user_dir = os.path.join(MEMORY_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    file_name = request.json.get('file_name')
    if not check_filename_validity(file_name):
        return jsonify({"error": f"Invalid file name: {file_name}."}), 400
    file_path = os.path.join(user_dir, file_name)
    if os.path.exists(file_path):
        return jsonify({"error": "File already exists."}), 400
    Memory(file_path).create()
    return jsonify({"message": "File created."})

@app.route('/memory', methods=['DELETE'])
def delete_memory_file():
    user_id = request.args.get('user_id')
    if not check_filename_validity(user_id):
        return jsonify({"error": "Invalid user ID."}), 400
    user_dir = os.path.join(MEMORY_DIR, user_id)
    file_name = request.json.get('file_name')
    if not check_filename_validity(file_name):
        return jsonify({"error": "Invalid file name."}), 400
    file_path = os.path.join(user_dir, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found."}), 404
    Memory(file_path).delete()
    return jsonify({"message": "File deleted."})

@app.route('/memory', methods=['PUT'])
def rename_memory_file():
    user_id = request.args.get('user_id')
    if not check_filename_validity(user_id):
        return jsonify({"error": "Invalid user ID."}), 400
    user_dir = os.path.join(MEMORY_DIR, user_id)
    old_file_name = request.json.get('old_file_name')
    new_file_name = request.json.get('new_file_name')
    if not check_filename_validity(old_file_name) or not check_filename_validity(new_file_name):
        return jsonify({"error": "Invalid file name."}), 400
    old_file_path = os.path.join(user_dir, old_file_name)
    new_file_path = os.path.join(user_dir, new_file_name)
    if not os.path.exists(old_file_path):
        return jsonify({"error": "File not found."}), 404
    if os.path.exists(new_file_path):
        return jsonify({"error": "File already exists."}), 400
    os.rename(old_file_path, new_file_path)
    return jsonify({"message": "File renamed."})
# endregion

@app.route('/process_request', methods=['POST'])
def process_request():
    # get information from request and process
    user_id = request.args.get('user_id')
    if not check_filename_validity(user_id):
        return jsonify({"response": ["Invalid user ID."]})
    mode = request.form.get('mode')
    selected_tab = request.form.get('selectedTab')
    
    params = request.form.get('parameters')
    params = json.loads(params) if params else PARAMS
    
    tmp_process = lambda input_str: ['_'.join([sub for sub in entity.strip().split(' ') if sub]) 
                                     for entity in input_str.split(',') if entity.strip()] if input_str else []
    knowledge_type = tmp_process(request.form.get('knowledgeType'))
    entity_type = tmp_process(request.form.get('entityType'))
    selected_memory = request.form.get('selectedMemory')
    selected_memory_list = set(selected_memory.split(','))
    use_llm = "%LLM%" in selected_memory_list and (selected_memory_list.remove("%LLM%") or True)
    use_internet = "%Internet%" in selected_memory_list and (selected_memory_list.remove("%Internet%") or True)
    selected_memory_list = list(selected_memory_list)
    selected_memory = ', '.join(selected_memory_list)
    if not all(check_filename_validity(mem) for mem in selected_memory_list):
        return jsonify({"response": ["Invalid memory file."]})
    
    input_data = request.form.get('input').strip() # if file is uploaded, this is the file name
    file = request.files.get('file')
    source = input_data if selected_tab != 'type-in' else 'type-in'
    source = source.replace(' ', '_')
    if not check_filename_validity(source):
        return jsonify({"response": ["Invalid source file name."]})

    # check if memory files exist
    if not check_memory_files(user_id, selected_memory_list):
        return jsonify({"response": ["Invalid memory file."]})

    # process request
    response = []
    if mode == 'Add':
        input_data = read_input(selected_tab, input_data, file, source, params)
        if input_data is None:
            return jsonify({"response": ["Invalid input file format or content."]})
        
        try:
            summary = configure_and_summarize(input_data, selected_tab, knowledge_type, entity_type, selected_memory_list, user_id, params=params)
        except Exception as e:
            return jsonify({"response": [f"An error occurred in configuring setting or summarizing material: {e}"]})
        if summary:
            response.append(f"Summary of {source}:\n\n{summary}")
        
        try:
            store_input(input_data, selected_memory_list, user_id, source)
        except Exception as e:
            return jsonify({"response": [f"An error occurred in storing data into memory: {e}"]})
        
        response.append(f"Successfully stored into {selected_memory} as a knowledge graph!")
        return jsonify({"response": response})
        
    elif mode == 'Query':
        try:
            query_result_list = query_memory(input_data, selected_memory_list, user_id, params=params)
        except Exception as e:
            return jsonify({"response": [f"An error occurred in querying memory: {e}"]})
        for mem, query_result in zip(selected_memory_list, query_result_list):
            response.append(f"**From {mem}:**\n\n{query_result}")

        if use_llm:
            response.append("**From LLM's knowledge:**\n\n" + query_llm(input_data, params))
        if use_internet:
            response.append("**From the Internet:**\n\n" + query_internet(input_data, params))
        
        try:
            summary = summarize_material_from_llm(response, params=params)
        except Exception as e:
            return jsonify({"response": [f"An error occurred in summarizing the query results: {e}"]})
        response.append(f"**Summary of all the query results:**\n\n{summary}")
        return jsonify({"response": response})
    else:
        return jsonify({"response": ["Invalid mode."]})

@app.route('/visual', methods=['POST'])
def visual():
    user_id = request.args.get('user_id')
    if not check_filename_validity(user_id):
        return jsonify({"error": "Invalid user ID."}), 400
    memory_to_visual = request.json.get('fileName')
    if not check_memory_files(user_id, [memory_to_visual]) or not check_filename_validity(memory_to_visual):
        return jsonify({"error": "Invalid memory file."}), 400
    try:
        memory_obj = Memory(os.path.join(MEMORY_DIR, user_id, memory_to_visual))
        visualizer_path = os.path.join(VISUALIZER_DIR, user_id)
        os.makedirs(visualizer_path, exist_ok=True)
        memory_obj.visualize(visualizer_path)
    except Exception as e:
        return jsonify({"error": f"An error occurred in visualizing memory: {e}"}), 400
    return jsonify({"message": "Memory visualization prepared."})

@app.route('/visualizer/<user_id>/build/<path:filename>', methods=['GET'])
def serve_user_build(user_id, filename):
    if not check_filename_validity(user_id):
        return jsonify({"error": "Invalid user ID."}), 400
    return send_from_directory(os.path.join(VISUALIZER_DIR, user_id, 'build'), filename)

@app.route('/feedback', methods=['POST'])
def save_feedback():
    user_id = request.json.get('user_id')
    feedback = request.json.get('feedback')
    if feedback is None:
        return jsonify({"error": "Feedback not provided."}), 400
    with open(FEEDBACK_PATH, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{user_id}\t{feedback}\n")    
    return jsonify({"message": "Feedback saved."})

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        setup()
    app.run(port=5000, debug=True)