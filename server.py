from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
import os
import time
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
from typing import Union
import json

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

MEMORY_DIR = os.path.join(os.path.dirname(__file__), 'databases', 'memory_files')
FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), 'databases', 'feedback.txt')
PARAMS = {
    "context_size": 100,
    "model": "gpt-3.5-turbo",
    "pdf_max_pages": 10,
}

# region initialize app
cmd = f'cd {os.path.dirname(__file__)} && npm run build'
if os.system(cmd) != 0:
    print("Failed to initialize.")
    exit()

app = Flask(__name__, static_folder='build', static_url_path='/')
# CORS(app, resources={r"/process_request": {"origins": "http://localhost:3000"}})

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')
# endregion

# region Memory Management
@app.route('/memory', methods=['GET'])
def get_memory_files():
    user_id = request.args.get('user_id')
    user_dir = os.path.join(MEMORY_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    files = [fn[:-4] for fn in os.listdir(user_dir)]
    return jsonify({"files": files})

@app.route('/memory/edit', methods=['GET'])
def read_memory_file():
    user_id = request.args.get('user_id')
    file_name = request.args.get('file_name')
    if file_name is None:
        return jsonify({"error": "File name not provided."}), 400
    file_path = os.path.join(MEMORY_DIR, user_id, file_name + '.txt')
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found."}), 404
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": f"Error reading file: {e}"}), 500
    
@app.route('/memory/edit', methods=['PATCH'])
def update_memory_file():
    user_id = request.args.get('user_id')
    file_name = request.json.get('file_name')
    content = request.json.get('content')
    if file_name is None or content is None:
        return jsonify({"error": "File name or content not provided."}), 400
    file_path = os.path.join(MEMORY_DIR, user_id, file_name + '.txt')
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found."}), 404
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return jsonify({"message": "File updated."})
    except Exception as e:
        return jsonify({"error": f"Error updating file: {e}"}), 500

@app.route('/memory', methods=['POST'])
def create_memory_file():
    user_id = request.args.get('user_id')
    user_dir = os.path.join(MEMORY_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    file_name = request.json.get('file_name') + '.txt'
    file_path = os.path.join(user_dir, file_name)
    if os.path.exists(file_path):
        return jsonify({"message": "File already exists."}), 400
    open(file_path, 'w').close()
    return jsonify({"error": "File created."})

@app.route('/memory', methods=['DELETE'])
def delete_memory_file():
    user_id = request.args.get('user_id')
    user_dir = os.path.join(MEMORY_DIR, user_id)
    file_name = request.json.get('file_name') + '.txt'
    file_path = os.path.join(user_dir, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found."}), 404
    os.remove(file_path)
    return jsonify({"message": "File deleted."})

@app.route('/memory', methods=['PUT'])
def rename_memory_file():
    user_id = request.args.get('user_id')
    user_dir = os.path.join(MEMORY_DIR, user_id)
    old_file_name = request.json.get('old_file_name') + '.txt'
    new_file_name = request.json.get('new_file_name') + '.txt'
    old_file_path = os.path.join(user_dir, old_file_name)
    new_file_path = os.path.join(user_dir, new_file_name)
    if not os.path.exists(old_file_path):
        return jsonify({"error": "File not found."}), 404
    if os.path.exists(new_file_path):
        return jsonify({"error": "File already exists."}), 400
    os.rename(old_file_path, new_file_path)
    return jsonify({"message": "File renamed."})
# endregion

# region LLM API Calls
def ask_llm(system_prompt: str, user_prompt: str, params: dict = PARAMS, split: bool = True) -> Union[list, str, Exception]:
    try:
        response = client.chat.completions.create(
            model=PARAMS['model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        result = response.choices[0].message.content
        return [line.strip() for line in result.split('\n') if line.strip()] if split else result
    except Exception as e:
        return e

def tidy_points_from_llm(text: str, context: str, params: dict = PARAMS) -> Union[list, Exception]: #TODO
    system_prompt = (
        "You are an expert assistant tasked with refining and organizing knowledge. "
        "Your goal is to: 1. review the provided `Text to process` and carefully "
        "correct, if it is really needed and should not augment, diminish or distort "
        "any of the original meaning, any issues such as typo, unclear expressions "
        "due to lack of context or others, based on provided `Memory Context` where "
        "the `Text to process` will be finally added into; 2. uncommon abbreviation "
        "within `Text to process` should be changed into full name; 3. split the "
        "corrected `Text to process` into distinct, independent, concise, and meaning"
        "ful knowledge point(s) (for one point, one sentence in one line without "
        "bulletin) so that they together are semantically equivalent of the original text. "
    )
    user_prompt = (
        f"Memory context:\n\n{context}\n\n\n"
        f"Text to process:\n\n{text}\n\n\n"
        "Please return a list of distinct knowledge sentences, one sentence per line."
    )
    return ask_llm(system_prompt, user_prompt, params=params)

def summarize_material_from_llm(material: str, context: str, params: dict = PARAMS) -> Union[str, Exception]: #TODO
    system_prompt = (
        "You are an expert assistant tasked with summarizing knowledge from provided "
        "`Material to summarize`. There is no restriction on the length or emphasis of "
        "the summary. If needed, `Memory Context` is also provided for you to understand "
        "the background, but the `Context` does not necessarily have direct relevance to "
        "the `Material`, is possible to contradict the `Material`, and should not be "
        "included in the summary. The summary should also be clear itself without the "
        "context and do not use abbreviation. "
    )
    user_prompt = (
        f"Memory context:\n\n{context}\n\n\n"
        f"Material to summarize:\n\n{material}\n\n\n"
        "Please provide a summary of the material."
    )
    return ask_llm(system_prompt, user_prompt, params=params, split=False)

def query_points_from_llm(text: str, context: str, params: dict = PARAMS) -> Union[list, Exception]: #TODO
    system_prompt = (
        "You are an expert assistant tasked with retrieving relevant knowledge points "
        "from a memory database. Your goal is to: 1. given the provided `User Query`, generate a list of points "
        "that are semantically related to the query from the provided `Memory Context`, "
        "without further modification, augmentation or deletion on the original points, one sentence in one line for "
        "one point. If nothing matches the `Memory Context`, do not include your own knowledge, "
        "just return one sentence acknowledging there is no match and skip the below steps. "
        "2. generate a very concise, but comprehensive if applicable ("
        "sometimes but not always mixed views exist), summary on all the above points in "
        "a single new line. No summary if no matched points. "
        "3. Return results in step 1 and step 2. "
    )
    user_prompt = (
        f"Memory context:\n\n{context}\n\n\n"
        f"User query:\n\n{text}\n\n\n"
        "Please return a list of knowledge point(s) and their summary as required in system prompt."
    )
    return ask_llm(system_prompt, user_prompt, params=params)
# endregion

# region utility functions for process_request
def prepare_context(memoryFiles: list, user_id: str) -> str:
    context = []
    for memoryFile in memoryFiles:
        with open(os.path.join(MEMORY_DIR, user_id, memoryFile), 'r') as f:
            context.append(f"In memory file {memoryFile}:\n" + '\n'.join([tmp for line in f.readlines()[-PARAMS['context_size']:] if (tmp:= line[:-1].split('\t')[-1])]))
    return '\n\n'.join(context)

def read_pdf(file, params: dict = PARAMS) -> str:
    pdf = PyPDF2.PdfReader(file)
    text = []
    for page in pdf.pages[:params['pdf_max_pages']]:
        text.append(page.extract_text())
    return '\n\n'.join(text).strip()

def store_data(data: list, memoryFiles: list, user_id: str, source: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for memoryFile in memoryFiles:
        with open(os.path.join(MEMORY_DIR, user_id, memoryFile), 'a') as f:
            for line in data:
                f.write(f"{timestamp}\t{source.replace('\t', ' ')}\t{line.replace('\t', ' ')}\n")
            f.write('\n')
    #TODO(LATER): construct knowledge graph for each memory file
    return

def check_memory_files(user_id: str, memoryFiles: list) -> bool:
    for memoryFile in memoryFiles:
        if not os.path.exists(os.path.join(MEMORY_DIR, user_id, memoryFile)):
            return False
    return True

def query_llm(text: str, params: dict = PARAMS) -> str:
    system_prompt = "You are an expert assistant tasked with providing concise but critical information relevant to the query based on your knowledge base."
    user_prompt = f"User query:\n\n{text}"
    return ask_llm(system_prompt, user_prompt, params=params, split=False)

def query_internet(text: str, params: dict = PARAMS) -> str:
    return "Unimplemented for query_internet."
# endregion

@app.route('/process_request', methods=['POST'])
def process_request():
    # get information from request
    user_id = request.args.get('user_id')
    mode = request.form.get('mode')
    selected_tab = request.form.get('selectedTab')
    params = request.form.get('parameters')
    params = json.loads(params) if params else PARAMS

    selected_memory = request.form.get('selectedMemory')
    selected_memory_list = selected_memory.split(',')
    use_llm = "%LLM%" in selected_memory_list and (selected_memory_list.remove("%LLM%") or True)
    use_internet = "%Internet%" in selected_memory_list and (selected_memory_list.remove("%Internet%") or True)
    selected_memory = list(set(selected_memory_list))
    selected_memory = ', '.join(selected_memory_list)
    selected_memory_list = [fn + ".txt" for fn in selected_memory_list]
    if not check_memory_files(user_id, selected_memory_list):
        return jsonify({"response": "Invalid memory file."})
    
    input_data = request.form.get('input') # if file is uploaded, this is the file name
    file = request.files.get('file')
    source = input_data if selected_tab != 'type-in' else 'type-in'

    # prepare context
    context = prepare_context(selected_memory_list, user_id)

    if mode == 'Add':
        if selected_tab == 'upload':
            if not source.endswith('.txt'):
                return jsonify({"response": "Invalid file format."})
            try:
                input_data = file.read().decode('utf-8')
            except:
                return jsonify({"response": "Invalid file content."})
        if selected_tab == 'type-in' or selected_tab == 'upload':
            processed_lines = tidy_points_from_llm(input_data.strip(), context, params)
            if isinstance(processed_lines, Exception):
                return jsonify({"response": f"An error occurred in calling `tidy_points_from_llm`: {processed_lines}"})
            store_data(processed_lines, selected_memory_list, user_id, source)
            response_text = f"Stored the following points in {selected_memory}:\n\n{'\n'.join(processed_lines)}"
        elif selected_tab == 'material':
            if not source.endswith('.pdf'):
                return jsonify({"response": f"Invalid file format."})
            try:
                input_data = read_pdf(file, params)
            except:
                return jsonify({"response": "Invalid file content."})
            summary = summarize_material_from_llm(input_data.strip(), context, params)
            if isinstance(summary, Exception):
                return jsonify({"response": f"An error occurred in calling `summarize_material_from_llm`: {summary}"})
            processed_lines = tidy_points_from_llm(summary, context, params)
            if isinstance(processed_lines, Exception):
                return jsonify({"response": f"An error occurred in calling `tidy_points_from_llm`: {processed_lines}"})
            store_data(processed_lines, selected_memory_list, user_id, source)
            response_text = f"Summary of {source}:\n\n{summary}\n\nStored the following points in {selected_memory}:\n\n{'\n'.join(processed_lines)}"
        else:
            response_text = "Invalid"
    elif mode == 'Query':
        response_text = query_points_from_llm(input_data.strip(), context, params)
        if isinstance(response_text, Exception):
            return jsonify({"response": f"An error occurred in calling `query_points_from_llm`: {response_text}"})
        if len(response_text) > 1:
            response_text = f"Query results from {selected_memory}:\n\n{'\n'.join(response_text[:-1])}\n\nSummary:\n{response_text[-1]}"
        else:
            response_text = f"Query results from {selected_memory}:\n\n{response_text[0]}"
        if use_llm:
            response_text += "\n\nFrom LLM's knowledge base:\n" + query_llm(input_data.strip(), params)
        if use_internet:
            response_text += "\n\nFrom the Internet:\n" + query_internet(input_data.strip(), params)
    else:
        response_text = "Invalid"

    return jsonify({"response": response_text})

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
    app.run(port=5000, debug=True)