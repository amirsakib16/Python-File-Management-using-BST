from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

class FILE:
    def __init__(self, name, size, format):
        self.name = name
        self.size = size
        self.format = format
        self.left = None
        self.right = None

class FILE_SYSTEM:
    def __init__(self):
        self.root = None
    
    def fileCreate(self, name, size, format):
        initFILE = FILE(name, size, format)
        if self.root == None:
            self.root = initFILE
        else:
            self.fileADD(self.root, initFILE)

    def fileADD(self, currentNode, newNode):
        if currentNode.name < newNode.name:
            if currentNode.right == None:
                currentNode.right = newNode
            else:
                self.fileADD(currentNode.right, newNode)
        elif currentNode.name > newNode.name:
            if currentNode.left == None:
                currentNode.left = newNode
            else:
                self.fileADD(currentNode.left, newNode)

    def seeALLfiles(self, root, result):
        if root == None:
            return None
        else:
            self.seeALLfiles(root.left, result)
            result.append({"name": root.name, "size": root.size, "format": root.format})
            self.seeALLfiles(root.right, result)
        return result

    def searchFILE_name(self, root, name):
        if root == None:
            return []
        if root.name == name:
            return {"name": root.name, "size": root.size, "format": root.format}
        elif name > root.name:
            return self.searchFILE_name(root.right, name)
        elif name < root.name:
            return self.searchFILE_name(root.left, name)
        return []

    def searchFILE_format(self, root, format, result=None):
        if root is None:
            return []
        if result is None:
            result = []
        if root.format == format:
            result.append({"name": root.name, "size": root.size, "format": root.format})
        self.searchFILE_format(root.left, format, result)
        self.searchFILE_format(root.right, format, result)
        return result

    def deleteFILE(self, root, name):
        if root == None:
            return root
        elif name < root.name:
            root.left = self.deleteFILE(root.left, name)
        elif name > root.name:
            root.right = self.deleteFILE(root.right, name)
        else:
            if root.left == None and root.right == None:
                return None
            if root.left == None:
                return root.right
            if root.right == None:
                return root.left
            if root.left and root.right:
                successor = self.findMIN(root.right)
                root.name = successor.name
                root.right = self.deleteFILE(root.right, successor.name)
        return root

    def findMIN(self, node):
        current = node
        while current.left:
            current = current.left
        return current
    
    def renameFILE(self, root, previousName, newName):
        if root is None:
            return False
        if root.name == previousName:
            root.name = newName
            return True
        elif previousName < root.name:
            return self.renameFILE(root.left, previousName, newName)
        else:
            return self.renameFILE(root.right, previousName, newName)

    def ascendingSIZE(self, root):
        result = []
        files = self.seeALLfiles(root, result)

    # Convert sizes to numeric values for sorting
        for file in files:
            size_str = file["size"]
            size = self.convert_size_to_kb(size_str)
            file["numeric_size"] = size

    # Sort the files by numeric size
        files.sort(key=lambda x: x["numeric_size"])

    # Remove the numeric_size key and return
        for file in files:
            del file["numeric_size"]
        return files

    def descendingSIZE(self, root):
        result = []
        files = self.seeALLfiles(root, result)

    # Convert sizes to numeric values for sorting
        for file in files:
            size_str = file["size"]
            size = self.convert_size_to_kb(size_str)
            file["numeric_size"] = size

    # Sort the files by numeric size in descending order
        files.sort(key=lambda x: x["numeric_size"], reverse=True)

    # Remove the numeric_size key and return
        for file in files:
            del file["numeric_size"]
        return files

    def convert_size_to_kb(self, size_str):
    # Convert size string like "10MB" to numeric KB value
        unit = size_str[-2:].upper()  # Extract last 2 characters
        value = int(size_str[:-2])    # Extract numeric part
        if unit == "KB":
            return value
        elif unit == "MB":
            return value * 1024
        elif unit == "GB":
            return value * 1024 * 1024
        else:
            raise ValueError(f"Unknown size unit: {unit}")


    def descendingNAME(self, root, result):
        if root is None:
            return result
        self.descendingNAME(root.right, result)
        result.append({
            "name": root.name,
            "size": root.size,
            "format": root.format
        })
        self.descendingNAME(root.left, result)
        return result
    
    def ascendingNAME(self, root, result):
        if root is None:
            return result
        self.ascendingNAME(root.left, result)
        result.append({
            "name": root.name,
            "size": root.size,
            "format": root.format
        })
        self.ascendingNAME(root.right, result)
        return result

file_system = FILE_SYSTEM()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    file_system.fileCreate(data['name'], data['size'], data['format'])
    return jsonify({"message": "File created successfully"})

@app.route('/files', methods=['GET'])
def get_files():
    result = []
    files = file_system.seeALLfiles(file_system.root, result)
    return jsonify(files)

@app.route('/search/name', methods=['GET'])
def search_by_name():
    name = request.args.get('name')
    file = file_system.searchFILE_name(file_system.root, name)
    return jsonify(file)

@app.route('/search/format', methods=['GET'])
def search_by_format():
    format = request.args.get('format')
    result = []
    files = file_system.searchFILE_format(file_system.root, format, result)
    return jsonify(files)

@app.route('/delete', methods=['DELETE'])
def delete():
    name = request.json['name']
    file_system.root = file_system.deleteFILE(file_system.root, name)
    return jsonify({"message": "File deleted successfully"})

@app.route('/rename', methods=['POST'])
def rename():
    data = request.json
    old_name = data['oldName']
    new_name = data['newName']
    result = file_system.renameFILE(file_system.root, old_name, new_name)
    if result:
        return jsonify({"message": "File renamed successfully"})
    else:
        return jsonify({"message": "File not found"}), 404





@app.route('/sort/name/asc', methods=['GET'])
def sort_files_by_name_ascending():
    result = []
    sorted_files = file_system.ascendingNAME(file_system.root, result)
    return jsonify(sorted_files)


@app.route('/sort/name/desc', methods=['GET'])
def sort_files_by_name_descending():
    result = []
    sorted_files = file_system.descendingNAME(file_system.root, result)
    return jsonify(sorted_files)


@app.route('/sort/size/asc', methods=['GET'])
def sort_files_by_size_ascending():
    sorted_files = file_system.ascendingSIZE(file_system.root)
    return jsonify(sorted_files)

@app.route('/sort/size/desc', methods=['GET'])
def sort_files_by_size_descending():
    sorted_files = file_system.descendingSIZE(file_system.root)
    return jsonify(sorted_files)




if __name__ == '__main__':
    app.run(debug=True)
